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
# Это предотвращает ошибку "license is not accepted".
android.accept_sdk_license = True

# === РЕКОМЕНДУЕМЫЕ СТАБИЛЬНЫЕ ВЕРСИИ ===
# Использование этих версий повышает шансы на успешную сборку.
# Они соответствуют стандартным настройкам Buildozer и хорошо работают в GH Actions.

# Версия Android API (уровень API Android)
android.api = 31

# Минимальная поддерживаемая версия API
android.minapi = 21

# Версия Android NDK (набор инструментов для нативной разработки)
# NDK r25b - это стабильная версия, рекомендуемая для многих сборок.
android.ndk = 25b

# Версия NDK API (уровень API для NDK)
android.ndk_api = 21

[buildozer]
log_level = 2
warn_on_root = 1