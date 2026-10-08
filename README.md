# 🤖 Professional Telegram Userbot

A powerful and modular Telegram Userbot built with Python and "Telethon" (https://github.com/LonamiWebs/Telethon).

Created by "@AliyHacker" (https://github.com/aliyhacker) ❤️

«⚡ Automation • AI • Telegram • Python • Cybersecurity»

## ✨ Features

- 🤖 AI-powered Auto Reply
- 🧠 AI-based message decisions
- ❤️ Automatic Telegram reactions
- 💬 Context-aware conversations
- 👤 Telegram profile information handling
- 🧩 Modular function system
- ⚙️ Easy to extend with new features
- 📱 Termux / Android compatible

## 📁 Project Structure

telegram-userbot/
├── main.py
├── config.py
├── requirements.txt
├── install.sh
├── font/
│   └── NotoSerifCJK.ttc
└── functions/
    ├── autoreply.py
    └── ...

Each feature is separated into its own module inside the "functions/" directory.

This makes the userbot easier to maintain, modify and extend.

---

## 🛠️ Requirements

You need:

- Python 3
- Telegram API ID
- Telegram API Hash
- A Telegram account
- Internet connection

Python dependencies are listed in:

requirements.txt

📦 What is "requirements.txt"?

"requirements.txt" is a file that contains the Python libraries required by the project.

Instead of installing every library manually, you can install all dependencies with one command:

pip install -r requirements.txt

---

## 🚀 Installation

1. Clone the repository

git clone https://github.com/aliyhacker/telegram-userbot.git
cd telegram-userbot

2. Install dependencies

pip install -r requirements.txt

---

## ⚙️ Configuration

Configure your Telegram API credentials and other settings in:

config.py

You can obtain your Telegram API credentials from:

https://my.telegram.org

Never publish your API credentials, session files, API keys or other private information on GitHub.

---

## ▶️ Running the Userbot

After configuration:

python main.py

If everything is configured correctly, the userbot will start and connect to Telegram.

---

## 🤖 AI Auto Reply

The Auto Reply system can use an AI model to decide:

- whether to reply to a message
- whether to react to a message
- which reaction emoji to use
- what response should be sent

The system also supports conversation memory and Telegram profile context.

AI configuration is handled through the project configuration and OpenRouter API.

---

## 🧩 Modular Architecture

The project is designed to be modular.

Instead of putting everything inside "main.py", individual features are placed inside:

functions/

For example:

from functions.autoreply import register_autoreply

register_autoreply(client)

This allows new features to be added without turning "main.py" into a giant file.

---

## 📱 Telegram Channel

For updates, projects and other content:

👉 Telegram: https://t.me/hackerportfolio

---

## 🔗 Repository

GitHub:

https://github.com/aliyhacker/telegram-userbot

---

# ⚠️ Disclaimer

This project is intended for educational, automation and personal-use purposes.

Use the userbot responsibly and follow Telegram's Terms of Service and applicable laws.

The author is not responsible for misuse of this software.

---

## 👨‍💻 Author

AliyHacker

GitHub:
https://github.com/aliyhacker

Telegram:
https://t.me/aliyhacker

«Made with Python, Telethon and a little bit of chaos. 😂»

---

⭐ If you find this project useful, consider giving the repository a star!
