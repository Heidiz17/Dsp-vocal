import os
import time
import requests
import subprocess

WORKER_URL = "https://arcatdia18-ttd.stream-hub-th.workers.dev"
# 獨立男聲資料夾，絕不影響舊庫
OUTPUT_DIR = "./keita_vocals"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 換入熱血男聲：圭太
VOICE = "ja-JP-KeitaNeural"

PITCH_LEVELS = {
    "low": "-30%",
    "mid": "0%",
    "high": "+30%"
}

# 108 粒日文歌聲全宇宙大滿貫清單 (黃金比例：2 粒字頭 + 5 粒母音 = 7 粒波)
SAMPLES = {
    # 1. 核心母音與鼻音 (純母音連打 7 粒)
    "a": "あああああああ", "i": "いいいいいいい", "u": "ううううううう", "e": "えええええええ", "o": "おおおおおおお",
    "n": "んんんんんんん",

    # 2. 五十音清音 (2 字頭 + 5 母音)
    "ka": "かかあああああ", "ki": "ききいいいいい", "ku": "くくううううう", "ke": "けけえええええ", "ko": "ここおおおおお",
    "sa": "ささあああああ", "shi": "ししいいいいい", "su": "すすううううう", "se": "せせえええええ", "so": "そそおおおおお",
    "ta": "たたあああああ", "chi": "ちちいいいいい", "tsu": "つつううううう", "te": "ててえええええ", "to": "ととおおおおお",
    "na": "ななあああああ", "ni": "ににいいいいい", "nu": "ぬぬううううう", "ne": "ねねえええええ", "no": "ののおおおおお",
    "ha": "ははあああああ", "hi": "ひひいいいいい", "fu": "ふふううううう", "he": "へへえええええ", "ho": "ほほおおおおお",
    "ma": "ままあああああ", "mi": "みみいいいいい", "mu": "むむううううう", "me": "めめえええええ", "mo": "ももおおおおお",
    "ya": "ややあああああ", "yu": "ゆゆううううう", "yo": "よよおおおおお",
    "ra": "ららあああああ", "ri": "りりいいいいい", "ru": "るるううううう", "re": "れれえええええ", "ro": "ろろおおおおお",
    "wa": "わわあああああ", "wo": "おおおおおおお",

    # 3. 濁音 (2 字頭 + 5 母音)
    "ga": "ががあああああ", "gi": "ぎぎいいいいい", "gu": "ぐぐううううう", "ge": "げげえええええ", "go": "ごごおおおおお",
    "za": "ざざあああああ", "ji": "じじいいいいい", "zu": "ずずううううう", "ze": "ぜぜえええええ", "zo": "ぞぞおおおおお",
    "da": "だだあああああ", "di": "ぢぢいいいいい", "du": "づづううううう", "de": "ででえええええ", "do": "どどおおおおお",
    "ba": "ばばあああああ", "bi": "びびいいいいい", "bu": "ぶぶううううう", "be": "べべえええええ", "bo": "ぼぼおおおおお",

    # 4. 半濁音 (2 字頭 + 5 母音)
    "pa": "ぱぱあああああ", "pi": "ぴぴいいいいい", "pu": "ぷぷううううう", "pe": "ぺぺえええええ", "po": "ぽぽおおおおお",

    # 5. 全套拗音 (2 字頭 + 5 母音)
    "kya": "きゃきゃあああああ", "kyu": "きゅきゅううううう", "kyo": "きょきょおおおおお",
    "sha": "しゃしゃあああああ", "shu": "しゅしゅううううう", "sho": "しょしょおおおおお",
    "cha": "ちゃちゃあああああ", "chu": "ちゅちゅううううう", "cho": "ちょちょおおおおお",
    "nya": "にゃにゃあああああ", "nyu": "にゅにゅううううう", "nyo": "にょにょおおおおお",
    "hya": "ひゃひゃあああああ", "hyu": "ひゅひゅううううう", "hyo": "ひょひょおおおおお",
    "mya": "みゃみゃあああああ", "myu": "みゅみゅううううう", "myo": "みょみょおおおおお",
    "rya": "りゃりゃあああああ", "ryu": "りゅりゅううううう", "ryo": "りょりょおおおおお",
    "gya": "ぎゃぎゃあああああ", "gyu": "ぎゅぎゅううううう", "gyo": "ぎょぎょおおおおお",
    "ja": "じゃじゃあああああ", "ju": "じゅじゅううううう", "jo": "じょじょおおおおお",
    "bya": "びゃびゃあああああ", "byu": "びゅびゅううううう", "byo": "びょびょおおおおお",
    "pya": "ぴゃぴゃあああああ", "pyu": "ぴゅぴゅううううう", "pyo": "ぴょぴょおおおおお",

    # 6. 外來語常用音
    "fa": "ふぁふぁあああああ", "fi": "ふぃふぃいいいいい", "fe": "ふぇふぇえええええ", "fo": "ふぉふぉおおおおお"
}

total = len(SAMPLES) * len(PITCH_LEVELS)
idx = 0

print(f"🚀 開始收割圭太 (Keita) 男聲【2字頭+5母音】黃金比例（總計 {total} 粒音）...")

for k, text in SAMPLES.items():
    for p_name, p_val in PITCH_LEVELS.items():
        idx += 1
        wav_name = f"{k}_{p_name}.wav"
        save_path = os.path.join(OUTPUT_DIR, wav_name)
        raw_mp3 = f"temp_{wav_name}.mp3"

        if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
            continue

        print(f"[{idx}/{total}] 處理中: {wav_name} ({text[:3]}..)...", end="", flush=True)
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

                # 由頭保留完整 Attack，剃淨開頭靜音，保留 1.0 秒充沛長音
                filter_chain = "silenceremove=start_periods=1:start_duration=0.01:start_threshold=-45dB,atrim=end=1.0,afade=t=in:ss=0:d=0.005,afade=t=out:st=0.98:d=0.02"
                cmd = [
                    "ffmpeg", "-y", "-i", raw_mp3,
                    "-af", filter_chain,
                    save_path
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                if os.path.exists(raw_mp3):
                    os.remove(raw_mp3)
                print(" -> ✂️ 2字頭黃金咬字入庫！✅")
            else:
                print(f" -> ❌ 失敗: {r.status_code}")
        except Exception as e:
            print(f" -> ❌ 出錯: {e}")

        time.sleep(0.35)

print("\n🎉 圭太 324 粒【2字頭+5母音】黃金比例音庫全部收割完畢！")
