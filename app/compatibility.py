def compatibility_summary(locale: str, score: int, *, style: str = "terms") -> str:
    from app.reading_voice import compatibility_summary_engaging

    return compatibility_summary_engaging(locale, score, style=style)
