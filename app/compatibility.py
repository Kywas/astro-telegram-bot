def compatibility_summary(locale: str, score: int, *, style: str = "terms", mode: str = "love") -> str:
    from app.reading_voice import compatibility_summary_engaging

    return compatibility_summary_engaging(locale, score, style=style, mode=mode)
