[app]

# (string) Title of your application
title = Student Progress App

# (string) Package name
package.name = studentprogress

# (string) Package domain (needed for android/ios packaging)
package.domain = org.test

# (string) Application version
version = 1.0

# (string) Kivy version you use
# Kivy has an unstable API, so we have to specify this a minimum.
# The default is a recent stable version from Git.
kivy.version = 2.3.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0

# (string) The Android NDK version to use
# Make sure to use a version that works with your dependencies.
# The 25b version is known to be stable.
android.ndk = 25b

# (string) Target Android API version
# This must be the same as the target_sdk_version in build.gradle
android.api = 31

# (string) Minimum Android API version
android.minapi = 21

# (string) The branch to use for python-for-android
p4a.branch = develop

# (list) Android permissions
android.permissions = INTERNET

# (string) The build toolchain to use.
# `stable` will use the latest stable release of p4a.
# `develop` will use the development branch of p4a.
# `local` will use a local clone of p4a (must be specified in `p4a.path`).
# `default` will use the version of p4a included with buildozer.
p4a.source = default

# (list) Android architectures to build for.
android.archs = arm64-v8a,armeabi-v7a

# (list) Android services to build for
# android.services = MyService:service.py

# (string) The Java version to use
# This must be set to `17` for API 31 and newer
android.java = 17

# (string) Your application's main file
source.dir = .
main.py = main.py

# (list) Files to exclude from the APK
# exclude_dirs = .buildozer, .git, .github

# (string) Path to your icons
icon.filename = %(source.dir)s/icon.png
android.icon_background = #FFFFFF
android.icon_foreground = %(source.dir)s/icon-fg.png