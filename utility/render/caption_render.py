import logging
import subprocess
import os
import utility.logger_config
SUBTITLE_TEMPLATE = """[Script Info]
Title: Centered Captions Example
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,15,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,20,3,5,10,10,10,1
Style: Yellow,Arial,15,&H00FFFF00,&H000000FF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,20,3,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

SUBTITLE_LINE = "Dialogue: 0,%s,%s,Default,,0,0,0,,{\an5}%s"
SUBTITLE_LINE_YELLOW = "Dialogue: 0,%s,%s,Yellow,,0,0,0,,{\an5}%s"

def add_caption(file_path, timed_captions):


    subtitle_content = SUBTITLE_TEMPLATE
    i = 0
    while i < len(timed_captions) - 1:
        (t1, t2), caption_text = timed_captions[i]
        (next_t1, next_t2), next_caption_text = timed_captions[i + 1]
        
        # Process current and next row simultaneously
        subtitle_content += SUBTITLE_LINE % (t1, t2, caption_text) + "\n"
        subtitle_content += SUBTITLE_LINE_YELLOW % (next_t1, next_t2, next_caption_text) + "\n"
        
        i += 2

    # Handle the last, unpaired row if present
    if i < len(timed_captions):
        (t1, t2), caption_text = timed_captions[i]
        subtitle_content += SUBTITLE_LINE % (t1, t2, caption_text) + "\n"

    caption_ass_file_path=file_path.replace(".mp4", f"_caption.ass")
    with open(caption_ass_file_path, "w") as caption_ass_file:
        caption_ass_file.write(subtitle_content)

    output_video=file_path.replace(".mp4", f"_caption.mp4")

    # FFmpeg command to burn the stylized ASS subtitles into the video
    subprocess.run([
        'ffmpeg', '-y', '-i', file_path, '-vf', f"ass={caption_ass_file_path}", 
        '-c:a', 'copy', output_video
    ])

    return None