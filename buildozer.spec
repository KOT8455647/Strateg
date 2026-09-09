[app]

title = Polniy Strateg
package.name = polniystrateg
package.domain = org.strateg

source.dir = .
source.include_exts = py, txt, json

version = 8.0

requirements = python3,kivy==2.3.0,requests,urllib3,certifi,charset_normalizer,idna

orientation = portrait
fullscreen = 0

android.archs = arm64-v8a

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.use_cleartext_traffic = True

android.api = 33
android.minapi = 21
android.ndk = 25b
android.python_version = 3.10.14

android.accept_sdk_license = True
android.skip_update = False
android.copy_libs = 0
android.gradle_dependencies =

[buildozer]

log_level = 2
warn_on_root = 1
