import os
import sys
from pynput import keyboard
from datetime import datetime
import time
import firebase_admin
from firebase_admin import credentials, db

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

firebase_key_path = resource_path("firebase_key.json")

# 🔐 Firebase RTDB Initialization
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-default-rtdb.firebaseio.com/'  # Replace with your actual URL
})

ref = db.reference("logs")

current_word = ""
last_word_time = None

def log_word_to_rtdb(word, typing_time):
    if not word.strip():
        return
    try:
        ref.push({
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "word": word,
            "typing_time": round(typing_time, 2)
        })
        print(f"📝 Logged: {word} - {typing_time:.2f}s")
    except Exception as e:
        print("❌ Firebase error:", e)

def on_press(key):
    global current_word, last_word_time
    try:
        if key.char.isalnum() or key.char in ("-", "_"):
            current_word += key.char
    except AttributeError:
        if key == keyboard.Key.space or key == keyboard.Key.enter:
            if current_word.strip():
                now = time.time()
                time_diff = now - last_word_time if last_word_time else 0.0
                log_word_to_rtdb(current_word.strip(), time_diff)
                last_word_time = now
            current_word = ""

def on_release(key):
    if key == keyboard.Key.esc:
        print("🛑 Logging stopped.")
        return False

print("⏺️ Typing logger started... Press ESC to stop.")
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
