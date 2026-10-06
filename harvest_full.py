import os
import time
import requests
import subprocess

WORKER_URL = "https://arcatdia18-ttd.stream-hub-th.workers.dev"
OUTPUT_DIR = "./vocal_samples"
os.makedirs(OUTPUT_DIR, exist_ok=True)

VOICE = "ja-JP-AoiNeural"

PITCH_LEVELS = {
    "low": "-30%",
    "mid": "0%",
    "high": "+30%"
}

# 108 粒日文歌聲全宇宙大滿貫清單 (每粒嚴格連打 10 字拖長音)
SAMPLES = {
    # 1. 核心母音與鼻音 (6)
    "a": "ああああああああああ", "i": "いいいいいいいいいい", "u": "うううううううううう", "e": "ええええええええええ", "o": "おおおおおおおおおお",
    "n": "んんんんんんんんんん",

    # 2. 五十音清音 (40)
    "ka": "かあああああああああ", "ki": "きいいいいいいいいい", "ku": "くううううううううう", "ke": "けえええええええええ", "ko": "こおおおおおおおおお",
    "sa": "さあああああああああ", "shi": "しいいいいいいいいい", "su": "すううううううううう", "se": "せえええええええええ", "so": "そおおおおおおおおお",
    "ta": "たあああああああああ", "chi": "ちいいいいいいいいい", "tsu": "つううううううううう", "te": "てえええええええええ", "to": "とおおおおおおおおお",
    "na": "なあああああああああ", "ni": "にいいいいいいいいい", "nu": "ぬううううううううう", "ne": "ねえええええええええ", "no": "のおおおおおおおおお",
    "ha": "はあああああああああ", "hi": "ひいいいいいいいいい", "fu": "ふううううううううう", "he": "へえええええええええ", "ho": "ほおおおおおおおおお",
    "ma": "まあああああああああ", "mi": "みいいいいいいいいい", "mu": "むううううううううう", "me": "めえええええええええ", "mo": "もおおおおおおおおお",
    "ya": "やあああああああああ", "yu": "ゆううううううううう", "yo": "よおおおおおおおおお",
    "ra": "らあああああああああ", "ri": "りいいいいいいいいい", "ru": "るううううううううう", "re": "れえええええええええ", "ro": "ろおおおおおおおおお",
    "wa": "わあああああああああ", "wo": "をおおおおおおおおお",

    # 3. 濁音 (20)
    "ga": "があああああああああ", "gi": "ぎいいいいいいいいい", "gu": "ぐううううううううう", "ge": "げえええええええええ", "go": "ごおおおおおおおおお",
    "za": "ざあああああああああ", "ji": "じいいいいいいいいい", "zu": "ずううううううううう", "ze": "ぜえええええええええ", "zo": "ぞおおおおおおおおお",
    "da": "だあああああああああ", "di": "ぢいいいいいいいいい", "du": "づううううううううう", "de": "でえええええええええ", "do": "どおおおおおおおおお",
    "ba": "ばあああああああああ", "bi": "びいいいいいいいいい", "bu": "ぶううううううううう", "be": "べえええええええええ", "bo": "ぼおおおおおおおおお",

    # 4. 半濁音 (5)
    "pa": "ぱあああああああああ", "pi": "ぴいいいいいいいいい", "pu": "ぷううううううううう", "pe": "ぺえええええええええ", "po": "ぽおおおおおおおおお",

    # 5. 全套拗音 (33)
    "kya": "きゃああああああああ", "kyu": "きゅうううううううう", "kyo": "きょおおおおおおおお",
    "sha": "しゃああああああああ", "shu": "しゅうううううううう", "sho": "しょおおおおおおおお",
    "cha": "ちゃああああああああ", "chu": "ちゅうううううううう", "cho": "ちょおおおおおおおお",
    "nya": "にゃああああああああ", "nyu": "にゅうううううううう", "nyo": "にょおおおおおおおお",
    "hya": "ひゃああああああああ", "hyu": "ひゅうううううううう", "hyo": "ひょおおおおおおおお",
    "mya": "みゃああああああああ", "myu": "みゅうううううううう", "myo": "みょおおおおおおおお",
    "rya": "りゃああああああああ", "ryu": "りゅうううううううう", "ryo": "りょおおおおおおおお",
    "gya": "ぎゃああああああああ", "gyu": "ぎゅうううううううう", "gyo": "ぎょおおおおおおおお",
    "ja": "じゃああああああああ", "ju": "じゅうううううううう", "jo": "じょおおおおおおおお",
    "bya": "びゃああああああああ", "byu": "びゅうううううううう", "byo": "びょおおおおおおおお",
    "pya": "ぴゃああああああああ", "pyu": "ぴゅうううううううう", "pyo": "ぴょおおおおおおおお",

    # 6. 外來語常用音 (4)
    "fa": "ふぁああああああああ", "fi": "ふぃいいいいいいいい", "fe": "ふぇええええええええ", "fo": "ふぉおおおおおおおお"
}

total = len(SAMPLES) * len(PITCH_LEVELS)
idx = 0

print(f"🚀 開始收割日文全宇宙 108 字根（總計 {total} 粒音）...")

for k, text in SAMPLES.items():
    for p_name, p_val in PITCH_LEVELS.items():
        idx += 1
        wav_name = f"{k}_{p_name}.wav"
        save_path = os.path.join(OUTPUT_DIR, wav_name)
        raw_mp3 = f"temp_{wav_name}.mp3"

        # 如果已經存在就跳過，斷線都唔驚
        if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
            continue

        print(f"[{idx}/{total}] 處理中: {wav_name} ({text[:2]}..)...", end="", flush=True)
        try:
            r = requests.post(WORKER_URL, json={
                "text": text,
                "voice": VOICE,
                "pitch": p_val,
                "rate": "0%"
            }, timeout=25)

            if r.status_code == 200:
                with open(raw_mp3, "wb") as f:
                    f.write(r.content)

                # 調用系統 FFmpeg 剃空氣仔與截取 0.8 秒
                filter_chain = "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-40dB,atrim=end=0.8,afade=t=in:ss=0:d=0.01,afade=t=out:st=0.79:d=0.01"
                cmd = [
                    "ffmpeg", "-y", "-i", raw_mp3,
                    "-af", filter_chain,
                    save_path
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                if os.path.exists(raw_mp3):
                    os.remove(raw_mp3)
                print(" -> ✂️ 空氣剃淨，入庫！✅")
            else:
                print(f" -> ❌ 失敗: {r.status_code}")
        except Exception as e:
            print(f" -> ❌ 出錯: {e}")

        time.sleep(0.35)

print("\n🎉 大滿貫 324 粒音訊全部收割完畢！")
