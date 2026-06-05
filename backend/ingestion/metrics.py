from datetime import datetime

def compute_engagement(likes: int, comments: int, views: int) -> float:
    if views and views > 0:
        return round((likes + comments) / views * 100, 2)
    return 0.0

def parse_upload_date(date_str: str) -> str:
    if not date_str:
        return "Unknown"
    try:
        dt = datetime.strptime(str(date_str), "%Y%m%d")
        return dt.strftime("%B %d, %Y")
    except:
        return str(date_str)

def days_since_upload(date_str: str) -> int:
    if not date_str:
        return 0
    try:
        dt = datetime.strptime(str(date_str), "%Y%m%d")
        return (datetime.now() - dt).days
    except:
        return 0

def build_video_summary(data: dict, label: str) -> dict:
    likes = int(data.get("likes") or 0)
    comments = int(data.get("comments") or 0)
    views = int(data.get("views") or 0)
    date_str = data.get("upload_date", "")

    data["engagement_rate"] = compute_engagement(likes, comments, views)
    data["likes_plus_comments"] = likes + comments
    data["upload_date_formatted"] = parse_upload_date(date_str)
    data["days_since_upload"] = days_since_upload(date_str)

    days = days_since_upload(date_str)
    data["daily_interactions"] = round(
        (likes + comments) / days, 1
    ) if days > 0 else 0

    data["video_id"] = label
    return data