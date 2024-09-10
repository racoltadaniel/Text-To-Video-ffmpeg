import os
import tempfile
import platform
import subprocess
import logging
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, VideoFileClip)
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from .caption_render import add_caption
import requests


generateFolder = ''
def read_api_key(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('generate_folder='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        print(f"Properties file not found: {file_path}")
    except Exception as e:
        print(f"Error reading properties file: {e}")
    return None

logging.basicConfig(
    filename= os.path.join(os.path.dirname(__file__), 'app.log'),            # Log file name
    filemode='a',                  # Append mode
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    level=logging.DEBUG            # Log level (DEBUG for detailed logs)
)

generateFolder = read_api_key('/etc/properties/videogen.properties')

def download_file(url, filename):
    with open(filename, 'wb') as f:
        response = requests.get(url)
        f.write(response.content)

def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    return program_path

def split_text(text, max_length=20):
    """Split text into two lines without cutting words."""
    if len(text) <= max_length:
        return text, ''
    
    split_index = text.rfind(' ', 0, max_length)
    
    if split_index == -1:
        split_index = max_length
    
    if split_index == 0:
        split_index = text.find(' ', max_length)
        if split_index == -1:
            split_index = len(text)
    
    line1 = text[:split_index].strip()
    line2 = text[split_index:].strip()
    
    return line1, line2



def get_output_media(audio_file_path, timed_captions, background_video_data, video_server, job_id):
    OUTPUT_FILE_NAME = generateFolder + "/rendered_video"+ str(job_id) +".mp4"
    magick_path = get_program_path("magick")
    print(magick_path)
    if magick_path:
        os.environ['IMAGEMAGICK_BINARY'] = magick_path
    else:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
    
    visual_clips = []

    target_resolution = (1080, 1920)

    for (t1_video, t2_video), video_url in background_video_data:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        download_file(video_url, video_filename)
        
        video_clip = VideoFileClip(video_filename)
        video_clip = video_clip.resize(newsize=target_resolution)
        video_clip = video_clip.set_start(t1_video).set_end(t2_video)
        logging.info("Created video %s", video_filename)
        visual_clips.append(video_clip)
                    
                
    video = CompositeVideoClip(visual_clips)
    
    audio_clips = []
    audio_file_clip = AudioFileClip(audio_file_path)
    audio_clips.append(audio_file_clip)

    if audio_clips:
        audio = CompositeAudioClip(audio_clips)
        video.duration = audio.duration
        video.audio = audio

    video.write_videofile(OUTPUT_FILE_NAME, codec='libx264', audio_codec='aac', fps=25, preset='veryfast', threads=4)

    for (t1, t2), video_url in background_video_data:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        os.remove(video_filename)

    add_caption(OUTPUT_FILE_NAME, timed_captions)

    return OUTPUT_FILE_NAME
