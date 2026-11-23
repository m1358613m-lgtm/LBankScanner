[app]
title = LBank Scanner
package.name = lbankscanner
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.1.0,requests

android.permissions = INTERNET
# این دو خط مشکل رو حل می‌کنن:
android.accept_sdk_license = True
android.build_tools = 33.0.0

android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
