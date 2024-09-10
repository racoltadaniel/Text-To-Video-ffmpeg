import edge_tts

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
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

    with open("test.vtt", "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs())
