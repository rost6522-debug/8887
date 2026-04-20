#!/usr/bin/env python3
"""
speak.py v2 - озвучивает текст
Провайдеры: openai | google | windows
Настройка: ~/.claude/skills/voice-output/voice.config
"""
import sys, os, tempfile, json

# ── Читаем конфиг ──────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "voice.config")

DEFAULT_CONFIG = {
    "provider": "openai",   # openai | google | windows
    "voice": "nova",        # openai: alloy echo fable onyx nova shimmer
    "speed": 1.1,           # 0.25 - 4.0
    "max_words": 300        # обрезать длинные ответы
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            cfg = json.load(f)
        return {**DEFAULT_CONFIG, **cfg}
    return DEFAULT_CONFIG

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

# ── Провайдеры ─────────────────────────────────────────────────
def speak_openai(text, cfg):
    from openai import OpenAI
    import sounddevice as sd
    import soundfile as sf

    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        print("⚠️  OPENAI_API_KEY не задан")
        return

    client = OpenAI(api_key=key)
    resp = client.audio.speech.create(
        model="tts-1",
        voice=cfg["voice"],
        input=text,
        speed=cfg["speed"]
    )
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp = f.name
    resp.write_to_file(tmp)
    data, sr = sf.read(tmp)
    sd.play(data, sr)
    sd.wait()
    os.unlink(tmp)

def speak_google(text, cfg):
    from google.cloud import texttospeech
    import sounddevice as sd
    import soundfile as sf

    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ru-RU",
        name="ru-RU-Wavenet-D",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=cfg["speed"]
    )
    resp = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(resp.audio_content)
        tmp = f.name
    data, sr = sf.read(tmp)
    sd.play(data, sr)
    sd.wait()
    os.unlink(tmp)

def speak_windows(text, cfg):
    import subprocess
    # Встроенный Windows TTS — бесплатно, роботизированный
    ps = f'Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate={int(cfg["speed"]*3-3)}; $s.Speak("{text.replace(chr(34), chr(39))}")'
    subprocess.run(["powershell", "-WindowStyle", "Hidden", "-Command", ps])

# ── Главная функция ────────────────────────────────────────────
def speak(text):
    cfg = load_config()

    # Обрезаем длинный текст
    words = text.split()
    if len(words) > cfg["max_words"]:
        text = " ".join(words[:cfg["max_words"]]) + "..."

    provider = cfg.get("provider", "openai")
    print(f"🔊 [{provider}]", end="", flush=True)

    try:
        if provider == "openai":
            speak_openai(text, cfg)
        elif provider == "google":
            speak_google(text, cfg)
        elif provider == "windows":
            speak_windows(text, cfg)
        else:
            print(f"⚠️  Неизвестный провайдер: {provider}")
        print(" ✓")
    except Exception as e:
        print(f" ⚠️  Ошибка: {e}")

# ── Команды настройки ──────────────────────────────────────────
def handle_config_command(args):
    cfg = load_config()

    if len(args) == 0 or args[0] == "show":
        print(f"\n📋 Текущий конфиг:")
        print(f"   provider : {cfg['provider']}  (openai | google | windows)")
        print(f"   voice    : {cfg['voice']}     (openai: alloy echo fable onyx nova shimmer)")
        print(f"   speed    : {cfg['speed']}")
        print(f"   max_words: {cfg['max_words']}")
        print(f"\n💡 Изменить: python speak.py config provider google")
        return

    if len(args) >= 2:
        key, val = args[0], args[1]
        if key in cfg:
            # Конвертируем тип
            if key in ["speed"]:
                val = float(val)
            elif key in ["max_words"]:
                val = int(val)
            cfg[key] = val
            save_config(cfg)
            print(f"✅ {key} = {val}")
        else:
            print(f"⚠️  Неизвестный параметр: {key}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python speak.py 'текст'          - озвучить")
        print("  python speak.py config           - показать настройки")
        print("  python speak.py config provider openai   - выбрать провайдер")
        print("  python speak.py config voice nova        - выбрать голос")
        print("  python speak.py config speed 1.2         - скорость")
        sys.exit(0)

    if sys.argv[1] == "config":
        handle_config_command(sys.argv[2:])
    else:
        text = " ".join(sys.argv[1:])
        speak(text)
