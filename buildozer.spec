[app]

# 应用标题（安装后显示的名字）
title = Word2Voice 文字转语音

# 包名相关（package.name 必须只含小写字母/数字/下划线/点）
package.name = word2voice
package.domain = org.word2voice

# 源码目录与入口
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,cfg,txt,ttf

# 版本号
version = 0.1

# 运行所需依赖（会打包进 APK）
requirements = python3,kivy,edge-tts,aiohttp,certifi,cffi

# ---------- Android 配置 ----------
# 目标 / 最低 SDK 版本
android.api = 34
android.minapi = 24
android.buildtools = 34.0.0
android.accept_sdk_licenses = True

# 架构（arm64 为主，兼容 32 位老机器）
android.archs = arm64-v8a, armeabi-v7a

# 权限：联网(edge-tts 在线) + 旧版本写入媒体库
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# 后台运行时不在通知栏显示服务
android.background_service = False

# 启动闪屏 / 图标（留空用默认）
# presplash.filename = %(source.dir)s/presplash.png
# icon.filename = %(source.dir)s/icon.png

# 应用方向：竖屏
android.orientation = portrait

# 是否全屏
fullscreen = 0

# 调试构建（true 即可安装到手机）
android.debug = True
# 发布构建时改成 release 并签名（见说明）
# android.releaseart = True

[buildozer]
# 构建时是否自动联网下载 SDK/NDK
log_level = 2
warn_on_root = 1
