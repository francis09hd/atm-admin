[app]
title = Sentinel Core
package.name = atmbot
package.domain = org.nosotrord.sentinel
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0

# Punto de entrada
source.main = BOT_CORE/main.py

# Requerimientos
requirements = python3,kivy,kivymd,requests,pillow,numpy,kivy_garden.mapview,pyjnius,plyer

# Orientación
orientation = portrait

# Permisos de Android
# Incluye GPS, internet, foreground service, overlay y almacenamiento.
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,FOREGROUND_SERVICE,WAKE_LOCK,SYSTEM_ALERT_WINDOW,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,RECEIVE_BOOT_COMPLETED,POST_NOTIFICATIONS

# Código Java adicional para boot receiver + actividad de arranque.
android.add_src = android_src
android.extra_manifest_xml = android_src/extra_manifest.xml

# Servicio en segundo plano (scanner/logica)
services = sentinelscan:BOT_CORE/services/sentinel_scan_service.py

# SDK/NDK
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Ndk API
android.ndk_api = 21

# No forzar wakelock
android.wakelock = False

# Log level
log_level = 2

# Bootstrap Kivy
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
