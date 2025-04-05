import voice

def main():
    print("🎬 Voice Command App Started")
    print("Say 'sync on' to activate. Use 'sync pause', 'sync resume', or 'sync off' to control it.")

    while True:
        voice.listen_and_execute()

if __name__ == "__main__":
    main()
