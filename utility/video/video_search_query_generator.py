from openai import OpenAI
import os
import json
import re
from datetime import datetime
from utility.utils import log_response,LOG_TYPE_GPT
import logging
import utility.logger_config



log_directory = ".logs/gpt_logs"

prompt = """# Instructions

Given the following video script and timed captions, extract three visually concrete and specific keywords for each time segment that can be used to search for background videos. The keywords should be short and capture the main essence of the sentence. They can be synonyms or related terms. If a caption is vague or general, consider the next timed caption for more context. If a keyword is a single word, try to return a two-word keyword that is visually concrete. Ensure that the time periods are strictly consecutive and cover the entire length of the video. The output should be in JSON format, like this: [[[t1, t2], ["keyword1", "keyword2", "keyword3"]], [[t2, t3], ["keyword4", "keyword5", "keyword6"]], ...]. Please handle all edge cases, such as overlapping time segments, vague or general captions, and single-word keywords.
The most important thing is that all Timed Caption is covered, for every caption it's mandatory that we have at least one keyword.
For example, if the caption is 'The cheetah is the fastest land animal, capable of running at speeds up to 75 mph', the keywords should include 'cheetah running', 'fastest animal', and '75 mph'. Similarly, for 'The Great Wall of China is one of the most iconic landmarks in the world', the keywords should be 'Great Wall of China', 'iconic landmark', and 'China landmark'.

Important Guidelines:

Use only English in your text queries.
Each search string must depict something visual.
The most important thing is that all script is covered, for every caption it's mandatory that we have at least one keyword.
The depictions have to be extremely visually concrete, like rainy street, or cat sleeping.
'emotional moment' <= BAD, because it doesn't depict something visually.
'crying child' <= GOOD, because it depicts something visual.
The list must always contain the most relevant and appropriate query searches.
['Car', 'Car driving', 'Car racing', 'Car parked'] <= BAD, because it's 4 strings.
['Fast car'] <= GOOD, because it's 1 string.
  """


def read_api_key(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('openai_api_key='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        logging.error(f"Properties file not found: {file_path}")
    except Exception as e:
        logging.error(f"Error reading properties file: {e}")
    return None

api_key = read_api_key('/etc/properties/videogen.properties')
if api_key:
    client = OpenAI(api_key=api_key)
else:
    raise ValueError("API key is not available. Please check the properties file.")

def fix_json(json_str):
    # Replace typographical apostrophes with straight quotes
    json_str = json_str.replace("’", "'")
    # Replace any incorrect quotes (e.g., mixed single and double quotes)
    json_str = json_str.replace("“", "\"").replace("”", "\"").replace("‘", "\"").replace("’", "\"")
    # Add escaping for quotes within the strings
    json_str = json_str.replace('"you didn"t"', '"you didn\'t"')
    return json_str



def getVideoSearchQueriesTimed(script,captions_timed):
    end = captions_timed[-1][0][1]
    try:
        
        out = [[[0,0],""]]
        # while out[-1][0][1] != end:
        content = call_OpenAI(script,captions_timed, end)
        try:
            out = json.loads(content)
        except Exception as e:
            logging.error(e)
            try:
              content = fix_json(content.replace("```json", "").replace("```", ""))
              logging.error("ChatGPT Content %s",content)
              out = json.loads(content)
              return out
            except Exception as e:
              content= re.sub(r'(?<!")(\d+:\d+:\d+\.\d+)(?!")', r'"\1"', content)
              logging.error("ChatGPT Content %s",content)
              out = json.loads(content)
              return out
        return out
    except Exception as e:
        logging.error("error in response %s",e)
   
    return None

def call_OpenAI(script,captions_timed, end):
    user_content = """Script: {}
Timed Captions:{}
""".format(script,"".join(map(str,captions_timed)))
    print("Content", user_content)
    
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=1,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]
    )
    logging.info("ChatGPT Response : %s", response)
    text = response.choices[0].message.content.strip()
    text = re.sub('\s+', ' ', text)
    logging.info("ChatGPT Text: %s", text)
    log_response(LOG_TYPE_GPT,script,text)
    return text

def merge_empty_intervals(segments):
    merged = []
    i = 0
    while i < len(segments):
        interval, url = segments[i]

        if url is None:
            # Find consecutive None intervals
            j = i + 1
            while j < len(segments) and segments[j][1] is None:
                j += 1
            
            # Merge consecutive None intervals with the previous valid URL
            if i > 0:
                prev_interval, prev_url = merged[-1]
                if prev_url is not None and prev_interval[1] == interval[0]:
                    merged[-1] = [[prev_interval[0], segments[j-1][0][1]], prev_url]
                else:
                    merged.append([interval, prev_url])
            else:
                merged.append([interval, None])
            
            i = j
        else:
            merged.append([interval, url])
            i += 1
    
    return merged
