import edge_tts

async def generate_audio(text,outputFilename, language):
    lang = 'en-AU-WilliamNeural'
    if (language == "Indonesian-Female"):
        lang = "id-ID-GadisNeural"
    if (language == "Indonesian-Male"):
        lang = "id-ID-ArdiNeural"
    if (language == "English-Female"):
        lang = "en-US-AriaNeural"
    communicate = edge_tts.Communicate(text,lang)
    await communicate.save(outputFilename)