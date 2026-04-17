# AI Drive Cleaner

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)

A production-ready command-line tool that scans your Windows C: drive for junk and unwanted files, uses the Groq AI engine to classify them, and securely deletes them after explicit user permission.

## Features

- **Deep Windows Scan**: Safely scans common temporary, cache, and dump directories. Excludes system critical files.
- **AI-Powered Analysis**: Leverages fast Groq language models to determine if files are safe to delete, need review, or should be kept.
- **Beautiful CLI UI**: Built with `rich` for a stunning terminal experience.
- **Fail-Safe**: Never deletes files without your explicit permission.

## Requirements

- Windows OS
- Python 3.10+
- A Groq API Key (get one at [console.groq.com](https://console.groq.com/))

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/ai-drive-cleaner.git
cd ai-drive-cleaner
pip install -r requirements.txt
```

## Usage

```bash
python -m ai_drive_cleaner.main
```
Or if installed via pip:
```bash
ai-drive-cleaner
```

### Models Used
This tool relies on the following models via the Groq API (with automatic fallback):
1. `moonshotai/Kimi-K2-Instruct-0905` (Primary)
2. `qwen/qwen3-32b` (Fallback 1)
3. `llama-3.3-70b-versatile` (Fallback 2)

## Warning
Always review before deleting. The tool asks for confirmation.

## Screenshots
<!-- Add your screenshots here -->
