import asyncio
import whisper_timestamped as whisper
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio, download_audio
from utility.captions.timed_caption_ffmpg import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
import utility.logger_config
import logging
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a topic.")
    parser.add_argument("topic", type=str, help="The topic for the video")
    parser.add_argument("jobId", type=int, help="Job id")
    parser.add_argument("language", type=str, help="language")
    parser.add_argument("audioUrl",  nargs='?', default=None,type=str, help="audioUrl")

    args = parser.parse_args()
    SAMPLE_TOPIC = args.topic
    JOB_ID=args.jobId
    LANGUAGE = args.language
    AUDIO_URL=args.audioUrl

    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"
    BACKGROUND_AUDIO_PATH_OUTPUT = "audio_background"
    
    # response = generate_script(SAMPLE_TOPIC)
    response = SAMPLE_TOPIC
    #response = '{"script":"I (36M) met my now ex (34F) a little over 2 years ago. During that time, the idea of her getting a boob job has come up a few times. She\'d asked me I ever dated anyone with them and what I thought of them. I told her I had, I am not a fan at all and they are a deal breaker for me"}'

    logging.info("Generating script for topic: %s", response)
    asyncio.run(generate_audio(response, SAMPLE_FILE_NAME, LANGUAGE))

    timed_captions = generate_timed_captions("test.vtt")
    logging.info("Timed captions generated: %s", timed_captions)

    timed_captions_mini = generate_timed_captions("test.vtt2")
    logging.info("Timed captions mini generated: %s", timed_captions_mini)

    search_terms = getVideoSearchQueriesTimed(response, timed_captions)
    #search_terms = [[[0, 2.82], ['meeting ex', 'relationship start', 'two years']], [[2.82, 5.24], ['ex-girlfriend', 'couple years', 'time together']], [[5.24, 7.54], ['boob job', 'surgery discussion', 'breast enhancement']], [[7.54, 9.24], ['previous partners', 'dating history', 'opinion on surgery']], [[9.24, 11.84], ['personal preference', 'dislikes surgery', 'deal breaker']]]
    logging.info("Search terms generated: %s", search_terms)

    background_video_urls = None
    if search_terms is not None:
        #background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
        background_video_urls = [[[0, 2.82], 'https://videos.pexels.com/video-files/6774385/6774385-hd_1080_1920_30fps.mp4'], [[2.82, 5.24], 'https://videos.pexels.com/video-files/4873454/4873454-hd_1080_1920_25fps.mp4'], [[5.24, 7.54], 'https://videos.pexels.com/video-files/8348724/8348724-hd_1080_1920_25fps.mp4'], [[7.54, 9.24], 'https://videos.pexels.com/video-files/5520102/5520102-hd_1080_1920_30fps.mp4'], [[9.24, 11.84], 'https://videos.pexels.com/video-files/7424458/7424458-hd_1080_1920_30fps.mp4']]
        logging.info("Background videos generated: %s", background_video_urls)
    else:
        logging.error("No background video found")

    background_video_urls = merge_empty_intervals(background_video_urls)

    background_audio_path = None
    if AUDIO_URL is not None:
        background_audio_path= download_audio(AUDIO_URL,BACKGROUND_AUDIO_PATH_OUTPUT)
        logging.info("Background audio path %s", background_audio_path)

    if background_video_urls is not None:
        video = get_output_media(SAMPLE_FILE_NAME, background_audio_path, timed_captions_mini, background_video_urls, VIDEO_SERVER, JOB_ID)
        logging.info("Video generation completed")
    else:
        logging.error("No video generated")
        
    logging.info("Process completed for topic: %s", SAMPLE_TOPIC)
