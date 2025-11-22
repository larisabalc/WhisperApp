import whisper

def transcribe(audio_path):
    model = whisper.load_model("small")
    result = model.transcribe(audio_path, word_timestamps=True)
    
    return result

def translate(media_path):
    model = whisper.load_model("small")
    
    result = model.transcribe(media_path, word_timestamps=True, task="translate")
    
    return result