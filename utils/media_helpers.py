import base64

def media_to_base64(media_path: str) -> str:
    with open(media_path, "rb") as f:
        data = f.read()
    ext = media_path.split(".")[-1].lower()
    video_exts = ["mp4", "mkv", "mov"]
    audio_exts = ["mp3", "wav", "m4a"]
    if ext in video_exts:
        mime = f"video/{ext if ext!='mkv' else 'mp4'}"
    elif ext in audio_exts:
        mime = "audio/mpeg"
    else:
        mime = "video/mp4"
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"
