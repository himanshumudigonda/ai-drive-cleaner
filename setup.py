from setuptools import setup, find_packages

setup(
    name="ai-drive-cleaner",
    version="1.0.0",
    description="A command-line tool that scans the Windows C: drive, uses Groq AI to identify junk files, and deletes them upon confirmation.",
    packages=find_packages(),
    install_requires=[
        "groq>=0.5.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "ai-drive-cleaner=ai_drive_cleaner.main:main",
        ],
    },
    python_requires=">=3.10",
)
