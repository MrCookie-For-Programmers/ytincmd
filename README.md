#IMPORTANT NOTE: MACOS AND WINDOWS ARENT TESTED



make sure the requirements.txt has the correct name for each os in the command btw


ASCII Video Player 🎬👾
This Python script is a wild little creation that plays YouTube videos directly in your console as glorious ASCII art. It even attempts to sync the audio, turning your terminal into a retro-futuristic multimedia experience. It's like watching a movie on a super-low-fi, interdimensional screen.

This project is a multi-platform beast, with a dedicated script for Linux, Windows, and macOS to handle audio playback natively.

Features
Plays YouTube videos as ASCII art in the console.

Downloads and plays the audio in a separate thread for (mostly) synchronized playback.

Clears the screen for a smooth, flipbook-like effect.

Prerequisites
You'll need Python 3 installed on your system. Each OS-specific script also relies on several libraries and system commands.

Installation
Choose the installation instructions for your operating system below. Each set of instructions uses a different Python script and requirements.txt file.

Linux 🐧
For Linux, it's best to use a virtual environment to keep things tidy. We'll also grab some system dependencies. This version of the script uses the aplay command for audio.

First, make sure you have pip, venv, and alsa-utils installed.

sudo apt update
sudo apt install -y python3-pip python3-venv alsa-utils

The alsa-utils package provides the aplay command for audio playback.

Copy the lol-linux.py and requirements-linux.txt files to your project directory.

Create and activate a virtual environment.

python3 -m venv venv
source venv/bin/activate

Install the required Python packages.

pip install -r requirements-linux.txt

Run the script:

python3 lol-linux.py

Windows 💻
For Windows, you can install the dependencies directly with pip. This version of the script uses the playsound library, which is a great cross-platform solution that works well on Windows.

Copy the lol-windows.py and requirements-windows.txt files to your project directory.

Install the required Python packages. It's recommended to use py to ensure you're using Python 3.

py -m pip install -r requirements-windows.txt

Run the script:

py lol-windows.py

macOS 🍎
For macOS, you can install the dependencies directly with pip. This version of the script uses the native afplay command for audio playback, so no extra system dependencies are needed.

Copy the lol-macos.py and requirements-macos.txt files to your project directory.

Install the required Python packages.

pip3 install -r requirements-macos.txt

Run the script:

python3 lol-macos.py
