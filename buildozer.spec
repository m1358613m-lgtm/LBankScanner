[app]
title = LBank Scanner
package.name = lbankscanner
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
# این بار hostpython3 رو هم قفل کردیم تا با python3 هماهنگ باشه
requirements = python3==3.10.8, hostpython3==3.10.8, kivy==2.3.0, requests

android.permissions = INTERNET
android.accept_sdk_license = True
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
