# ContinueExtensionProxy
Simple proxy to intercept request from Continue Extension to local Ollama server.

## Installation
 - Download lastest release from [Releases](https://github.com/Anh39/ContinueExtensionProxy/releases)
 - Run .exe file directly or with CLI.
 - Server will forward request from port 11433 to 11434 (Ollama).

## Build from source
 - Create new python environment with version 3.12.8
 - Install requirement with [requirements.txt](requirements.txt)
 - Build app with `pyinstaller --onefile app.py`
