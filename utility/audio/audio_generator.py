import edge_tts
import logging
import utility.logger_config

async def generate_audio(text,outputFilename, language):
    lang = 'en-AU-WilliamNeural'
    if (language == "Indonesian-Female"):
        lang = "id-ID-GadisNeural"
    if (language == "Indonesian-Male"):
        lang = "id-ID-ArdiNeural"
    if (language == "English-Female"):
        lang = "en-US-AriaNeural"

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
        
