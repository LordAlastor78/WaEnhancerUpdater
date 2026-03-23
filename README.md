# WaEnhancer Compatibility Checker

🔧 Script para verificar la compatibilidad entre WhatsApp y el módulo Xposed [WaEnhancer](https://github.com/Dev4Mod/WaEnhancer)

## 📋 Descripción

Este programa soluciona el problema de perder funcionalidad del módulo WaEnhancer cuando WhatsApp se actualiza automáticamente. 

**¿Qué hace?**
- ✅ Detecta la versión de WhatsApp instalada en tu móvil Android
- ✅ Consulta el repositorio oficial de WaEnhancer en GitHub
- ✅ Compara y verifica compatibilidad
- ✅ **[NUEVO]** Actualiza automáticamente WaEnhancer a la última versión
- ✅ **[NUEVO]** Hace downgrade automático de WhatsApp a versión compatible
- ✅ **[NUEVO]** Solución completa automática (intenta primero actualizar WaEnhancer, luego downgrade si es necesario)
- ✅ Te pregunta qué hacer si detecta incompatibilidad
- ✅ Proporciona links y guías para procedimientos manuales

## 🎯 Requisitos Previos

### 1. Android Platform Tools (ADB)

Necesitas tener ADB instalado:

**Windows:**
1. Descarga: https://developer.android.com/tools/releases/platform-tools
2. Extrae el ZIP a una carpeta (ej: `C:\platform-tools`)
3. Añade la ruta al PATH del sistema:
   - Busca "Variables de entorno" en Windows
   - Edita la variable `Path`
   - Añade la ruta donde está `adb.exe`

**Verificar instalación:**
```cmd
adb version
```

### 2. Python 3.7 o superior

Verifica que tienes Python instalado:
```cmd
python --version
```

Si no lo tienes, descarga desde: https://www.python.org/downloads/

### 3. Habilitar Depuración USB en tu Android

1. Activa "Opciones de desarrollador" (toca 7 veces sobre "Número de compilación" en Ajustes)
2. Habilita "Depuración USB" en Opciones de desarrollador
3. Conecta el móvil por USB
4. Acepta el diálogo de autorización en el móvil

## 🚀 Instalación

1. **Clona o descarga este repositorio**
```cmd
cd ruta\donde\descargaste\VaEnhancerFIX
```

2. **Instala las dependencias de Python**
```cmd
pip install -r requirements.txt
```

### (Opcional) Descargar APKs automáticamente desde APKMirror

Si quieres que el script intente descargar APKs de WhatsApp automáticamente desde APKMirror, instala la utilidad `apkmirror-downloader`:

```cmd
pip install apkmirror-downloader
```

Una vez instalada, el script intentará usarla para bajar la versión compatible de WhatsApp automáticamente cuando elijas la opción de downgrade. Si no está instalada, el script abrirá APKMirror en el navegador y te pedirá la ruta del APK descargado manualmente.

Opcional (recomendado para downgrades automáticos desde APKMirror):
```cmd
pip install apkmirror-downloader
# ó incluirlo en `requirements.txt`
```

## 💻 Uso

1. **Conecta tu móvil Android por USB** con depuración USB habilitada

2. **Ejecuta el script**
```cmd
python waenhancer_checker.py
```

3. **El script automáticamente:**
   - Verificará que ADB esté instalado
   - Detectará tu dispositivo conectado
   - Leerá la versión de WhatsApp instalada
   - Consultará el último release de WaEnhancer en GitHub
   - Mostrará el estado de compatibilidad

4. **Si hay incompatibilidad**, verás un menú con opciones automáticas:
   - **🤖 [AUTO] Actualizar WaEnhancer** - Descarga e instala automáticamente la última versión
   - **🤖 [AUTO] Hacer downgrade de WhatsApp** - Te guía paso a paso para instalar versión compatible
   - **🤖 [AUTO] Solución completa** - Intenta primero actualizar WaEnhancer y luego downgrade de WhatsApp
   - Ver información del último release
   - Abrir página de releases en GitHub
   - Obtener links de descarga de WhatsApp compatible
   - Ver instrucciones para downgrade manual

## 📱 Ejemplo de Salida

```
WaEnhancer Compatibility Checker

[1/4] Verificando ADB... ✓
[2/4] Verificando dispositivo... ✓
[3/4] Obteniendo versión de WhatsApp... ✓
[4/4] Consultando GitHub WaEnhancer... ✓

============================================================
  WaEnhancer Compatibility Checker
============================================================

WhatsApp instalado: 2.24.1.78
WaEnhancer release: v2.1.0
Versiones compatibles: 2.24.1.78

✓ Tu WhatsApp es COMPATIBLE con WaEnhancer

============================================================
```

## 🤖 Opciones Automáticas

Cuando se detecta incompatibilidad, tienes 3 opciones automáticas:

### 1️⃣ Actualizar WaEnhancer
- **Detecta automáticamente** si tienes WhatsApp normal o WhatsApp Business
- **Descarga automáticamente** el APK debug correcto desde GitHub:
  - `app-whatsapp-debug.apk` para WhatsApp normal
  - `app-business-debug.apk` para WhatsApp Business
- La instala en tu dispositivo vía ADB (9.91 MB aprox.)
- **Requiere:** Reiniciar el dispositivo después para que Xposed cargue el módulo
- **Totalmente automático** - sin intervención manual

### 2️⃣ Downgrade de WhatsApp
- **Detecta automáticamente** la versión compatible desde WaEnhancer release notes
- **Múltiples opciones de descarga**:
  1. 🏆 **APKMirror** (Recomendado) - Abre el navegador automáticamente
  2. 📦 **APKPure** - Fuente alternativa confiable
  3. ⬇️ **Uptodown** - Otra alternativa
  4. 📁 **Ya tengo el APK** - Solo pegar ruta del archivo
  5. 🌐 **URL directa** - Descarga automática desde link del APK
- **Instalación automática vía ADB** con flags `-r -d` (permite downgrade)
- **Desinstalación segura** del WhatsApp actual (con confirmación)
- Te recuerda hacer backup y desactivar actualizaciones automáticas

### 3️⃣ Solución Completa (Recomendado)
- **Paso 1:** Intenta actualizar WaEnhancer primero
- **Paso 2:** Si aún hay incompatibilidad, hace downgrade de WhatsApp
- Es la forma más efectiva de resolver el problema

**IMPORTANTE:** Antes de cualquier operación:
- ✅ Haz backup de tus chats de WhatsApp
- ✅ Desactiva actualizaciones automáticas en Play Store después

## � Fuentes de Descarga de WhatsApp

El programa automáticamente genera links de descarga para la versión compatible desde:

### 🏆 APKMirror (Recomendado)
- Fuente más confiable y segura
- APKs verificados y firmados
- Múltiples variantes disponibles (universal, nodpi)
- **Uso:** El programa abre el link de búsqueda automáticamente

### 📦 APKPure
- Alternativa confiable
- Interfaz simple
- Versiones históricas disponibles
- **Uso:** Selecciona opción 2 en el menú de downgrade

### ⬇️ Uptodown
- Buena alternativa para versiones antiguas
- Descarga directa
- **Uso:** Selecciona opción 3 en el menú de downgrade

### 🌐 Descarga Directa desde URL
- Si tienes un link directo del APK
- El programa descarga automáticamente
- **Uso:** Selecciona opción 5 y pega la URL

## �🔧 Solución de Problemas

### "ADB no está instalado"
- Asegúrate de haber descargado Android Platform Tools
- Verifica que `adb.exe` esté en tu PATH
- Prueba ejecutar `adb version` en CMD

### "No hay dispositivo Android conectado"
- Conecta el móvil por USB
- Habilita Depuración USB en el móvil
- Acepta el diálogo de autorización
- Prueba ejecutar `adb devices` para ver dispositivos

### "No se pudo obtener versión de WhatsApp"
- Verifica que WhatsApp esté instalado
- Asegúrate de que el dispositivo esté autorizado
- Intenta ejecutar manualmente: `adb shell dumpsys package com.whatsapp`

### "Error al consultar GitHub"
- Verifica tu conexión a internet
- GitHub API tiene límite de rate (60 requests/hora sin autenticación)
- Espera unos minutos y vuelve a intentar

## 🛡️ Cómo Evitar Actualizaciones Automáticas de WhatsApp

Para prevenir que WhatsApp se actualice automáticamente:

1. **Play Store:**
   - Abre Play Store
   - Busca WhatsApp
   - Toca los 3 puntos (⋮)
   - Desmarca "Actualización automática"

2. **Configuración del sistema:**
   - Algunos launchers permiten desactivar actualizaciones por app

## 🔗 Enlaces Útiles

- **WaEnhancer GitHub:** https://github.com/Dev4Mod/WaEnhancer
- **Descargar WhatsApp APKs antiguos:**
  - https://www.apkmirror.com/apk/whatsapp-inc/whatsapp/
  - https://whatsapp.en.uptodown.com/android/versions
- **Android Platform Tools:** https://developer.android.com/tools/releases/platform-tools

## ⚠️ Advertencias

- Hacer downgrade de WhatsApp puede requerir desinstalar y reinstalar
- Siempre haz backup de tus chats antes de desinstalar WhatsApp
- Desactiva las actualizaciones automáticas para evitar el problema
- Usa solo fuentes confiables para descargar APKs (APKMirror es seguro)

## 📝 Notas

Este script es una herramienta de ayuda para usuarios de WaEnhancer que enfrentan problemas de compatibilidad tras actualizaciones de WhatsApp. No es un parche ni una modificación directa, sino un asistente para gestionar versiones y mantener la funcionalidad del módulo.

## 🤝 Contribuciones

¿Encontraste un bug o tienes una sugerencia? Siéntete libre de modificar el código según tus necesidades.

## 📄 Licencia

Libre para uso personal.

---

**Desarrollado para evitar perder WaEnhancer tras actualizaciones de WhatsApp** 🚀
