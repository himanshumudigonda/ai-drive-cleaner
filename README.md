# 🚀 AI Drive Cleaner

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Textual TUI](https://img.shields.io/badge/TUI-Textual-00ffff.svg)](https://textual.textualize.io/)
[![Powered by Groq](https://img.shields.io/badge/AI-Groq-f55036.svg)](https://groq.com/)

> **"Windows Disk Cleanup is boring. AI Drive Cleaner is judgmental."**

**AI Drive Cleaner** is a blazingly fast, Terminal User Interface (TUI) process manager that uses Large Language Models (LLMs) to scan your C: drive, hunt down bloatware and temporary files, and roast them before letting you safely delete them.

Built with Python and **Textual**, and powered by the lightning-fast **Groq API**.

---

## ✨ Features

- **Split-Screen TUI**: A beautiful terminal dashboard displaying your junk files on the left, and the AI's "Brain Stream" on the right.
- **Context-Aware AI**: It doesn't just find temporary files; it uses Groq's LLMs (Kimi, Qwen, Llama) to analyze if a file is actually safe to delete. 
- **The Roasts**: The AI doesn't just categorize files as `SAFE_DELETE`—it gives you a funny, snarky reason *why* the file deserves to be deleted.
- **Fail-Safe Deletions**: Files are heavily filtered, and Windows critical files are completely ignored. Nothing is *ever* deleted without your explicit final `YES` confirmation.

---

## 🚀 Quick Start

### 1. Install Dependencies
Make sure you have Python 3.10+ installed.

```bash
git clone https://github.com/himanshumudigonda/ai-drive-cleaner.git
cd ai-drive-cleaner
pip install -r requirements.txt
```

### 2. Run the TUI
```bash
python -m ai_drive_cleaner.main
```

### 3. Add Your Brain (API Key)
1. Get a completely free, lightning-fast API Key from [console.groq.com](https://console.groq.com).
2. Launch the app.
3. Press **`k`** to open the Key Manager and paste your key.
4. Press **`s`** to start the deep scan!

---

## 🎮 Controls

| Key | Action | Description |
| --- | --- | --- |
| **`k`** | **Key Config** | Enter your Groq API key securely. |
| **`s`** | **Scan Drive** | Initiate the deep recursive scan of your C: drive. |
| **`d`** | **Delete Junk** | Open the confirmation modal to permanently delete all `SAFE_DELETE` files. |
| **`q`** | **Quit** | Exit the cleaner. |

---

## 🛠️ Built With
- **[Textual](https://textual.textualize.io/)**: The framework powering the terminal UI.
- **[Groq](https://groq.com/)**: The world's fastest AI inference engine.
- **Python**: Core logic and system interactions.

---

*Found a bug or want to add a feature? PRs are always welcome!*
