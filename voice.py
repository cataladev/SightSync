import pyautogui
import speech_recognition as sr
import os
import fnmatch
import platform
import getpass
import subprocess
import difflib
import time

# Global voice status & shutdown flag
_voice_status = "Waiting"
_should_exit = False

def set_voice_status(status):
    global _voice_status
    _voice_status = status

def get_voice_status():
    return _voice_status

def should_exit_app():
    return _should_exit

# Voice state flags
is_active = False
is_paused = False

def normalize_command(command):
    command = command.lower().strip()
    command = command.replace("sink", "sync")
    command = command.replace("sing", "sync")
    command = command.replace("synk", "sync")
    return command

def open_app(app_name):
    if platform.system() != "Windows":
        set_voice_status("Open app unsupported on non-Windows.")
        return

    app_name = app_name.lower().strip()
    user = getpass.getuser()

    start_menu_paths = [
        rf"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        rf"C:\Users\{user}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
    ]
    alias_path = rf"C:\Users\{user}\AppData\Local\Microsoft\WindowsApps"

    candidates = {}

    for base in start_menu_paths:
        for root, dirs, files in os.walk(base):
            for file in files:
                if file.lower().endswith(".lnk"):
                    name = os.path.splitext(file)[0].lower()
                    candidates[name] = os.path.join(root, file)

    if os.path.isdir(alias_path):
        for file in os.listdir(alias_path):
            if file.lower().endswith(".exe"):
                name = os.path.splitext(file)[0].lower()
                candidates[name] = os.path.join(alias_path, file)

    best_match = difflib.get_close_matches(app_name, candidates.keys(), n=1, cutoff=0.4)
    if best_match:
        match = best_match[0]
        set_voice_status(f"Opening: {match}")
        os.startfile(candidates[match])
    else:
        set_voice_status(f"No match found for: {app_name}")
        print(f"[!] No match found for: {app_name}")

def execute_command(command):
    global is_active, is_paused, _should_exit

    command = normalize_command(command)

    if command == "sync on":
        is_active = True
        is_paused = False
        set_voice_status("✅ Sync ON")
        return
    elif command == "sync off":
        set_voice_status("🛑 Sync OFF - Shutting down")
        _should_exit = True
        return
    elif command == "sync pause":
        if is_active:
            is_paused = True
            set_voice_status("⏸️ Paused")
        return
    elif command == "sync resume":
        if is_active:
            is_paused = False
            set_voice_status("▶️ Resumed")
        return

    if not is_active:
        set_voice_status("⚠️ Ignored - Sync OFF")
        return
    if is_paused:
        set_voice_status("⏸️ Ignored - Paused")
        return

    if command.startswith("open "):
        app_to_open = command[5:].strip()
        open_app(app_to_open)
        return

    match command:
        case "click":
            pyautogui.click()
        case "double click":
            pyautogui.doubleClick()
        case "right click":
            pyautogui.rightClick()
        case "hold":
            pyautogui.mouseDown()
        case "release":
            pyautogui.mouseUp()
        case "scroll up":
            pyautogui.scroll(200)
        case "scroll down":
            pyautogui.scroll(-200)
        case "refresh":
            pyautogui.hotkey("ctrl", "r")
        case "tabs":
            pyautogui.hotkey("ctrl", "tab")
        case "kill":
            pyautogui.hotkey("alt", "f4")
        case "fullscreen":
            pyautogui.press("f11")
        case "screenshot":
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            set_voice_status("📸 Screenshot saved")
        case "undo":
            pyautogui.hotkey("ctrl", "z")
        case "redo":
            pyautogui.hotkey("ctrl", "y")
        case "copy":
            pyautogui.hotkey("ctrl", "c")
        case "paste":
            pyautogui.hotkey("ctrl", "v")
        case "cut":
            pyautogui.hotkey("ctrl", "x")
        case "select all":
            pyautogui.hotkey("ctrl", "a")
        case "find":
            pyautogui.hotkey("ctrl", "f")
        case "save":
            pyautogui.hotkey("ctrl", "s")
        case "enter":
            pyautogui.press("enter")
        case "escape":
            pyautogui.press("esc")
        case "space":
            pyautogui.press("space")
        case "tab":
            pyautogui.press("tab")
        case "backspace":
            pyautogui.press("backspace")
        case "delete":
            pyautogui.press("delete")
        case "erase line":
            pyautogui.hotkey("ctrl", "backspace")
        case "maximize":
            pyautogui.hotkey("win", "up")
        case "minimize":
            pyautogui.hotkey("win", "down")
        case "volume up":
            pyautogui.press("volumeup")
        case "volume down":
            pyautogui.press("volumedown")
        case "mute":
            pyautogui.press("volumemute")
        case "zoom in":
            pyautogui.hotkey("ctrl", "+")
        case "zoom out":
            pyautogui.hotkey("ctrl", "-")
        case _ if command.startswith("type "):
            spoken_to_symbol = {
                "dot": ".", "comma": ",", "colon": ":", "semicolon": ";",
                "dash": "-", "hyphen": "-", "underscore": "_",
                "slash": "/", "backslash": "\\", "exclamation mark": "!",
                "question mark": "?", "at": "@", "hash": "#", "hashtag": "#",
                "dollar": "$", "percent": "%", "caret": "^", "ampersand": "&",
                "star": "*", "asterisk": "*", "plus": "+", "equals": "=",
                "less than": "<", "greater than": ">", "open parenthesis": "(",
                "close parenthesis": ")", "open bracket": "[", "close bracket": "]",
                "open brace": "{", "close brace": "}", "quote": "\"", "double quote": "\"",
                "single quote": "'", "space": " "
            }
            text = command[5:]
            words = text.split()
            output = ""
            i = 0
            while i < len(words):
                if i + 1 < len(words):
                    pair = f"{words[i]} {words[i+1]}"
                    if pair in spoken_to_symbol:
                        output += spoken_to_symbol[pair]
                        i += 2
                        continue
                output += spoken_to_symbol.get(words[i], words[i])
                output += " "
                i += 1
            pyautogui.write(output.strip())
            set_voice_status(f"Typed: {text}")
        case _:
            set_voice_status(f"Unknown command: {command}")
            print(f"[!] Unknown command: '{command}'")

def listen_and_execute():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while not _should_exit:
        try:
            set_voice_status("Listening...")
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            command = recognizer.recognize_google(audio)
            print(f"🗣️ Heard: {command}")
            set_voice_status(f"Heard: {command}")
            execute_command(command)
        except sr.UnknownValueError:
            print("[!] Could not understand.")
            set_voice_status("Didn't catch that.")
        except sr.RequestError as e:
            print(f"[!] Error with recognition: {e}")
            set_voice_status("Recognition error.")
        time.sleep(1)
