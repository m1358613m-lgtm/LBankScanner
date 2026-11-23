[app]
title = LBank Scanner
package.name = lbankscanner
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.1.0,requests

android.permissions = INTERNET
android.archs = arm64-v8a
android.allow_backup = True
