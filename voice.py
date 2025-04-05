import pyautogui
import speech_recognition as sr
import os
import fnmatch
import platform
import getpass

is_active = False
is_paused = False

def normalize_command(command):
    return command.lower().replace("sink", "sync").strip()

def open_app(app_name):
    if platform.system() != "Windows":
        print("[!] 'open' command is only supported on Windows.")
        return

    app_name = app_name.lower().strip()
    user = getpass.getuser()

    # Start Menu paths to search
    search_paths = [
        rf"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        rf"C:\Users\{user}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"
    ]

    matches = []

    for base in search_paths:
        for root, dirs, files in os.walk(base):
            for file in files:
                if fnmatch.fnmatch(file.lower(), "*.lnk") and app_name in file.lower():
                    full_path = os.path.join(root, file)
                    matches.append(full_path)

    if matches:
        print(f"🚀 Opening {os.path.basename(matches[0])}")
        os.startfile(matches[0])
    else:
        print(f"[!] Could not find an app matching '{app_name}' in Start Menu.")

def execute_command(command):
    global is_active, is_paused

    command = normalize_command(command)

    # Wake word handling
    if command == "sync on":
        is_active = True
        is_paused = False
        print("✅ Sync is now ON.")
        return
    elif command == "sync off":
        print("🛑 Sync is now OFF. Exiting...")
        exit(0)
    elif command == "sync pause":
        if is_active:
            is_paused = True
            print("⏸️ Sync PAUSED.")
        return
    elif command == "sync resume":
        if is_active:
            is_paused = False
            print("▶️ Sync RESUMED.")
        return

    # If not active or paused, ignore
    if not is_active:
        print("⚠️ Ignoring command. Sync is OFF.")
        return
    if is_paused:
        print("⏸️ Ignoring command. Sync is PAUSED.")
        return

    # "Open app" command
    if command.startswith("open "):
        app_to_open = command[5:].strip()
        open_app(app_to_open)
        return

    # Action commands
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
        case "close":
            pyautogui.hotkey("alt", "f4")
        case "fullscreen":
            pyautogui.press("f11")
        case "screenshot":
            screenshot = pyautogui.screenshot()
            screenshot.save("screenshot.png")
            print("📸 Screenshot saved as 'screenshot.png'.")
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
            text = command[5:]
            pyautogui.write(text)
        case _:
            print(f"[!] Unknown command: '{command}'")

def listen_and_execute():
    recognizer = sr.Recognizer()
    mic = sr.Microphone() 

    with mic as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"🗣️ Heard: {command}")
        execute_command(command)
    except sr.UnknownValueError:
        print("[!] Could not understand.")
    except sr.RequestError as e:
        print(f"[!] Error with recognition: {e}")
