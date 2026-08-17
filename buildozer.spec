[app]

# 应用标题（安装后显示的名字）
title = Word2Voice 文字转语音

# 包名（必须只含小写字母/数字/下划线/点）
package.name = word2voice
package.domain = org.word2voice

# 源码目录与入口
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,cfg,txt,ttf,json

# 版本号（自动取 git tag 时可省略）
version = 0.1

# 运行所需依赖（会打包进 APK）
# hostpython3 与 python3 必须同版本，否则 p4a 会直接报错退出
# edge-tts 依赖 aiohttp；aiohttp 在 p4a 上需要 cffi 及若干传递依赖
requirements = hostpython3==3.12.8,python3==3.12.8,kivy==2.3.0,edge-tts==7.2.0,aiohttp,multidict,attrs,yarl,async-timeout,charset-normalizer,idna,certifi,cffi,typing-extensions

# 固定使用 NDK r25b（p4a 官方推荐稳定版本，避免 r28c 的兼容问题）
android.ndk = 25b

# ---------- Android 配置 ----------
# 目标 / 最低 SDK 版本
android.api = 34
android.minapi = 24
# 钉死构建工具版本，与 CI 预装的 34.0.0 一致
android.buildtools = 34.0.0
android.accept_sdk_licenses = True

# 架构（arm64 为主，兼容 32 位老机器）
android.archs = arm64-v8a, armeabi-v7a

# 权限：联网(edge-tts 在线) + 旧版本写入媒体库
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# 后台运行时不在通知栏显示服务
android.background_service = False

# 应用方向：竖屏
android.orientation = portrait

# 是否全屏
fullscreen = 0

# 调试构建（true 即可安装到手机）
android.debug = True

# 使用最新的 p4a（master 分支），修复对 SDK 新布局的兼容
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
