import cv2
import numpy as np
from pytubefix import YouTube
from colorama import Fore, Style, init
import os
import time
import subprocess
import threading
import sys
from playsound import playsound

# Initializing colorama for colorful console output
init(autoreset=True)

# A list of ASCII characters ordered from darkest to lightest
ASCII_CHARS_GREYSCALE = "@%#*+=-:. "

# Your requested static delay to sync audio and video
STATIC_DELAY = -1.25

def clear_screen():
    """
    Clears the console screen, works for both Windows ('cls') and other systems ('clear').
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def get_ascii_char(pixel_value):
    """
    Maps a grayscale pixel value (0-255) to a character from the ASCII_CHARS_GREYSCALE list.
    """
    index = int(pixel_value / 256 * len(ASCII_CHARS_GREYSCALE))
    return ASCII_CHARS_GREYSCALE[index]

def play_audio(youtube_url, audio_ready_event, stop_event):
    """
    Downloads the audio using yt-dlp and plays it using the playsound library (for Windows).
    """
    audio_filename = "temp_audio.wav"
    command = [
        "yt-dlp",
        "-x",  # Extract audio
        "--audio-format", "wav",
        "--audio-quality", "0",  # Best quality
        "--no-playlist",  # Prevents downloading an entire playlist
        "-o", audio_filename,
        youtube_url
    ]

    print(f"{Fore.YELLOW}>> Grabbing the audio stream... this might take a moment!")
    try:
        # Check if yt-dlp is installed and run it
        subprocess.run(["yt-dlp", "--version"], check=True, capture_output=True)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"{Fore.RED}yt-dlp download failed. Error: {stderr}")
            stop_event.set()
            return
            
    except FileNotFoundError:
        print(f"{Fore.RED}Oops! yt-dlp is not installed. Please install it (pip install yt-dlp).")
        stop_event.set()
        return
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Bummer! Failed to download audio. Error: {e.stderr}")
        stop_event.set()
        return

    print(f"{Fore.GREEN}>> Audio downloaded! Now attempting to play...")
    
    # Signal that audio is ready to go, even before playback starts, for better sync
    audio_ready_event.set()
    
    try:
        playsound(audio_filename)
        
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
        print(f"{Fore.MAGENTA}>> Audio cleanup complete!")
        
    except Exception as e:
        print(f"{Fore.RED}Yikes! Couldn't play the audio. Error: {e}")
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
        stop_event.set()
        return
    
def get_video_stream(youtube_url):
    """
    Downloads and plays the video stream.
    """
    try:
        yt = YouTube(youtube_url)
        # Find the best progressive stream to play
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not stream:
            print(f"{Fore.RED}Couldn't find a suitable progressive video stream.")
            return None
        return stream
    except Exception as e:
        print(f"{Fore.RED}Bummer! Couldn't grab the video stream. Error: {e}")
        return None

def main():
    """Main function to run the script."""
    
    youtube_url = input("Yo, drop a YouTube video link here: ")
    mode = 'ascii'

    stop_event = threading.Event()
    audio_ready_event = threading.Event()

    audio_thread = threading.Thread(target=play_audio, args=(youtube_url, audio_ready_event, stop_event))
    audio_thread.start()

    print(f"{Fore.CYAN}>> Audio download started. Waiting for audio to be ready...")

    audio_ready_event.wait()
    
    if stop_event.is_set():
        print(f"{Fore.RED}Audio download failed. Exiting.")
        audio_thread.join()
        return
        
    print(f"{Fore.CYAN}>> Audio is now playing! Starting video playback.")

    stream = get_video_stream(youtube_url)
    if not stream:
        stop_event.set()
        audio_thread.join()
        return

    cap = cv2.VideoCapture(stream.url)
    if not cap.isOpened():
        print(f"{Fore.RED}Couldn't open the video stream. Is the URL valid?")
        stop_event.set()
        audio_thread.join()
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = 1.0 / fps if fps > 0 else 0.03
    
    video_start_time = time.time()
    frame_index = 0
    
    while cap.isOpened() and not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        # Calculate the target time for this specific frame
        target_time = video_start_time + frame_index * frame_interval
        
        # Wait until the target time, adding the static delay you requested
        current_time = time.time()
        sleep_time = target_time - current_time + STATIC_DELAY
        if sleep_time > 0:
            time.sleep(sleep_time)

        # Process the frame
        new_width = 120
        aspect_ratio = frame.shape[1] / frame.shape[0]
        new_height = int(new_width / aspect_ratio * 0.5)
        resized_frame = cv2.resize(frame, (new_width, new_height))
        
        clear_screen()
        
        output_frame = ""
        grayscale_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        for row in grayscale_frame:
            output_frame += "".join([get_ascii_char(pixel) for pixel in row]) + "\n"
        
        print(output_frame)
        
        frame_index += 1

    cap.release()
    cv2.destroyAllWindows()
    stop_event.set()
    audio_thread.join()
    time.sleep(5)
    print(f"{Fore.GREEN}Playback finished! What a chaotic masterpiece.")

if __name__ == "__main__":
    main()
