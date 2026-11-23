[app]
title = LBank Scanner
package.name = lbankscanner
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
# نسخه پایتون و کیوی رو دقیقا قفل کردیم تا مشکل cgi و config.pxi حل بشه
requirements = python3==3.10.8, kivy==2.3.0, requests

android.permissions = INTERNET
android.accept_sdk_license = True
android.api = 33
android.minapi = 24
android.ndk = 25b
# فقط برای گوشی‌های 64 بیتی (برای جلوگیری از خطای cgl_sdl2)
android.archs = arm64-v8a
android.allow_backup = True
