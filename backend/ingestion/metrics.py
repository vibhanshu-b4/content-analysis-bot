def compute_engagement(likes: int, comments: int, views: int) -> float:
    if views is None or views == 0:
        return 0.0

    return round((likes + comments) / views * 100, 2)


def build_video_summary(data: dict, label: str) -> dict:
    return {
        **data,
        "engagement_rate": compute_engagement(
            data.get("likes", 0),
            data.get("comments", 0),
            data.get("views", 0),
        ),
        "video_id": label,
    }
