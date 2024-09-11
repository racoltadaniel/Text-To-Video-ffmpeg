import edge_tts
import logging
import utility.logger_config
from pytube import YouTube
import yt_dlp

async def generate_audio(text,outputFilename, language):
    lang = 'en-AU-WilliamNeural'
    if (language == "Indonesian-Female"):
        lang = "id-ID-GadisNeural"
    if (language == "Indonesian-Male"):
        lang = "id-ID-ArdiNeural"
    if (language == "English-Female"):
        lang = "en-US-AriaNeural"
    if (language == "Romanian-Female"):
        lang = "ro-RO-AlinaNeural"
    if (language == "Romanian-Male"):
        lang = "ro-RO-EmilNeural"

    communicate = edge_tts.Communicate(text, lang)
    submaker = edge_tts.SubMaker()
    with open(outputFilename, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # logging.info("Offest %s duration %s text %s", chunk["offset"], chunk["duration"], chunk["text"])
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    with open("test.vtt", "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs())

    with open("test.vtt2", "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs(words_in_cue=2))
        
def download_audio(youtube_url, output_path):
    try:
        # Create a YouTube object
        yt = YouTube(youtube_url)

        # Get the highest resolution audio stream available
        audio_stream = yt.streams.filter(only_audio=True).first()

        # Download the audio stream
        audio_path = audio_stream.download(output_path=output_path)
        logging.info(f"Audio downloaded successfully: {audio_path} from link: {youtube_url}")
        return audio_path
    except Exception as e:
        logging.info(f"An error occurred: {e}")
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            logging.info(f"Audio downloaded successfully: {output_path}")
            return output_path +".mp3"
        except Exception as e:
            logging.info(f"An error occurred: {e}")