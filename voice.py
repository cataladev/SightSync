import pyautogui
import speech_recognition as sr
import os
import fnmatch
import platform
import getpass
import subprocess
import difflib
import time
import threading
import numpy as np
import noisereduce as nr
from vision import NoseTracker
import pygetwindow as gw

pyautogui.FAILSAFE = False

eye_tracker = NoseTracker()
tracker_started = False

_voice_status = "Waiting"
_should_exit = False

def set_voice_status(status):
    global _voice_status
    _voice_status = status

def get_voice_status():
    return _voice_status

def should_exit_app():
    return _should_exit

is_active = False
is_paused = False

def normalize_command(command):
    command = command.lower().strip()
    command = command.replace("sink", "sync")
    command = command.replace("sing", "sync")
    command = command.replace("synk", "sync")
    command = command.replace("sides", "sync")
    command = command.replace("sight", "sync")
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

def command_matches(command, keywords):
    return any(k in command or command == k for k in keywords)

def execute_command(command):
    global is_active, is_paused, _should_exit, tracker_started

    command = normalize_command(command)

    if "sync on" in command:
        if not is_active or is_paused:
            is_active = True
            is_paused = False
            set_voice_status("Sync ON")
            current_window = gw.getActiveWindow()
            if current_window:
                current_window.minimize()
            if not tracker_started:
                threading.Thread(target=eye_tracker.start, daemon=True).start()
                tracker_started = True
        return

    elif "sync off" in command or "sync stop" in command:
        set_voice_status("Sync OFF - Shutting down")
        if tracker_started:
            eye_tracker.stop()
        _should_exit = True
        return

    elif "sync pause" in command:
        if is_active and not is_paused:
            is_paused = True
            if tracker_started:
                eye_tracker.pause()
            set_voice_status("Tracking Paused")
        return

    elif "sync resume" in command:
        if is_active and is_paused:
            is_paused = False
            if tracker_started:
                eye_tracker.resume()
            set_voice_status("Tracking Resumed")
        return

    if not is_active:
        set_voice_status("Ignored - Sync OFF")
        return
    if is_paused:
        set_voice_status("Ignored - Paused")
        return

    words = command.split()
    if "open" in words:
        index = words.index("open")
        app_to_open = " ".join(words[index + 1:])
        if app_to_open:
            open_app(app_to_open)
            return


    if "maximize " in command or "minimize " in command or "close " in command:
        action, _, target_title = command.partition(" ")
        matched_window = None

        windows = gw.getWindowsWithTitle(target_title)
        if not windows:
            titles = [win.title for win in gw.getAllWindows() if win.title]
            best_match = difflib.get_close_matches(target_title, titles, n=1, cutoff=0.4)
            if best_match:
                matched_window = next((win for win in gw.getAllWindows() if win.title == best_match[0]), None)
        else:
            matched_window = windows[0]

        if matched_window:
            if action == "maximize":
                matched_window.maximize()
                set_voice_status(f"Maximized: {matched_window.title}")
            elif action == "minimize":
                matched_window.minimize()
                set_voice_status(f"Minimized: {matched_window.title}")
            elif action == "close":
                matched_window.close()
                set_voice_status(f"Closed: {matched_window.title}")
        else:
            set_voice_status(f"Window not found: {target_title}")
        return

    if command_matches(command, ["help"]):
        set_voice_status("Opening help window")
        subprocess.Popen(["python", "help_window.py"])

        def position_help_window():
            time.sleep(1.5)
            for win in gw.getAllWindows():
                if "help" in win.title.lower():
                    screen_width, screen_height = pyautogui.size()
                    win.moveTo(screen_width // 2, 0)
                    win.resizeTo(screen_width // 2, screen_height)
                    break

        threading.Thread(target=position_help_window, daemon=True).start()
        return

    if command_matches(command, ["click", "press"]):
        pyautogui.click()
    if command_matches(command, ["double click", "double press"]):
        pyautogui.doubleClick()
    if command_matches(command, ["right click", "right press"]):
        pyautogui.rightClick()
    if command_matches(command, ["mouse down", "hold"]):
        pyautogui.mouseDown()
    if command_matches(command, ["mouse up", "release"]):
        pyautogui.mouseUp()

    if command_matches(command, ["scroll up"]):
        pyautogui.scroll(200)
    if command_matches(command, ["scroll down"]):
        pyautogui.scroll(-200)
    if command_matches(command, ["scroll left"]):
        pyautogui.hscroll(-200)
    if command_matches(command, ["scroll right"]):
        pyautogui.hscroll(200)

    if command_matches(command, ["refresh"]):
        pyautogui.hotkey("ctrl", "r")
    if command_matches(command, ["select"]):
        pyautogui.press("enter")
    if command_matches(command, ["close"]):
        pyautogui.hotkey("alt", "f4")
    if command_matches(command, ["fullscreen"]):
        pyautogui.press("f11")
    if command_matches(command, ["screenshot"]):
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        set_voice_status("Screenshot saved")
    if command_matches(command, ["undo"]):
        pyautogui.hotkey("ctrl", "z")
    if command_matches(command, ["redo"]):
        pyautogui.hotkey("ctrl", "y")
    if command_matches(command, ["copy"]):
        pyautogui.hotkey("ctrl", "c")
    if command_matches(command, ["paste"]):
        pyautogui.hotkey("ctrl", "v")
    if command_matches(command, ["cut"]):
        pyautogui.hotkey("ctrl", "x")
    if command_matches(command, ["select all"]):
        pyautogui.hotkey("ctrl", "a")
    if command_matches(command, ["find"]):
        pyautogui.hotkey("ctrl", "f")
    if command_matches(command, ["save"]):
        pyautogui.hotkey("ctrl", "s")
    if command_matches(command, ["enter"]):
        pyautogui.press("enter")
    if command_matches(command, ["escape"]):
        pyautogui.press("esc")
    if command_matches(command, ["space"]):
        pyautogui.press("space")
    elif command_matches(command, ["remove"]):
        pyautogui.press("backspace")
    if command_matches(command, ["delete"]):
        pyautogui.press("delete")
    if command_matches(command, ["erase line"]):
        pyautogui.hotkey("ctrl", "backspace")
    if command_matches(command, ["maximize", "max"]):
        gw.getActiveWindow().maximize()
    if command_matches(command, ["minimize", "mini"]):
        gw.getActiveWindow().minimize()
    if command_matches(command, ["volume up", "sound up"]):
        pyautogui.press("volumeup")
    if command_matches(command, ["volume down", "sound down"]):
        pyautogui.press("volumedown")
    if command_matches(command, ["mute", "unmute"]):
        pyautogui.press("volumemute")
    if command_matches(command, ["zoom in"]):
        pyautogui.hotkey("ctrl", "+")
    if command_matches(command, ["zoom out"]):
        pyautogui.hotkey("ctrl", "-")

    if "type " in command:
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
    else:
        set_voice_status(f"Unknown command: {command}")
        print(f"Unknown command: '{command})'")


            
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
            print(f"Heard: {command}")
            set_voice_status(f"Heard: {command}")
            execute_command(command)

        except sr.UnknownValueError:
            print("Could not understand.")
            set_voice_status("Didn't catch that.")
        except sr.RequestError as e:
            print(f"[Error with recognition: {e}")
            set_voice_status("Recognition error.")
        time.sleep(1)
