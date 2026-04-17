from setuptools import setup, find_packages
import os

# Read the contents of the README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ai-drive-cleaner",
    version="1.0.0",
    description="A sassy TUI that uses Groq AI to scan, roast, and clean your Windows C: drive.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Himanshu Mudigonda",
    url="https://github.com/himanshumudigonda/ai-drive-cleaner",
    packages=find_packages(),
    install_requires=[
        "groq>=0.9.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "textual>=0.52.1"
    ],
    entry_points={
        "console_scripts": [
            "ai-drive-cleaner=ai_drive_cleaner.main:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
    ],
    keywords="ai cleaner groq textual tui windows bloatware",
    project_urls={
        "Source": "https://github.com/himanshumudigonda/ai-drive-cleaner",
        "Tracker": "https://github.com/himanshumudigonda/ai-drive-cleaner/issues",
    },
)
