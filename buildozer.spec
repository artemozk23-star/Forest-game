[app]
title = Forest Game
package.name = forestgame
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,mp3,wav,ttf
version = 0.1
requirements = python3,kivy,pyjnius==1.8.0
orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
