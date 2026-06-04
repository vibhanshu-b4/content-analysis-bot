from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp


def get_transcript(video_url: str) -> str:
    try:
        if "youtu.be/" in video_url:
            video_id = video_url.split("youtu.be/", 1)[1].split("?", 1)[0].split("&", 1)[0].split("/", 1)[0]
        else:
            video_id = video_url.split("v=", 1)[1].split("&", 1)[0].split("#", 1)[0]

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry["text"] for entry in transcript)
    except Exception as e:
        raise ValueError(f"Could not get transcript: {str(e)}")


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


def get_youtube_data(video_url: str) -> dict:
    try:
        transcript = get_transcript(video_url)
        metadata = get_metadata(video_url)
        return {
            **metadata,
            "transcript": transcript,
            "source_url": video_url,
            "platform": "youtube",
        }
    except Exception as e:
        raise ValueError(str(e))
