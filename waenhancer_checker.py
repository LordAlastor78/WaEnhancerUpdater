#!/usr/bin/env python3
"""
WaEnhancer Compatibility Checker
Verifica la compatibilidad entre WhatsApp instalado y el módulo WaEnhancer de Xposed
"""

import subprocess
import sys
import requests
import json
import re
import os
import tempfile
import webbrowser
from typing import Optional, Dict, List, Tuple
from packaging import version
from pathlib import Path


class Colors:
    """Colores para output en consola"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class WaEnhancerChecker:
    WHATSAPP_PACKAGE = "com.whatsapp"
    WHATSAPP_BUSINESS_PACKAGE = "com.whatsapp.w4b"
    GITHUB_REPO = "Dev4Mod/WaEnhancer"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}"
    
    def __init__(self):
        self.whatsapp_version: Optional[str] = None
        self.waenhancer_version: Optional[str] = None
        self.compatible_versions: List[str] = []
        self.release_info: Dict = {}
        self.downloads_dir = Path.home() / "Downloads" / "WaEnhancerFix"
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.is_business: bool = False  # Detecta si es WhatsApp Business
    
    def check_adb_installed(self) -> bool:
        """Verifica si ADB está instalado y disponible"""
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def check_device_connected(self) -> bool:
        """Verifica si hay un dispositivo Android conectado"""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Busca líneas que no sean "List of devices" y que tengan "device"
            lines = result.stdout.strip().split('\n')[1:]
            devices = [line for line in lines if '\tdevice' in line]
            return len(devices) > 0
        except subprocess.TimeoutExpired:
            return False
    
    def get_whatsapp_version(self) -> Optional[str]:
        """Obtiene la versión de WhatsApp instalada en el dispositivo"""
        try:
            # Intenta primero WhatsApp normal
            result = subprocess.run(
                ["adb", "shell", "dumpsys", "package", self.WHATSAPP_PACKAGE],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                match = re.search(r'versionName=([0-9.]+)', result.stdout)
                if match:
                    self.is_business = False
                    return match.group(1)
            
            # Si no encontró, intenta WhatsApp Business
            result = subprocess.run(
                ["adb", "shell", "dumpsys", "package", self.WHATSAPP_BUSINESS_PACKAGE],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                match = re.search(r'versionName=([0-9.]+)', result.stdout)
                if match:
                    self.is_business = True
                    return match.group(1)
            
            return None
        except subprocess.TimeoutExpired:
            return None
    
    def get_waenhancer_info(self) -> Dict:
        """Obtiene información del último release de WaEnhancer desde GitHub"""
        try:
            # Obtener el último release
            response = requests.get(
                f"{self.GITHUB_API_URL}/releases/latest",
                timeout=10
            )
            
            if response.status_code == 200:
                release_data = response.json()
                return {
                    'version': release_data.get('tag_name', '').lstrip('v'),
                    'name': release_data.get('name', ''),
                    'body': release_data.get('body', ''),
                    'html_url': release_data.get('html_url', ''),
                    'published_at': release_data.get('published_at', ''),
                }
            
            return {}
        except requests.RequestException as e:
            print(f"{Colors.RED}Error al consultar GitHub: {e}{Colors.RESET}")
            return {}
    
    def extract_compatible_whatsapp_versions(self, release_body: str) -> List[str]:
        """Extrae las versiones compatibles de WhatsApp del release notes"""
        compatible = []
        
        # Busca patrones comunes en release notes
        patterns = [
            r'WhatsApp\s+v?([0-9.]+)',
            r'WA\s+v?([0-9.]+)',
            r'compatible.*?([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',
            r'tested.*?([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',
            r'supports?.*?([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, release_body, re.IGNORECASE)
            compatible.extend(matches)
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique = []
        for v in compatible:
            if v not in seen:
                seen.add(v)
                unique.append(v)
        
        return unique
    
    def download_file(self, url: str, filename: str) -> Optional[Path]:
        """Descarga un archivo desde una URL"""
        try:
            print(f"\n{Colors.BLUE}Descargando: {filename}{Colors.RESET}")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            filepath = self.downloads_dir / filename
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgreso: {percent:.1f}%", end='')
            
            print(f" {Colors.GREEN}✓{Colors.RESET}")
            return filepath
        except Exception as e:
            print(f"\n{Colors.RED}Error al descargar: {e}{Colors.RESET}")
            return None
    
    def get_waenhancer_download_url(self) -> Optional[Tuple[str, str]]:
        """Obtiene la URL de descarga del APK debug de WaEnhancer"""
        try:
            response = requests.get(
                f"{self.GITHUB_API_URL}/releases/latest",
                timeout=10
            )
            if response.status_code == 200:
                assets = response.json().get('assets', [])
                
                # Determinar qué tipo de APK buscar
                if self.is_business:
                    target_name = "business-debug.apk"
                    app_type = "WhatsApp Business"
                else:
                    target_name = "whatsapp-debug.apk"
                    app_type = "WhatsApp"
                
                # Buscar el APK específico para el tipo de WhatsApp
                for asset in assets:
                    name = asset.get('name', '')
                    if target_name in name.lower():
                        print(f"{Colors.GREEN}✓ Encontrado: {name} (para {app_type}){Colors.RESET}")
                        return asset.get('browser_download_url'), name
                
                # Si no encuentra el específico, buscar cualquier debug APK
                print(f"{Colors.YELLOW}⚠ No se encontró APK específico para {app_type}{Colors.RESET}")
                print(f"{Colors.BLUE}Buscando APK debug genérico...{Colors.RESET}")
                
                for asset in assets:
                    name = asset.get('name', '')
                    if 'debug' in name.lower() and name.lower().endswith('.apk'):
                        print(f"{Colors.GREEN}✓ Encontrado: {name}{Colors.RESET}")
                        return asset.get('browser_download_url'), name
                
                # Prioridad 3: Cualquier APK
                for asset in assets:
                    name = asset.get('name', '')
                    if name.lower().endswith('.apk'):
                        print(f"{Colors.YELLOW}⚠ Encontrado APK genérico: {name}{Colors.RESET}")
                        return asset.get('browser_download_url'), name
            
            return None, None
        except Exception as e:
            print(f"{Colors.RED}Error obteniendo URL de WaEnhancer: {e}{Colors.RESET}")
            return None, None
    
    def install_waenhancer(self) -> bool:
        """Descarga e instala la última versión de WaEnhancer"""
        print(f"\n{Colors.BOLD}=== Instalando WaEnhancer ==={Colors.RESET}\n")
        
        print(f"{Colors.BLUE}Buscando APK debug en GitHub...{Colors.RESET}")
        
        # Obtener URL de descarga
        download_url, filename = self.get_waenhancer_download_url()
        if not download_url:
            print(f"\n{Colors.RED}✗ No se encontró archivo de descarga en el release{Colors.RESET}")
            print(f"Descarga manualmente desde: https://github.com/{self.GITHUB_REPO}/releases")
            return False
        
        # Descargar archivo
        filepath = self.download_file(download_url, filename)
        
        if not filepath:
            return False
        
        print(f"{Colors.BLUE}Archivo guardado en: {filepath}{Colors.RESET}")
        
        # Verificar si es APK o ZIP
        if not str(filepath).lower().endswith('.apk'):
            print(f"\n{Colors.YELLOW}⚠ El archivo descargado no es un APK{Colors.RESET}")
            print(f"Es posible que sea un módulo Xposed (.zip)")
            print(f"Debes instalarlo manualmente desde el gestor de Xposed/LSPosed")
            print(f"\nArchivo guardado en: {filepath}")
            return False
        
        # Instalar APK en el dispositivo
        print(f"\n{Colors.BLUE}Instalando APK en dispositivo vía ADB...{Colors.RESET}")
        
        try:
            result = subprocess.run(
                ["adb", "install", "-r", str(filepath)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and "Success" in result.stdout:
                print(f"{Colors.GREEN}✓ WaEnhancer instalado exitosamente{Colors.RESET}")
                print(f"\n{Colors.BOLD}Pasos siguientes:{Colors.RESET}")
                print(f"  1. {Colors.YELLOW}Reinicia el dispositivo{Colors.RESET}")
                print(f"  2. Abre el gestor de Xposed/LSPosed")
                print(f"  3. Activa el módulo WaEnhancer")
                print(f"  4. Reinicia nuevamente si es necesario")
                return True
            else:
                print(f"{Colors.RED}✗ Error instalando: {result.stdout}{result.stderr}{Colors.RESET}")
                return False
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}Timeout durante la instalación{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            return False
    
    def get_whatsapp_apk_info(self) -> Tuple[Optional[str], Optional[str]]:
        """Busca información del APK compatible en APKMirror (retorna versión y URL sugerida)"""
        if not self.compatible_versions:
            return None, None
        
        compatible_version = self.compatible_versions[0]
        # APKMirror URL base (el usuario tendrá que navegar)
        apkmirror_url = "https://www.apkmirror.com/apk/whatsapp-inc/whatsapp/"
        
        return compatible_version, apkmirror_url
    
    def get_whatsapp_download_links(self, version: str) -> Dict[str, str]:
        """Genera links de descarga para una versión específica de WhatsApp"""
        # APKMirror - búsqueda por versión
        apkmirror_search = f"https://www.apkmirror.com/apk/whatsapp-inc/whatsapp-messenger/?q={version}"
        
        # APKPure - link directo si existe
        version_code = version.replace('.', '-')
        apkpure = f"https://apkpure.com/whatsapp-messenger/com.whatsapp/versions"
        
        # Uptodown - versiones antiguas
        uptodown = "https://whatsapp.en.uptodown.com/android/versions"
        
        return {
            "apkmirror": apkmirror_search,
            "apkpure": apkpure,
            "uptodown": uptodown
        }
    
    def download_apk_from_url(self, url: str, filename: str) -> Optional[Path]:
        """Descarga un APK desde una URL directa"""
        try:
            print(f"\n{Colors.BLUE}Descargando APK desde URL...{Colors.RESET}")
            print(f"URL: {url}")
            
            response = requests.get(url, stream=True, timeout=120, allow_redirects=True)
            response.raise_for_status()
            
            # Verificar que es un APK
            content_type = response.headers.get('content-type', '').lower()
            if 'application/vnd.android.package-archive' not in content_type and not url.endswith('.apk'):
                print(f"{Colors.YELLOW}⚠ Advertencia: El archivo puede no ser un APK válido{Colors.RESET}")
            
            total_size = int(response.headers.get('content-length', 0))
            filepath = self.downloads_dir / filename
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgreso: {percent:.1f}%", end='')
            
            print(f" {Colors.GREEN}✓{Colors.RESET}")
            print(f"Archivo guardado en: {filepath}")
            return filepath
            
        except requests.RequestException as e:
            print(f"\n{Colors.RED}Error descargando: {e}{Colors.RESET}")
            return None
        except Exception as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
            return None
    
    def install_apk_via_adb(self, apk_path: str, allow_downgrade: bool = True) -> bool:
        """Instala un APK vía ADB"""
        if not os.path.exists(apk_path):
            print(f"{Colors.RED}Error: No se encontró el archivo {apk_path}{Colors.RESET}")
            return False
        
        print(f"\n{Colors.BLUE}Instalando APK vía ADB...{Colors.RESET}")
        print(f"Archivo: {apk_path}")
        
        try:
            # Flags: -r (reinstalar), -d (permitir downgrade)
            cmd = ["adb", "install"]
            if allow_downgrade:
                cmd.extend(["-r", "-d"])
            else:
                cmd.append("-r")
            cmd.append(apk_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and "Success" in result.stdout:
                print(f"{Colors.GREEN}✓ APK instalado exitosamente{Colors.RESET}")
                return True
            else:
                print(f"{Colors.RED}✗ Error instalando APK{Colors.RESET}")
                print(f"Output: {result.stdout}")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}Timeout durante la instalación{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            return False
    
    def downgrade_whatsapp(self) -> bool:
        """Guía el proceso de downgrade de WhatsApp con múltiples opciones de descarga"""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}  Downgrade de WhatsApp{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
        
        # Obtener versión compatible
        compatible_version, _ = self.get_whatsapp_apk_info()
        
        if not compatible_version:
            print(f"{Colors.YELLOW}No se pudo determinar versión compatible específica{Colors.RESET}")
            print(f"Consulta: https://github.com/{self.GITHUB_REPO}/releases\n")
            return False
        
        wa_type = "WhatsApp Business" if self.is_business else "WhatsApp"
        wa_package = self.WHATSAPP_BUSINESS_PACKAGE if self.is_business else self.WHATSAPP_PACKAGE
        
        print(f"{Colors.BLUE}Versión actual:{Colors.RESET} {wa_type} {self.whatsapp_version}")
        print(f"{Colors.GREEN}Versión compatible:{Colors.RESET} {compatible_version}")
        print(f"{Colors.RED}\n⚠ IMPORTANTE: Haz backup de tus chats antes de continuar{Colors.RESET}\n")
        
        # Generar links de descarga
        download_links = self.get_whatsapp_download_links(compatible_version)
        
        # Menú de opciones de descarga
        print(f"{Colors.BOLD}Opciones de descarga:{Colors.RESET}\n")
        print(f"  1. {Colors.GREEN}APKMirror{Colors.RESET} (Recomendado - Abrir en navegador)")
        print(f"  2. {Colors.GREEN}APKPure{Colors.RESET} (Alternativa - Abrir en navegador)")
        print(f"  3. {Colors.GREEN}Uptodown{Colors.RESET} (Abrir en navegador)")
        print(f"  4. {Colors.BLUE}Ya tengo el APK descargado{Colors.RESET} (Pegar ruta)")
        print(f"  5. {Colors.BLUE}Descargar desde URL directa{Colors.RESET} (Pegar link del APK)")
        print(f"  6. {Colors.YELLOW}Cancelar{Colors.RESET}\n")
        
        choice = input(f"{Colors.BLUE}Selecciona opción (1-6): {Colors.RESET}").strip()
        
        apk_path = None
        
        if choice == "1":
            # APKMirror
            print(f"\n{Colors.GREEN}Abriendo APKMirror...{Colors.RESET}")
            webbrowser.open(download_links["apkmirror"])
            print(f"\n{Colors.YELLOW}Instrucciones:{Colors.RESET}")
            print(f"  1. Busca la versión {compatible_version}")
            print(f"  2. Descarga el APK (variant: universal o nodpi)")
            print(f"  3. Guarda el archivo y pega la ruta aquí\n")
            apk_path = input(f"{Colors.BLUE}Ruta del APK descargado: {Colors.RESET}").strip().strip('"')
        
        elif choice == "2":
            # APKPure
            print(f"\n{Colors.GREEN}Abriendo APKPure...{Colors.RESET}")
            webbrowser.open(download_links["apkpure"])
            print(f"\n{Colors.YELLOW}Instrucciones:{Colors.RESET}")
            print(f"  1. Busca la versión {compatible_version} en la lista")
            print(f"  2. Descarga el APK")
            print(f"  3. Guarda el archivo y pega la ruta aquí\n")
            apk_path = input(f"{Colors.BLUE}Ruta del APK descargado: {Colors.RESET}").strip().strip('"')
        
        elif choice == "3":
            # Uptodown
            print(f"\n{Colors.GREEN}Abriendo Uptodown...{Colors.RESET}")
            webbrowser.open(download_links["uptodown"])
            print(f"\n{Colors.YELLOW}Instrucciones:{Colors.RESET}")
            print(f"  1. Busca la versión {compatible_version}")
            print(f"  2. Descarga el APK")
            print(f"  3. Guarda el archivo y pega la ruta aquí\n")
            apk_path = input(f"{Colors.BLUE}Ruta del APK descargado: {Colors.RESET}").strip().strip('"')
        
        elif choice == "4":
            # Ya tiene el APK
            apk_path = input(f"\n{Colors.BLUE}Ruta completa del APK: {Colors.RESET}").strip().strip('"')
        
        elif choice == "5":
            # Descargar desde URL directa
            url = input(f"\n{Colors.BLUE}Pega la URL directa del APK: {Colors.RESET}").strip()
            if url:
                filename = f"WhatsApp-{compatible_version}.apk"
                downloaded_path = self.download_apk_from_url(url, filename)
                if downloaded_path:
                    apk_path = str(downloaded_path)
                else:
                    print(f"{Colors.RED}No se pudo descargar el APK{Colors.RESET}")
                    return False
        
        elif choice == "6":
            print(f"\n{Colors.YELLOW}Operación cancelada{Colors.RESET}")
            return False
        
        else:
            print(f"\n{Colors.RED}Opción inválida{Colors.RESET}")
            return False
        
        # Verificar que tenemos un APK
        if not apk_path:
            print(f"\n{Colors.RED}No se proporcionó ruta del APK{Colors.RESET}")
            return False
        
        if not os.path.exists(apk_path):
            print(f"\n{Colors.RED}Error: No se encontró el archivo {apk_path}{Colors.RESET}")
            return False
        
        # Confirmar desinstalación
        print(f"\n{Colors.YELLOW}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}PASO 1: Desinstalar {wa_type} actual{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
        confirm = input(f"\n{Colors.RED}¿Confirmas desinstalar {wa_type}? (escribe SI en mayúsculas): {Colors.RESET}")
        
        if confirm != "SI":
            print(f"\n{Colors.YELLOW}Operación cancelada{Colors.RESET}")
            return False
        
        # Desinstalar WhatsApp
        try:
            print(f"\n{Colors.BLUE}Desinstalando {wa_type}...{Colors.RESET}")
            result = subprocess.run(
                ["adb", "uninstall", wa_package],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✓ {wa_type} desinstalado{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠ Advertencia al desinstalar: {result.stderr}{Colors.RESET}")
        
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ Error al desinstalar: {e}{Colors.RESET}")
            print(f"{Colors.BLUE}Continuando con la instalación...{Colors.RESET}")
        
        # Instalar nueva versión
        print(f"\n{Colors.YELLOW}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}PASO 2: Instalar {wa_type} {compatible_version}{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}")
        
        if self.install_apk_via_adb(apk_path, allow_downgrade=True):
            print(f"\n{Colors.GREEN}{'='*60}{Colors.RESET}")
            print(f"{Colors.GREEN}✓ Downgrade completado exitosamente{Colors.RESET}")
            print(f"{Colors.GREEN}{'='*60}{Colors.RESET}")
            print(f"\n{Colors.BOLD}Pasos siguientes:{Colors.RESET}")
            print(f"  1. {Colors.YELLOW}Restaura el backup de tus chats{Colors.RESET}")
            print(f"  2. {Colors.YELLOW}Abre Play Store → WhatsApp → ⋮ → Desmarcar 'Actualización automática'{Colors.RESET}")
            print(f"  3. {Colors.GREEN}¡Listo! Ahora tienes WhatsApp compatible con WaEnhancer{Colors.RESET}\n")
            return True
        else:
            print(f"\n{Colors.RED}No se pudo completar el downgrade{Colors.RESET}")
            return False
    
    def auto_fix(self) -> bool:
        """Intenta solución automática: primero actualizar WaEnhancer, luego downgrade WhatsApp"""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}  Solución Automática Completa{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
        
        print(f"{Colors.BLUE}Paso 1:{Colors.RESET} Actualizando WaEnhancer...\n")
        
        if self.install_waenhancer():
            print(f"\n{Colors.GREEN}✓ WaEnhancer actualizado{Colors.RESET}")
            print(f"\n{Colors.BLUE}Verificando compatibilidad...{Colors.RESET}")
            
            # Recargar versión de WhatsApp por si cambió
            self.whatsapp_version = self.get_whatsapp_version()
            is_compatible = self.compare_versions(
                self.whatsapp_version,
                self.compatible_versions
            )
            
            if is_compatible:
                print(f"{Colors.GREEN}✓ ¡Problema resuelto! WhatsApp ahora es compatible{Colors.RESET}")
                return True
        
        print(f"\n{Colors.YELLOW}WaEnhancer actualizado, pero aún hay incompatibilidad{Colors.RESET}")
        print(f"{Colors.BLUE}Paso 2:{Colors.RESET} Haciendo downgrade de WhatsApp...\n")
        
        if self.downgrade_whatsapp():
            print(f"\n{Colors.GREEN}✓ ¡Solución completa! WhatsApp compatible instalado{Colors.RESET}")
            return True
        
        print(f"\n{Colors.YELLOW}Completado con advertencias. Verifica manualmente.{Colors.RESET}")
        return False
    
    def compare_versions(self, installed: str, compatible: List[str]) -> bool:
        """Compara si la versión instalada es compatible"""
        if not compatible:
            # Si no hay info específica, asumimos que puede ser compatible
            return None
        
        try:
            installed_v = version.parse(installed)
            for compatible_v_str in compatible:
                if version.parse(compatible_v_str) == installed_v:
                    return True
            return False
        except version.InvalidVersion:
            return None
    
    def print_status(self, is_compatible: Optional[bool]):
        """Imprime el estado de compatibilidad"""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}  WaEnhancer Compatibility Checker{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
        
        wa_type = "WhatsApp Business" if self.is_business else "WhatsApp"
        print(f"{Colors.BLUE}{wa_type} instalado:{Colors.RESET} {self.whatsapp_version}")
        print(f"{Colors.BLUE}WaEnhancer release:{Colors.RESET} v{self.waenhancer_version}")
        
        if self.compatible_versions:
            print(f"{Colors.BLUE}Versiones compatibles:{Colors.RESET} {', '.join(self.compatible_versions)}")
        
        print()
        
        if is_compatible is None:
            print(f"{Colors.YELLOW}⚠ No se pudo determinar compatibilidad automáticamente{Colors.RESET}")
            print(f"  Verifica manualmente en: https://github.com/{self.GITHUB_REPO}/releases")
        elif is_compatible:
            print(f"{Colors.GREEN}✓ Tu WhatsApp es COMPATIBLE con WaEnhancer{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Tu WhatsApp NO es compatible con WaEnhancer{Colors.RESET}")
            print(f"{Colors.YELLOW}  ¡Riesgo de perder funcionalidad del módulo!{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    def show_options(self):
        """Muestra opciones al usuario cuando hay incompatibilidad"""
        print(f"{Colors.BOLD}¿Qué deseas hacer?{Colors.RESET}\n")
        print(f"  1. {Colors.GREEN}[AUTO]{Colors.RESET} Actualizar WaEnhancer (instalar última versión)")
        print(f"  2. {Colors.GREEN}[AUTO]{Colors.RESET} Hacer downgrade de WhatsApp")
        print(f"  3. {Colors.GREEN}[AUTO]{Colors.RESET} Solución completa (1+2: actualizar WaEnhancer y downgrade WhatsApp)")
        print(f"  4. Ver información del último release de WaEnhancer")
        print(f"  5. Abrir página de releases en GitHub")
        print(f"  6. Obtener link de descarga de WhatsApp compatible")
        print(f"  7. Ver instrucciones para downgrade manual")
        print(f"  8. Salir\n")
        
        try:
            choice = input(f"{Colors.BLUE}Selecciona una opción (1-8): {Colors.RESET}")
            return choice.strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            return "8"
    
    def handle_user_choice(self, choice: str, release_info: Dict):
        """Maneja la elección del usuario"""
        if choice == "1":
            # Actualizar WaEnhancer
            self.install_waenhancer()
        
        elif choice == "2":
            # Downgrade de WhatsApp
            self.downgrade_whatsapp()
        
        elif choice == "3":
            # Solución completa automática
            self.auto_fix()
        
        elif choice == "4":
            print(f"\n{Colors.BOLD}Información del release:{Colors.RESET}\n")
            print(f"Versión: {release_info.get('version', 'N/A')}")
            print(f"Nombre: {release_info.get('name', 'N/A')}")
            print(f"Publicado: {release_info.get('published_at', 'N/A')}")
            print(f"\nNotas del release:\n{release_info.get('body', 'N/A')}")
            print()
        
        elif choice == "5":
            url = release_info.get('html_url', f"https://github.com/{self.GITHUB_REPO}/releases")
            print(f"\n{Colors.GREEN}Abriendo: {url}{Colors.RESET}\n")
            webbrowser.open(url)
        
        elif choice == "6":
            if self.compatible_versions:
                print(f"\n{Colors.BOLD}Versiones compatibles de WhatsApp:{Colors.RESET}\n")
                for v in self.compatible_versions:
                    print(f"  • {v}")
                print(f"\n{Colors.YELLOW}Descarga APKs antiguos de WhatsApp desde:{Colors.RESET}")
                print(f"  - https://www.apkmirror.com/apk/whatsapp-inc/whatsapp/")
                print(f"  - https://whatsapp.en.uptodown.com/android/versions")
                print()
            else:
                print(f"\n{Colors.YELLOW}No se detectaron versiones específicas en release notes{Colors.RESET}")
                print(f"Consulta: https://github.com/{self.GITHUB_REPO}/releases\n")
        
        elif choice == "7":
            print(f"\n{Colors.BOLD}Instrucciones para hacer downgrade manual de WhatsApp:{Colors.RESET}\n")
            print(f"  1. Haz backup de tus chats en WhatsApp")
            print(f"  2. Desinstala WhatsApp actual")
            print(f"  3. Descarga el APK de la versión compatible")
            print(f"  4. Habilita instalación de fuentes desconocidas")
            print(f"  5. Instala el APK descargado")
            print(f"  6. Restaura el backup si es necesario")
            print(f"  7. Desactiva actualizaciones automáticas en Play Store")
            print(f"\n{Colors.YELLOW}NOTA: Requiere desactivar actualizaciones automáticas de WhatsApp{Colors.RESET}\n")
        
        elif choice == "8":
            print(f"{Colors.GREEN}Adiós!{Colors.RESET}\n")
            return False
        
        else:
            print(f"{Colors.RED}Opción inválida{Colors.RESET}\n")
        
        return True
    
    def run(self):
        """Ejecuta el checker principal"""
        print(f"\n{Colors.BOLD}WaEnhancer Compatibility Checker{Colors.RESET}\n")
        
        # 1. Verificar ADB
        print(f"[1/4] Verificando ADB...", end=" ")
        if not self.check_adb_installed():
            print(f"{Colors.RED}✗{Colors.RESET}")
            print(f"\n{Colors.RED}Error: ADB no está instalado o no está en PATH{Colors.RESET}")
            print(f"Descarga Android Platform Tools: https://developer.android.com/tools/releases/platform-tools")
            return 1
        print(f"{Colors.GREEN}✓{Colors.RESET}")
        
        # 2. Verificar dispositivo conectado
        print(f"[2/4] Verificando dispositivo...", end=" ")
        if not self.check_device_connected():
            print(f"{Colors.RED}✗{Colors.RESET}")
            print(f"\n{Colors.RED}Error: No hay dispositivo Android conectado{Colors.RESET}")
            print(f"Conecta tu dispositivo por USB y habilita depuración USB")
            return 1
        print(f"{Colors.GREEN}✓{Colors.RESET}")
        
        # 3. Obtener versión de WhatsApp
        print(f"[3/4] Obteniendo versión de WhatsApp...", end=" ")
        self.whatsapp_version = self.get_whatsapp_version()
        if not self.whatsapp_version:
            print(f"{Colors.RED}✗{Colors.RESET}")
            print(f"\n{Colors.RED}Error: No se pudo obtener versión de WhatsApp{Colors.RESET}")
            print(f"¿Está WhatsApp instalado en el dispositivo?")
            return 1
        print(f"{Colors.GREEN}✓{Colors.RESET}")
        
        # 4. Obtener info de WaEnhancer
        print(f"[4/4] Consultando GitHub WaEnhancer...", end=" ")
        release_info = self.get_waenhancer_info()
        if not release_info:
            print(f"{Colors.RED}✗{Colors.RESET}")
            print(f"\n{Colors.RED}Error: No se pudo consultar información de WaEnhancer{Colors.RESET}")
            return 1
        print(f"{Colors.GREEN}✓{Colors.RESET}")
        
        self.waenhancer_version = release_info.get('version', 'Unknown')
        self.compatible_versions = self.extract_compatible_whatsapp_versions(
            release_info.get('body', '')
        )
        
        # Comparar versiones
        is_compatible = self.compare_versions(
            self.whatsapp_version,
            self.compatible_versions
        )
        
        # Mostrar status
        self.print_status(is_compatible)
        
        # Si no es compatible o no se pudo determinar, mostrar opciones
        if is_compatible is False or is_compatible is None:
            while True:
                choice = self.show_options()
                if not self.handle_user_choice(choice, release_info):
                    break
        
        return 0


def main():
    """Punto de entrada principal"""
    checker = WaEnhancerChecker()
    sys.exit(checker.run())


if __name__ == "__main__":
    main()
