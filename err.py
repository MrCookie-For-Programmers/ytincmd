import cv2
import numpy as np
from pytubefix import YouTube
from colorama import Fore, Style, init
import os
import time
import subprocess
import threading
import sys

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
    Downloads and plays the audio using yt-dlp and aplay.
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
    try:
        # Use aplay to play the audio
        aplay_command = ["aplay", audio_filename]
        audio_process = subprocess.Popen(aplay_command)
        
        time.sleep(0.5)
        
        if audio_process.poll() is not None:
            print(f"{Fore.RED}Aplay failed to start. Is 'aplay' installed and working?")
            stop_event.set()
            return

        audio_ready_event.set()  # Signal that audio is ready to go

        while audio_process.poll() is None and not stop_event.is_set():
            time.sleep(0.1)

        if audio_process.poll() is None:
            audio_process.terminate()

        os.remove(audio_filename)
        print(f"{Fore.MAGENTA}>> Audio cleanup complete!")

    except Exception as e:
        print(f"{Fore.RED}Yikes! Couldn't play the audio. Error: {e}")
        if os.path.exists(audio_filename):
            os.remove(audio_filename)
        stop_event.set()
        return

def download_video(youtube_url):
    """
    Downloads the best quality progressive video stream and returns the filename.
    """
    video_filename = "temp_video.mp4"
    try:
        yt = YouTube(youtube_url)
        print(f"{Fore.YELLOW}>> Grabbing the video stream and downloading it to a file... this might take a moment!")
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not stream:
            print(f"{Fore.RED}Couldn't find a suitable progressive video stream.")
            return None
        
        stream.download(filename=video_filename)
        print(f"{Fore.GREEN}>> Video downloaded! Ready to rock.")
        return video_filename
    except Exception as e:
        print(f"{Fore.RED}Bummer! Couldn't grab or download the video stream. Error: {e}")
        return None

def main():
    """Main function to run the script."""
    
    youtube_url = input("Yo, drop a YouTube video link here: ")
    print("Choose your playback mode, my dude:")
    print("1. Classic ASCII (black and white)")
    print("2. FULL COLOR ASCII (the real deal)")
    
    mode_choice = input("Enter 1 or 2: ")
    if mode_choice == '1':
        mode = 'ascii'
        print(f"{Fore.CYAN}>> Let's get retro with Classic ASCII!")
    elif mode_choice == '2':
        mode = 'full_color'
        print(f"{Fore.CYAN}>> Prepare for a visual fiesta with FULL COLOR ASCII!")
    else:
        print(f"{Fore.RED}That's wackier than a rubber duck trying to lead a storm! Defaulting to Classic ASCII.")
        mode = 'ascii'
        
    invert_choice = input("Do you want to invert the colors? (y/n): ")
    invert_colors = invert_choice.lower() == 'y'

    if invert_colors:
        print(f"{Fore.CYAN}>> Cosmic inversion activated! Prepare for the flip.")
    else:
        print(f"{Fore.CYAN}>> No inversion. Sticking to the standard path.")


    stop_event = threading.Event()
    audio_ready_event = threading.Event()

    audio_thread = threading.Thread(target=play_audio, args=(youtube_url, audio_ready_event, stop_event))
    audio_thread.start()

    print(f"{Fore.CYAN}>> Audio download started. Waiting for audio to be ready...")
    
    video_filename = download_video(youtube_url)
    if not video_filename:
        stop_event.set()
        audio_thread.join()
        return

    audio_ready_event.wait()
    
    if stop_event.is_set():
        print(f"{Fore.RED}Audio download failed. Exiting.")
        if os.path.exists(video_filename):
            os.remove(video_filename)
        audio_thread.join()
        return
        
    print(f"{Fore.CYAN}>> Audio is now playing! Starting video playback.")

    cap = cv2.VideoCapture(video_filename)
    if not cap.isOpened():
        print(f"{Fore.RED}Couldn't open the video file. Is the file valid?")
        stop_event.set()
        audio_thread.join()
        return

    try:
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
            
            if mode == 'ascii':
                grayscale_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
                for row in grayscale_frame:
                    row_chars = ""
                    for pixel in row:
                        if invert_colors:
                            pixel = 255 - pixel
                        row_chars += get_ascii_char(pixel)
                    output_frame += row_chars + "\n"
            elif mode == 'full_color':
                # We will use the BGR frame directly
                for row in resized_frame:
                    row_chars = ""
                    for pixel in row:
                        # OpenCV uses BGR, so we grab those values
                        b, g, r = pixel
                        
                        # Calculate a brightness value for the ASCII character
                        # A standard luminosity formula
                        brightness = int(0.299 * r + 0.587 * g + 0.114 * b)
                        
                        # Invert the brightness if the user wants it
                        if invert_colors:
                            brightness = 255 - brightness
                        
                        ascii_char = get_ascii_char(brightness)
                        
                        # Generate the 24-bit color escape code
                        color_code = f"\033[38;2;{r};{g};{b}m"
                        row_chars += f"{color_code}{ascii_char}"
                    
                    output_frame += row_chars + "\033[0m" + "\n" # Reset color at end of line
            
            print(output_frame)
            
            frame_index += 1

    finally:
        cap.release()
        cv2.destroyAllWindows()
        stop_event.set()
        audio_thread.join()
        if os.path.exists(video_filename):
            os.remove(video_filename)
        print(f"{Fore.GREEN}Playback finished and cleanup complete! What a chaotic masterpiece.")

if __name__ == "__main__":
    main()
