[app]
title = Табло Прогресса
package.name = studentprogress
package.domain = org.example.progress

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,csv

version = 1.0.0
# Используем стабильную версию Kivy
requirements = kivy==2.3.0

# Ориентация landscape, как в оригинале
orientation = landscape
fullscreen = 0

# === КРИТИЧЕСКИ ВАЖНАЯ НАСТРОЙКА ===
# Автоматически принимаем лицензию SDK.
android.accept_sdk_license = True

# === РЕКОМЕНДУЕМЫЕ СТАБИЛЬНЫЕ НАСТРОЙКИ ДЛЯ СБОРКИ ===
# API Level 31 (Android 12) - хороший баланс
android.api = 31
# Минимальная версия API 21 (Android 5.0)
android.minapi = 21
# Используем NDK r25b - проверенная версия
android.ndk = 25b
# API Level для NDK
android.ndk_api = 21

[buildozer]
log_level = 2
warn_on_root = 1