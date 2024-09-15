from utility.captions.timed_captions_generator import generate_timed_captions
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a topic.")
    parser.add_argument("audioFile", type=str, help="The audio file")

    args = parser.parse_args()
    AUDIO_FILE = args.audioFile
    captions = generate_timed_captions(AUDIO_FILE)

    with open("output.vtt", "w", encoding="utf-8") as file:
        for caption in captions:
            file.write(caption[1] + " ") 