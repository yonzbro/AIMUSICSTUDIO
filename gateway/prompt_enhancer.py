"""
AI-Powered Prompt Enhancer — Gateway
Uses Qwen2 (via lyrics-service) to intelligently enhance user prompts,
generate song titles, and detect genres.
"""

import httpx
import os

LYRICS_SERVICE_URL = os.getenv("LYRICS_SERVICE_URL", "http://localhost:8001")

# ── System Prompts ───────────────────────────────────────────────

ENHANCE_SYSTEM = (
    "You are a professional music producer and creative director. "
    "The user gives you a short song idea. Your job is to expand it into a "
    "detailed, vivid music production prompt that will help an AI generate better music. "
    "Include mood, instruments, tempo hints, and atmosphere. "
    "Output ONLY the enhanced prompt, nothing else. Keep it under 100 words."
)

TITLE_SYSTEM = (
    "You are a creative songwriter. Given a song description and style, "
    "generate a catchy, memorable song title. "
    "Output ONLY the title, nothing else. No quotes, no punctuation, no explanation."
)

GENRE_SYSTEM = (
    "You are a music genre classifier. Given a text description, identify the most "
    "fitting music genre/style from this list: "
    "Deep House, House, Trap, Chill, Electronic, Lo-Fi, Ambient, Hip-Hop, Pop, "
    "R&B, Jazz, Classical, Rock, Metal, Reggaeton, Afrobeat, Funk, Soul, Country, Folk. "
    "Output ONLY the genre name, nothing else."
)


async def _call_qwen(system_prompt: str, user_message: str, timeout: float = 30.0) -> str:
    """
    Send a chat-completion-style request to the lyrics service's Qwen2 model.
    Uses the /generate-lyrics endpoint with a custom system prompt.
    """
    # We construct a combined prompt since lyrics-service expects a simple prompt
    combined = f"[SYSTEM] {system_prompt}\n[USER] {user_message}"

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            resp = await client.post(
                f"{LYRICS_SERVICE_URL}/generate-lyrics",
                json={"prompt": combined},
            )
            if resp.status_code == 200:
                result = resp.json().get("lyrics", "").strip()
                # Clean up any residual formatting
                result = result.replace("[SYSTEM]", "").replace("[USER]", "").strip()
                return result
            else:
                print(f"[Enhancer] Qwen2 returned {resp.status_code}")
                return ""
        except Exception as e:
            print(f"[Enhancer] Qwen2 call failed: {e}")
            return ""


async def enhance_prompt(raw_prompt: str, style: str = "", language: str = "en") -> str:
    """
    Take a user's raw, possibly short prompt and expand it into a
    detailed music production prompt using Qwen2.
    """
    user_msg = f"Style: {style}\nLanguage: {language}\nIdea: {raw_prompt}"
    enhanced = await _call_qwen(ENHANCE_SYSTEM, user_msg)

    if not enhanced or len(enhanced) < 10:
        # Fallback: return original prompt if enhancement failed
        print("[Enhancer] Enhancement failed, using original prompt.")
        return raw_prompt

    print(f"[Enhancer] '{raw_prompt[:40]}...' → '{enhanced[:60]}...'")
    return enhanced


async def generate_song_title(prompt: str, style: str = "") -> str:
    """Generate a creative song title based on the prompt and style."""
    user_msg = f"Style: {style}\nDescription: {prompt}"
    title = await _call_qwen(TITLE_SYSTEM, user_msg, timeout=15.0)

    if not title or len(title) < 2:
        # Fallback: create a simple title from the first words
        words = prompt.split()[:3]
        title = " ".join(words).title()
        print(f"[Enhancer] Title generation failed, using fallback: {title}")

    # Clean up: remove quotes, limit length
    title = title.strip('"\'').strip()[:60]
    print(f"[Enhancer] Generated title: {title}")
    return title


async def detect_genre(prompt: str) -> str:
    """Auto-detect the best matching genre from a text description."""
    genre = await _call_qwen(GENRE_SYSTEM, prompt, timeout=10.0)

    if not genre or len(genre) < 2:
        genre = "Electronic"  # Safe fallback
        print(f"[Enhancer] Genre detection failed, using fallback: {genre}")

    print(f"[Enhancer] Detected genre: {genre}")
    return genre
