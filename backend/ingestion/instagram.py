import os

import yt_dlp


def download_audio(video_url: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "/tmp/ig_audio.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    for filename in os.listdir("/tmp"):
        if filename.startswith("ig_audio"):
            return os.path.join("/tmp", filename)

    raise ValueError("No downloaded audio file found")


def get_transcript(audio_path: str) -> str:
    try:
        import whisper
        import os
        model = whisper.load_model("small")

        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        _, probs = model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)
        print(f"Detected language: {detected_lang}")

        if detected_lang == "en":
            # English — just transcribe normally
            result = model.transcribe(audio_path, task="transcribe")
        else:
            # Non-English — translate to English for better RAG quality
            print(f"Non-English detected ({detected_lang}), translating to English...")
            result = model.transcribe(
                audio_path,
                task="translate",  # this translates to English
                language=detected_lang
            )

        transcript = result["text"].strip()
        print(f"Transcript preview: {transcript[:100]}")
        os.remove(audio_path)
        return transcript

    except Exception as e:
        raise ValueError(str(e))


def get_metadata(video_url: str) -> dict:
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        info = ydl.extract_info(video_url, download=False)

    return {
        "title": info.get("title", "Unknown"),
        "views": info.get("view_count", 0),
        "likes": info.get("like_count", 0),
        "comments": info.get("comment_count", 0),
        "creator": info.get("uploader", "Unknown"),
        "followers": info.get("channel_follower_count", None),
        "upload_date": info.get("upload_date", None),
        "duration": info.get("duration", 0),
        "hashtags": info.get("tags", []),
    }


def get_instagram_data(video_url: str) -> dict:
    metadata = get_metadata(video_url)
    audio_path = download_audio(video_url)
    transcript = get_transcript(audio_path)

    return {
        **metadata,
        "transcript": transcript,
        "source_url": video_url,
        "platform": "instagram",
    }
