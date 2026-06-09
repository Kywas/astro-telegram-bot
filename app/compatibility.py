def compatibility_summary(locale: str, score: int) -> str:
    if locale == "ru":
        if score >= 85:
            return "Общий фон: очень высокая совместимость по натальным аспектам."
        if score >= 70:
            return "Общий фон: хорошая совместимость — много поддерживающих связей."
        if score >= 55:
            return "Общий фон: средняя совместимость — есть и гармония, и точки роста."
        return "Общий фон: непростая синастрия — потребуются терпение и диалог."

    if score >= 85:
        return "Overall: very high compatibility by natal aspects."
    if score >= 70:
        return "Overall: good compatibility with many supportive links."
    if score >= 55:
        return "Overall: moderate compatibility — harmony and growth points mix."
    return "Overall: challenging synastry — patience and dialogue will matter."
