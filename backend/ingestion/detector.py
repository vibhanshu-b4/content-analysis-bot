def detect_platform(url: str) -> str:
    url = url.lower()
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "instagram.com" in url:
        return "instagram"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "twitter.com" in url or "x.com" in url:
        return "twitter"
    else:
        return "unknown"

def get_video_data(url: str) -> dict:
    platform = detect_platform(url)
    
    if platform == "youtube":
        from ingestion.youtube import get_youtube_data
        return get_youtube_data(url)
    
    elif platform == "instagram":
        from ingestion.instagram import get_instagram_data
        return get_instagram_data(url)
    
    else:
        raise ValueError(f"Unsupported platform for URL: {url}")
    
    