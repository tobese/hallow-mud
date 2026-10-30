"""
Pictures for the web client in one style, painted by Gemini's image model.

LlamaTale shows <name>.jpg for an NPC or location, named in lower case with spaces as
underscores: portraits at 512x512, rooms at 512x320.
"""
import base64
import io
import os
import time

import requests
from PIL import Image

MODEL = "gemini-3.1-flash-image"

STYLE = ("A hand-tinted 1870s tintype photograph, Swedish immigrant shantytown Swede Hollow in Saint Paul, "
         "All Hallows' Eve night with fog and lantern light. Muted palette of deep forest green, pine, sage and "
         "bone-white, with warm lantern-gold highlights and small touches of blood red. Grainy, eerie, atmospheric. "
         "No text, no lettering, no border, no frame.")
PORTRAIT = "Head-and-shoulders portrait, centred, looking at the viewer, dark misty background. "
ROOM = "Wide establishing shot, no people. "
PORTRAIT_SIZE = (512, 512)
ROOM_SIZE = (512, 320)


def file_name(name: str) -> str:
    """The file LlamaTale looks for when showing this NPC or location."""
    return name.strip().replace(" ", "_").lower() + ".jpg"


def paint(subject: str, aspect: str, size: tuple, api_key: str = "", attempts: int = 4) -> Image.Image:
    api_key = api_key or os.environ["GEMINI_API_KEY"]
    for attempt in range(attempts):
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
            headers={"x-goog-api-key": api_key},
            json={"contents": [{"parts": [{"text": f"{subject} {STYLE}"}]}],
                  "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}},
            timeout=300)
        # the image model is often briefly overloaded
        if response.status_code not in (429, 500, 503) or attempt == attempts - 1:
            break
        time.sleep(10 * (attempt + 1))
    response.raise_for_status()
    for part in response.json()["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            image = Image.open(io.BytesIO(base64.b64decode(part["inlineData"]["data"]))).convert("RGB")
            return fit(image, *size)
    raise RuntimeError("no image in the response")


def paint_portrait(who: str, api_key: str = "", attempts: int = 4) -> Image.Image:
    return paint(PORTRAIT + who, "1:1", PORTRAIT_SIZE, api_key, attempts)


def paint_room(what: str, api_key: str = "", attempts: int = 4) -> Image.Image:
    return paint(ROOM + what, "16:9", ROOM_SIZE, api_key, attempts)


def fit(image: Image.Image, width: int, height: int) -> Image.Image:
    """Scale to cover width x height and crop the middle."""
    scale = max(width / image.width, height / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    left, top = (image.width - width) // 2, (image.height - height) // 2
    return image.crop((left, top, left + width, top + height))
