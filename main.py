# -*- coding: utf-8 -*-
"""
Word2Voice - 文字转语音 Android 应用
- 使用 edge-tts 生成神经网络中文女声
- 生成后可播放、并分享到微信 / 其他应用
"""
import os
import time
import asyncio
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout

import edge_tts

# Android 平台相关（仅在 APK 中可用，桌面测试时为 None）
try:
    from jnius import autoclass, cast
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    ContentValues = autoclass('android.content.ContentValues')
    MediaStoreAudio = autoclass('android.provider.MediaStore$Audio$Media')
    Environment = autoclass('android.os.Environment')
    IS_ANDROID = True
except Exception:
    IS_ANDROID = False

# 女声列表（中文为主 + 一个英文女声）
VOICES = [
    ("晓晓 (zh-CN-XiaoxiaoNeural)", "zh-CN-XiaoxiaoNeural"),
    ("晓伊 (zh-CN-XiaoyiNeural)", "zh-CN-XiaoyiNeural"),
    ("晓涵 (zh-CN-XiaohanNeural)", "zh-CN-XiaohanNeural"),
    ("晓梦 (zh-CN-XiaomengNeural)", "zh-CN-XiaomengNeural"),
    ("晓秋 (zh-CN-XiaoqiuNeural)", "zh-CN-XiaoqiuNeural"),
    ("晓睿 (zh-CN-XiaoruiNeural)", "zh-CN-XiaoruiNeural"),
    ("晓双 (zh-CN-XiaoshuangNeural)", "zh-CN-XiaoshuangNeural"),
    ("晓辰 (zh-CN-XiaochenNeural)", "zh-CN-XiaochenNeural"),
    ("Jenny (en-US-JennyNeural)", "en-US-JennyNeural"),
]

KV = '''
<TtsScreen>:
    orientation: 'vertical'
    padding: dp(16)
    spacing: dp(12)

    Label:
        text: '文字转语音（女声）'
        size_hint_y: None
        height: dp(40)
        font_size: '22sp'
        bold: True

    Label:
        text: '选择声音：'
        size_hint_y: None
        height: dp(24)
        font_size: '14sp'
        halign: 'left'
        text_size: self.size

    Spinner:
        id: voice_spinner
        text: ''
        values: []
        size_hint_y: None
        height: dp(48)
        font_size: '16sp'

    Label:
        text: '输入文字：'
        size_hint_y: None
        height: dp(24)
        font_size: '14sp'
        halign: 'left'
        text_size: self.size

    TextInput:
        id: text_input
        hint_text: '请输入要转换的文字...'
        multiline: True
        font_size: '16sp'

    Button:
        text: '生成语音'
        size_hint_y: None
        height: dp(52)
        font_size: '18sp'
        on_release: root.generate()

    Button:
        text: '播放语音'
        id: play_btn
        size_hint_y: None
        height: dp(52)
        font_size: '18sp'
        on_release: root.play()
        disabled: True

    Button:
        text: '分享到微信 / 其他应用'
        id: share_btn
        size_hint_y: None
        height: dp(52)
        font_size: '18sp'
        on_release: root.share()
        disabled: True

    Label:
        id: status
        text: '就绪'
        size_hint_y: None
        height: dp(28)
        font_size: '13sp'
        halign: 'left'
        text_size: self.size
'''


class TtsScreen(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.current_file = None
        # 等子控件创建好后再填充 Spinner
        Clock.schedule_once(self._populate_voices)

    def _populate_voices(self, dt):
        names = [v[0] for v in VOICES]
        self.ids.voice_spinner.values = names
        self.ids.voice_spinner.text = names[0]

    # ---- UI helpers ----
    def set_status(self, text):
        self.ids.status.text = text

    def _sync_buttons(self):
        ok = bool(self.current_file) and os.path.exists(self.current_file)
        self.ids.play_btn.disabled = not ok
        self.ids.share_btn.disabled = not ok

    # ---- 生成语音 ----
    def generate(self):
        text = self.ids.text_input.text.strip()
        if not text:
            self.set_status('请输入文字')
            return
        voice_key = None
        for name, key in VOICES:
            if name == self.ids.voice_spinner.text:
                voice_key = key
                break
        if not voice_key:
            voice_key = VOICES[0][1]

        self.set_status('生成中，请稍候...')
        self.ids.play_btn.disabled = True
        self.ids.share_btn.disabled = True

        def work():
            try:
                out_path = self._get_output_path()
                loop = asyncio.new_event_loop()
                try:
                    loop.run_until_complete(self._synthesize(text, voice_key, out_path))
                finally:
                    loop.close()
                self.current_file = out_path
                Clock.schedule_once(lambda dt: self.set_status('生成完成: ' + os.path.basename(out_path)))
                Clock.schedule_once(lambda dt: self._sync_buttons())
            except Exception as e:
                msg = '生成失败: ' + str(e)
                Clock.schedule_once(lambda dt: self.set_status(msg))

        threading.Thread(target=work, daemon=True).start()

    async def _synthesize(self, text, voice, out_path):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(out_path)

    # ---- 播放 ----
    def play(self):
        if not self.current_file or not os.path.exists(self.current_file):
            return
        sound = SoundLoader.load(self.current_file)
        if sound:
            sound.play()
            self.set_status('播放中...')
        else:
            self.set_status('无法播放该文件')

    # ---- 分享到微信 / 其他应用 ----
    def share(self):
        if not self.current_file or not os.path.exists(self.current_file):
            return
        if not IS_ANDROID:
            self.set_status('桌面环境不支持分享，请用 APK 运行')
            return
        try:
            uri = self._save_to_media_store(self.current_file)
            if uri is None:
                self.set_status('分享失败：无法写入媒体库')
                return
            self._share_uri(uri)
            self.set_status('已唤起分享，选择微信即可')
        except Exception as e:
            self.set_status('分享失败: ' + str(e))

    def _save_to_media_store(self, file_path):
        """把音频写入系统媒体库（Music/Word2Voice），返回可分享的 content:// URI"""
        activity = PythonActivity.mActivity
        resolver = activity.getContentResolver()
        base = os.path.splitext(os.path.basename(file_path))[0]

        values = ContentValues()
        values.put(MediaStoreAudio.DISPLAY_NAME, base + '.mp3')
        values.put(MediaStoreAudio.MIME_TYPE, 'audio/mpeg')
        try:
            values.put(MediaStoreAudio.RELATIVE_PATH, 'Music/Word2Voice')
        except Exception:
            pass  # 旧版本没有该字段
        try:
            values.put(MediaStoreAudio.IS_PENDING, 1)
        except Exception:
            pass

        uri = resolver.insert(MediaStoreAudio.EXTERNAL_CONTENT_URI, values)
        if uri is None:
            return None

        out = resolver.openOutputStream(uri)
        buf = bytearray(8192)
        with open(file_path, 'rb') as f:
            while True:
                n = f.readinto(buf)
                if not n:
                    break
                out.write(buf, 0, n)
        out.flush()
        out.close()

        try:
            done = ContentValues()
            done.put(MediaStoreAudio.IS_PENDING, 0)
            resolver.update(uri, done, None, None)
        except Exception:
            pass
        return uri

    def _share_uri(self, uri):
        activity = PythonActivity.mActivity
        intent = Intent(Intent.ACTION_SEND)
        intent.setType('audio/*')
        intent.putExtra(Intent.EXTRA_STREAM, cast('android.os.Parcelable', uri))
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        activity.startActivity(Intent.createChooser(intent, '分享语音到...'))

    # ---- 输出路径 ----
    def _get_output_path(self):
        if IS_ANDROID:
            # 应用外部文件目录，无需存储权限
            activity = PythonActivity.mActivity
            music_dir = activity.getExternalFilesDir(Environment.DIRECTORY_MUSIC)
            d = music_dir.getAbsolutePath()
        else:
            d = os.path.abspath('output')
            os.makedirs(d, exist_ok=True)
        fname = 'tts_' + str(int(time.time())) + '.mp3'
        return os.path.join(d, fname)


class Word2VoiceApp(App):
    def build(self):
        Builder.load_string(KV)
        return TtsScreen()


if __name__ == '__main__':
    Word2VoiceApp().run()
