import os
import re
import time
from collections.abc import Generator
from typing import Final

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY: Final[str] = os.getenv("GEMINI_API_KEY", "").strip()

MODEL_NAME: Final[str] = os.getenv(
    "GEMINI_MODEL",
    "models/gemini-3.5-flash",
).strip()

client = genai.Client(api_key=API_KEY) if API_KEY else None

ERROR_PREFIX = "AI service unavailable:"


def _friendly_error(message: str) -> str:
    lower = message.lower()

    if (
        "resource_exhausted" in lower
        or "quota" in lower
        or "429" in lower
    ):
        if (
            "perday" in lower
            or "per day" in lower
            or "free_tier_requests" in lower
        ):
            return (
                f"{ERROR_PREFIX} today's free Gemini quota has been used. "
                "Please try again after the quota resets or use a billed "
                "API project."
            )

        return (
            f"{ERROR_PREFIX} Gemini is rate-limiting requests right now. "
            "Please wait a few seconds and try again."
        )

    if (
        "unavailable" in lower
        or "high demand" in lower
        or "503" in lower
    ):
        return (
            f"{ERROR_PREFIX} Gemini is temporarily busy because of high "
            "demand. Please try again in a moment."
        )

    if "not_found" in lower or "404" in lower:
        return (
            f"{ERROR_PREFIX} the configured Gemini model is unavailable. "
            "Check GEMINI_MODEL in the .env file."
        )

    return (
        f"{ERROR_PREFIX} the request could not be completed. "
        "Please try again."
    )


def gemini_failed(text: str) -> bool:
    return (
        not text
        or text.startswith(ERROR_PREFIX)
        or text.startswith("Gemini is not configured")
    )


def _retry_delay_seconds(message: str, attempt: int) -> float:
    match = re.search(
        r"retry(?:Delay| in)\D*(\d+(?:\.\d+)?)",
        message,
        re.IGNORECASE,
    )

    if match:
        return min(float(match.group(1)), 10.0)

    return 1.5 * (attempt + 1)


def ask_gemini(prompt: str, max_attempts: int = 3) -> str:
    """
    Return one complete Gemini response.

    This function is retained because other CareerPilot modules
    still use non-streaming responses.
    """

    if client is None:
        return (
            "Gemini is not configured. Add GEMINI_API_KEY to your "
            ".env file and restart the server."
        )

    last_error = ""

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            text = getattr(response, "text", None)

            if text and text.strip():
                return text.strip()

            last_error = "Gemini returned an empty response."

        except Exception as exc:
            last_error = str(exc)
            lower = last_error.lower()

            daily_quota = (
                "perday" in lower
                or "per day" in lower
                or "free_tier_requests" in lower
            )

            retryable = any(
                token in lower
                for token in (
                    "429",
                    "503",
                    "resource_exhausted",
                    "unavailable",
                    "high demand",
                )
            )

            if (
                daily_quota
                or not retryable
                or attempt == max_attempts - 1
            ):
                break

            time.sleep(_retry_delay_seconds(last_error, attempt))

    return _friendly_error(last_error)


def stream_gemini(
    prompt: str,
    max_attempts: int = 3,
) -> Generator[str, None, None]:
    """
    Yield Gemini response text progressively.

    Each yielded value is sent to the browser immediately through
    FastAPI StreamingResponse.
    """

    if client is None:
        yield (
            "Gemini is not configured. Add GEMINI_API_KEY to your "
            ".env file and restart the server."
        )
        return

    last_error = ""

    for attempt in range(max_attempts):
        produced_output = False

        try:
            response_stream = client.models.generate_content_stream(
                model=MODEL_NAME,
                contents=prompt,
            )

            for chunk in response_stream:
                text = getattr(chunk, "text", None)

                if text:
                    produced_output = True
                    yield text

            if produced_output:
                return

            last_error = "Gemini returned an empty streamed response."

        except Exception as exc:
            last_error = str(exc)
            lower = last_error.lower()

            if produced_output:
                yield (
                    "\n\nThe response was interrupted because the AI "
                    "service became temporarily unavailable."
                )
                return

            daily_quota = (
                "perday" in lower
                or "per day" in lower
                or "free_tier_requests" in lower
            )

            retryable = any(
                token in lower
                for token in (
                    "429",
                    "503",
                    "resource_exhausted",
                    "unavailable",
                    "high demand",
                )
            )

            if (
                daily_quota
                or not retryable
                or attempt == max_attempts - 1
            ):
                break

            time.sleep(_retry_delay_seconds(last_error, attempt))

    yield _friendly_error(last_error)