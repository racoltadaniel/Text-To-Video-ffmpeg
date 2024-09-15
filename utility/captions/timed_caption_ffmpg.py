import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re
import logging
import utility.logger_config
import re

def format_timestamp(ts):
    # Split the timestamp into hours, minutes, seconds, and milliseconds
    match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})', ts)
    if match:
        hours, minutes, seconds, milliseconds = match.groups()
        # Convert milliseconds to seconds and format the timestamp
        total_seconds = int(seconds) + int(milliseconds) / 1000
        return f'{int(hours)}:{int(minutes):02}:{total_seconds:05.2f}'
    else:
        raise ValueError(f"Invalid timestamp format: {ts}")

def parse_vtt(vtt_file):
    with open(vtt_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    captions = []
    current_caption = None
    
    for line in lines:
        line = line.strip()
        
        # Check if the line is a timestamp line
        match = re.match(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', line)
        if match:
            if current_caption:
                captions.append(current_caption)
            start_time, end_time = match.groups()
            start_time = format_timestamp(start_time)
            end_time = format_timestamp(end_time)
            current_caption = ((start_time, end_time), "")
        elif current_caption:
            # Accumulate text lines
            if line:
                current_caption = ((current_caption[0]), f"{current_caption[1]} {line}".strip())
                logging.info("Line %s", line)
            else:
                # Empty line indicates the end of the caption
                captions.append(current_caption)
                logging.info("Line %s", line)
                current_caption = None
    
    if current_caption:
        captions.append(current_caption)
    
    return captions

def generate_timed_captions(subtitle_file):
    captions = parse_vtt(subtitle_file)
    logging.info(captions)
    merged = []
    i = 0
    while i < len(captions):
        interval, text = captions[i]

        if i < len(captions) - 1:
            next_interval = captions[i + 1][0]
            if interval[1] != next_interval[0]:
                new_interval = (interval[0], next_interval[0])
                captions[i] = (new_interval, text) 

        merged.append([interval, text])
        i += 1

    first_entry = captions[0]
    first_entry_interval = first_entry[0]
    first_entry_interval_new = (0.0 , first_entry_interval[1]) 
    captions[0] = (first_entry_interval_new, first_entry[1])
    last_entry = captions[-1]
    start_time_last, end_time_last = last_entry[0]
    end_time = timestamp_to_seconds(end_time_last)
    end_time +=1
    new_end_time_last = seconds_to_timestamp(end_time)
    new_last= ((start_time_last, new_end_time_last), last_entry[1])
    captions.pop()
    captions.append(new_last)
    logging.info("new captiosn: %s", captions)
    return captions

def replace_first_caption(captions, caption_one_word ):
    new_caption = []
    new_first_caption_text = ""
    new_first_caption_start = captions[0][0][0]

    i=0
    startCaptionFrom = 0
    while i < len(caption_one_word):
        interval, text = caption_one_word[i]
        if(text.istitle() and i>0):
            # if new sentence
            for caption in captions:
                # if first word in next caption the capital letter leave it unchange, continue appending from here
                if(caption[0][0] == interval[0]):
                    startCaptionFrom=captions.index(caption)
                    new_first_caption_end = interval[0]
                    break
            
            if(startCaptionFrom>0):
                break

            j=0
            while j < len(captions):
                caption= captions[j]
                # if last word in next caption
                if(caption[0][1] == interval[1]):
                    #continue caption from here but 
                    startCaptionFrom=captions.index(caption)
                    #make interval smaller
                    new_first_caption_end = interval[0]
                    captions[j] = ((interval[0], caption[0][1]), caption[1].split()[-1])
                    
                    break
                j += 1
            break
        else:
            new_first_caption_text+= text + " "
        i += 1

    new_caption.append(((new_first_caption_start, new_first_caption_end ), new_first_caption_text))

    i=startCaptionFrom
    while i < len(captions):
        caption = captions[i]
        new_caption.append(caption)
        i+=1

    return new_caption

def timestamp_to_seconds(ts):
    # Convert timestamp in format 0:00:04.41 to seconds
    match = re.match(r'(\d+):(\d{2}):(\d{2})\.(\d{2})', ts)
    if match:
        hours, minutes, seconds, milliseconds = match.groups()
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 100
        return total_seconds
    else:
        raise ValueError(f"Invalid timestamp format: {ts}")

def seconds_to_timestamp(seconds):
    # Convert seconds to timestamp in format 0:00:04.41
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 100)
    return f"{hours}:{minutes:02}:{int(seconds):02}.{milliseconds:02}"