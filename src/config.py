#!/usr/bin/env python3
"""
Configuration & Constants
-------------------------
Stores application constants, animation row definitions, localized strings (i18n),
path resolution utilities, and Windows registry autostart helpers.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    import winreg
except ImportError:
    winreg = None

# UI & Rendering Constants
TRANSPARENT_COLOR = "#000001"
BASE_CELL_W = 192
BASE_CELL_H = 208

# Windows 11 Fluent + Kikuri Hiroi UI Themes (Dark & Light)
THEMES: dict[str, dict[str, str]] = {
    'dark': {
        'card_bg': '#17141f',
        'border': '#433256',
        'border_alert': '#ff2a70',
        'sep': '#2e233d',
        'hover_pill': '#2f233f',
        'text_primary': '#fdf4ff',
        'text_secondary': '#c084fc',
        'accent': '#d946ef',
        'cascade_arrow': '#a855f7',
        'cpu': '#c084fc',
        'ram': '#34d399',
        'gpu': '#f472b6',
        'warn': '#fbbf24',
        'alert': '#ff2a70',
    },
    'light': {
        'card_bg': '#fbf9fd',
        'border': '#e2d9eb',
        'border_alert': '#dc2626',
        'sep': '#ece4f3',
        'hover_pill': '#f0e8f7',
        'text_primary': '#21182c',
        'text_secondary': '#8b299e',
        'accent': '#a21caf',
        'cascade_arrow': '#9333ea',
        'cpu': '#8b299e',
        'ram': '#059669',
        'gpu': '#db2777',
        'warn': '#d97706',
        'alert': '#dc2626',
    },
}

# Windows Autostart Registry Constants
REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTOSTART_APP_NAME = "KikuriHiroiDesktopPet"


def get_app_dir() -> Path:
    """Directory where application executable or script lives (for user settings/data)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent.resolve()
    return Path(__file__).resolve().parent.parent


def get_bundle_dir() -> Path:
    """Directory where PyInstaller unpacks bundled resources."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS).resolve()
    return get_app_dir()


def get_autostart_command() -> str:
    """Construct command to silently run desktop pet on Windows startup."""
    if getattr(sys, 'frozen', False):
        return f'"{sys.executable}"'
    app_root = get_app_dir()
    script_path = app_root / "desktop_pet.py"
    python_dir = Path(sys.executable).parent
    pythonw = python_dir / "pythonw.exe"
    exe = str(pythonw) if pythonw.is_file() else sys.executable
    return f'"{exe}" "{script_path}"'


def is_autostart_registered() -> bool:
    """Check if Kikuri pet is currently registered in Windows Run registry."""
    if os.name != 'nt' or winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ) as key:
            try:
                winreg.QueryValueEx(key, AUTOSTART_APP_NAME)
                return True
            except FileNotFoundError:
                return False
    except Exception:
        return False


def set_autostart_registry(enable: bool) -> bool:
    """Add or remove Kikuri pet from Windows Run registry."""
    if os.name != 'nt' or winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                cmd = get_autostart_command()
                winreg.SetValueEx(key, AUTOSTART_APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, AUTOSTART_APP_NAME)
                except OSError:
                    pass
        return True
    except Exception as e:
        print(f"Failed to update registry autostart: {e}")
        return False


# Silky smooth, relaxed and comfortable frame durations (in milliseconds for 12 frames, 0.45x original speed)
ROWS_CONFIG: dict[str, dict[str, int | list[int]]] = {
    'idle':          {'row': 0, 'frames': 12, 'durations': [533, 489, 444, 444, 489, 533, 444, 356, 444, 400, 533, 711]},
    'running-right': {'row': 1, 'frames': 12, 'durations': [220, 220, 220, 220, 220, 220, 220, 220, 220, 220, 220, 220]},
    'running-left':  {'row': 2, 'frames': 12, 'durations': [220, 220, 220, 220, 220, 220, 220, 220, 220, 220, 220, 220]},
    'waving':        {'row': 3, 'frames': 12, 'durations': [444, 400, 356, 333, 333, 356, 333, 333, 356, 400, 444, 578]},
    'jumping':       {'row': 4, 'frames': 12, 'durations': [489, 400, 311, 311, 400, 444, 400, 311, 311, 400, 444, 578]},
    'failed':        {'row': 5, 'frames': 12, 'durations': [422, 400, 378, 378, 400, 422, 422, 400, 378, 378, 400, 489]},
    'waiting':       {'row': 6, 'frames': 12, 'durations': [489, 422, 356, 356, 422, 489, 489, 422, 356, 356, 422, 622]},
    'playing':       {'row': 7, 'frames': 12, 'durations': [320, 280, 260, 280, 320, 340, 320, 280, 260, 280, 320, 340]},
}

# Multi-language dictionary (English / Chinese / Japanese)
I18N: dict[str, dict] = {
    'en': {
        'states': {
            'idle': '💤 Idle',
            'running-right': '➡️ Walk Right',
            'running-left': '⬅️ Walk Left',
            'waving': '👋 Wave',
            'jumping': '🦘 Jump',
            'failed': '💫 Dizzy / Fail',
            'waiting': '⏳ Waiting',
            'playing': '🎸 Bass Groove',
        },
        'menu': {
            'states': '🎭 Set Animation State',
            'scale': '🔍 Pet Size',
            'speed': '⏱️ Animation Speed',
            'theme': '🎨 UI Theme',
            'theme_dark': '🌙 Dark Mode',
            'theme_light': '☀️ Light Mode',
            'lang': '🌐 Language (语言 / 言語)',
            'stats': '📊 Toggle System Stats (CPU/RAM/GPU)',
            'roam': '🐾 Toggle Autonomous Roam Mode',
            'bass_playing': '🎸 Bass Playing Mode',
            'autostart': '🚀 Launch on Startup',
            'bday': '🎂 Birthday Celebration (Bebea)',
            'toast': '🍶 Drunken Sake Toast!',
            'exit': '❌ Exit Pet',
            'scale_75': '75% (Small)',
            'scale_100': '100% (Normal)',
            'scale_125': '125% (Medium)',
            'scale_150': '150% (Large)',
            'speed_slow': '🐌 Slower (0.7x)',
            'speed_normal': '🚶 Relaxed Normal (1.0x)',
            'speed_fast': '⚡ Faster (1.4x)',
        },
        'quotes': [
            "Gahaha! Work hard, rock harder! 🍶",
            "Where did I leave my Onikoro carton? 🧃",
            "Bassists are the backbone of the band! 🎸",
            "Sick Hack is ready to rock at Shinjuku FOLT! 🤘🔥",
            "Happiness spiral! Drink up and enjoy life! 🍶🌀✨",
            "Bocchi-chan! The audience isn't your enemy, enjoy the music! 🎸✨",
            "🎸 SICK HACK groove time! Let's jam! 🎶",
            "Bassists are the backbone of the band! Listen to this slap bass! 🎸✨",
            "Yeah! Riding this beat to the top! 🎵🤘",
            "Drunken bass groove in full swing! 🍶🎶",
            "Phew, that was a great jam! Time for an Onikoro sake break~ 🍶",
            "Track finished! SICK HACK is always ready for the next song! 🎸",
            "Gahaha! What a killer beat! Kanpai! 🍶✨",
        ],
        'toast_msg': "Gahaha! Kanpai! 🍶 Here's to great rock & good health!",
        'roam_on': "Roam mode ON! Let's take a peaceful walk around Shimokitazawa~ 🐾",
        'roam_off': "Staying put! 💤",
        'bass_on_playing': "🎸 Bass Playing Mode ON! SICK HACK groove time! 🤘✨",
        'bass_on_waiting': "🎸 Bass Playing Mode ready! Kikuri will jam when background music plays~ 🎶",
        'bass_off': "🎸 Bass Playing Mode OFF! Time for a break~ 🍶",
        'autostart_on': "🚀 Launch on Startup enabled! Kikuri will greet you on boot! ✨",
        'autostart_off': "Launch on Startup disabled. 💤",
        'bday_msg': "🎂 Happy Birthday, Bebea!\n✨ Wishing you a wonderful and rockin' year ahead!\n🍶 Gahaha! Cheers to another great year!",
    },
    'cn': {
        'states': {
            'idle': '💤 待机',
            'running-right': '➡️ 向右走',
            'running-left': '⬅️ 向左走',
            'waving': '👋 打招呼',
            'jumping': '🦘 开心跳跃',
            'failed': '💫 眩晕失落',
            'waiting': '⏳ 期待等待',
            'playing': '🎸 贝斯演奏',
        },
        'menu': {
            'states': '🎭 切换动作状态',
            'scale': '🔍 宠物大小',
            'speed': '⏱️ 动画播放速度',
            'theme': '🎨 UI 主题风格',
            'theme_dark': '🌙 深色模式 (Dark)',
            'theme_light': '☀️ 浅色模式 (Light)',
            'lang': '🌐 语言切换 (Language / 言語)',
            'stats': '📊 开启/关闭硬件监控 (CPU/RAM/GPU)',
            'roam': '🐾 自动漫游模式',
            'bass_playing': '🎸 贝斯演奏模式',
            'autostart': '🚀 开机自动启动',
            'bday': '🎂 贝贝亚生日祝福 (8/15)',
            'toast': '🍶 畅饮鬼杀清酒！',
            'exit': '❌ 退出桌面宠物',
            'scale_75': '75% (小型)',
            'scale_100': '100% (标准)',
            'scale_125': '125% (中型)',
            'scale_150': '150% (大型)',
            'speed_slow': '🐌 悠闲慢速 (0.7x)',
            'speed_normal': '🚶 舒适标准 (1.0x)',
            'speed_fast': '⚡ 疾速狂飙 (1.4x)',
        },
        'quotes': [
            "嘎哈哈！工作要加油，摇滚更要全力以赴！🍶",
            "诶？我的鬼杀清酒放哪儿去了？🧃",
            "贝斯手可是整个乐队的主心骨哦！🎸",
            "SICK HACK 随时准备在新宿FOLT开噪！🤘🔥",
            "幸福螺旋！只要喝了酒每天都是快快乐乐的！🍶🌀✨",
            "波奇酱！台下的观众可不是敌人，放轻松去弹吧！🎸✨",
            "🎸 SICK HACK 摇滚时刻！来感受我的超绝击弦吧！🎶",
            "贝斯手可是乐队的灵魂！听听这段律动！🎸✨",
            "这首歌太有感觉了！跟着节奏嗨起来！🎵🤘",
            "酒劲上来了，这贝斯弹得绝了！嘎哈哈！🍶🎶",
            "呼~ 这一曲弹得真痛快！喝口清酒润润喉~ 🍶",
            "曲子播完啦！SICK HACK 随时准备下一首开噪！🎸",
            "嘎哈哈！好听好听，干杯！🍶✨",
        ],
        'toast_msg': "嘎哈哈！干杯〜！🍶 祝我们天天开心、身体健康！",
        'roam_on': "自动漫游模式已开启！慢悠悠在下北泽闲逛咯~ 🐾",
        'roam_off': "停下脚步，安静待命~ 💤",
        'bass_on_playing': "🎸 贝斯演奏模式开启！检测到音乐，SICK HACK 就位！🤘✨",
        'bass_on_waiting': "🎸 贝斯演奏模式已就绪！播放背景音乐时菊里就会开始演奏哦~ 🎶",
        'bass_off': "🎸 贝斯演奏模式已关闭，休息一下喝口鬼杀~ 🍶",
        'autostart_on': "🚀 开机自启动已开启！开机菊里就会陪着你哦~ ✨",
        'autostart_off': "开机自启动已关闭。💤",
        'bday_msg': "🎂 生日快乐，贝贝亚！\n✨ 祝在新的一岁顺遂无忧、万事胜意！\n🍶 嘎哈哈！天天都要开开心心的，干杯！",
    },
    'jp': {
        'states': {
            'idle': '💤 アイドル (待機)',
            'running-right': '➡️ 右へ歩く',
            'running-left': '⬅️ 左へ歩く',
            'waving': '👋 手を振る',
            'jumping': '🦘 ジャンプ',
            'failed': '💫 へろへろ',
            'waiting': '⏳ お待ちかね',
            'playing': '🎸 ベース演奏',
        },
        'menu': {
            'states': '🎭 アクション切り替え',
            'scale': '🔍 ペットのサイズ',
            'speed': '⏱️ アニメーション速度',
            'theme': '🎨 UI テーマ設定',
            'theme_dark': '🌙 ダークモード (Dark)',
            'theme_light': '☀️ ライトモード (Light)',
            'lang': '🌐 言語設定 (Language / 语言)',
            'states_header': '🎭 アクション',
            'stats': '📊 ハードウェア監視 (CPU/RAM/GPU)',
            'roam': '🐾 自由お散歩モード',
            'bass_playing': '🎸 ベース演奏モード',
            'autostart': '🚀 スタートアップ登録 (自動起動)',
            'bday': '🎂 ベベア誕生日祝い (8/15)',
            'toast': '🍶 鬼ころしで乾杯！',
            'exit': '❌ 終了',
            'scale_75': '75% (小)',
            'scale_100': '100% (標準)',
            'scale_125': '125% (中)',
            'scale_150': '150% (大)',
            'speed_slow': '🐌 のんびり (0.7x)',
            'speed_normal': '🚶 ちょうどいい (1.0x)',
            'speed_fast': '⚡ はやい (1.4x)',
        },
        'quotes': [
            "がはは！仕事もロックも気合入れていこう！🍶",
            "あれ？私のおにころどこ置いたっけ？🧃",
            "ベースはバンドの要なんだからね！🎸",
            "SICK HACK、新宿FOLTでいつでも出撃準備OKよ！🤘🔥",
            "幸せスパイラル！お酒を飲めば毎日ハッピー！🍶🌀✨",
            "ぼっちちゃん！お客さんは敵じゃないんだから、楽しんで弾きな！🎸✨",
            "🎸 ノリノリの音楽が聞こえる！SICK HACKベース開演！🎶",
            "ベースはバンドの要！きくり姉さんの超絶スラップを聞きな！🎸✨",
            "いい曲だねぇ！リズムに合わせてガンガンいくよ！🎵🤘",
            "酒が回って最高のグルーヴだ！がはは！🍶🎶",
            "ふぅ〜いいセッションだった！演奏後の鬼ころしは最高だね！🍶",
            "曲が終わったね！いつでも次の曲かかってきなさい！🎸",
            "がはは！ナイスなビートだったよ、カンパ〜イ！🍶✨",
        ],
        'toast_msg': "がはは！カンパ〜イ！🍶 最高のロックと健康に乾杯！",
        'roam_on': "お散歩モードON！下北沢をのんびり歩くよ〜 🐾",
        'roam_off': "その場でお留守番！💤",
        'bass_on_playing': "🎸 ベース演奏モードON！音楽に合わせてベース開始！🤘✨",
        'bass_on_waiting': "🎸 ベース演奏モード待機中！音楽が流れるとベースを弾くよ〜 🎶",
        'bass_off': "🎸 ベース演奏モードOFF！ちょっと休憩～ 🍶",
        'autostart_on': "🚀 自動起動ON！起動時に菊里がお出迎えするよ！✨",
        'autostart_off': "自動起動OFFにしました。💤",
        'bday_msg': "🎉 お誕生日おめでとう、ベベア！\n✨ 素敵な一年になりますように！\n🍶 がはは！ベベアちゃんおめでとう、カンパ〜イ！",
    }
}
