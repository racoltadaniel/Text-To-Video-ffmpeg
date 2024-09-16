import os 
import requests
from utility.utils import log_response,LOG_TYPE_PEXEL
import logging
import utility.logger_config

PEXELS_API_KEY = ''
def read_api_key(file_path):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('pexels_api_key='):
                    return line.split('=', 1)[1].strip()
    except FileNotFoundError:
        logging.error(f"Properties file not found: {file_path}")
    except Exception as e:
        logging.error(f"Error reading properties file: {e}")
    return None

api_key = read_api_key('/etc/properties/videogen.properties')
if api_key:
    PEXELS_API_KEY=api_key
else:
    raise ValueError("API key is not available. Please check the properties file.")

def search_videos(query_string, orientation_landscape=False):
   
    if not PEXELS_API_KEY:
        raise ValueError("PEXELS API key is missing. Please provide a valid API key.")
   
    url = "https://api.pexels.com/videos/search"
    headers = {
        "Authorization": PEXELS_API_KEY,
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    }
    params = {
        "query": query_string,
        "orientation": "landscape" if orientation_landscape else "portrait",
        "per_page": 15,
        "size": "medium"
    }
    logging.debug(f"Url: {url}, Headers: {headers}, Params: {params}")
    response = requests.get(url, headers=headers, params=params)
    logging.debug(f"Response: {response}")
    json_data = response.json()
    log_response(LOG_TYPE_PEXEL,query_string,response.json())
   
    return json_data


def getBestVideo(query_string, orientation_landscape=True, used_vids=[]):
    vids = None
    try:
        vids = search_videos(query_string, orientation_landscape)
    except Exception as e:
        logging.error(f"Error searching videos: {e}")
        return None
    videos = vids['videos']  # Extract the videos list from JSON

    # Filter and extract videos with width and height as 1920x1080 for landscape or 1080x1920 for portrait
    if orientation_landscape:
        filtered_videos = [video for video in videos if video['width'] >= 1920 and video['height'] >= 1080 and video['width']/video['height'] == 16/9]
    else:
        filtered_videos = [video for video in videos if video['width'] >= 1080 and video['height'] >= 1920 and video['height']/video['width'] == 16/9]

    # Sort the filtered videos by duration in ascending order
    sorted_videos = sorted(filtered_videos, key=lambda x: abs(15-int(x['duration'])))

    # Extract the top 3 videos' URLs
    for video in sorted_videos:
        for video_file in video['video_files']:
            if orientation_landscape:
                if video_file['width'] == 1920 and video_file['height'] == 1080:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        return video_file['link']
            else:
                if video_file['width'] == 1080 and video_file['height'] == 1920:
                    if not (video_file['link'].split('.hd')[0] in used_vids):
                        return video_file['link']
    logging.error("NO LINKS found for this round of search with query :%s", query_string)
    return None


def generate_video_url(timed_video_searches,video_server):
        timed_video_urls = []
        if video_server == "pexel":
            used_links = []
            for (t1, t2), search_terms in timed_video_searches:
                url = ""
                for query in search_terms:
                  
                    url = getBestVideo(query, orientation_landscape=False, used_vids=used_links)
                    if url:
                        used_links.append(url.split('.hd')[0])
                        break
                timed_video_urls.append([[t1, t2], url])
        elif video_server == "stable_diffusion":
            timed_video_urls = get_images_for_video(timed_video_searches)

        return timed_video_urls
