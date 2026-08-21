from src.core.settings import settings


class AIServiceError(Exception):
    pass


def generate_ai_response(
    user_message: str,
) -> str:
    engine = settings.AI_ENGINE.strip().lower()

    if engine in {
        "mock",
        "development",
        "dev",
    }:
        return "NEXUS development AI received your message: " f"{user_message}"

    raise AIServiceError("AI engine is not configured.")
