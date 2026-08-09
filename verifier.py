from engine.llm_client import ask_ai
from engine.price_engine import PRICE_DB

MODERATION_PROMPT = """You are a content moderator for a circular economy waste marketplace.

Listing: "{listing_text}"

Decide if this looks like a genuine waste material listing, or if it looks like spam, a scam,
or an unsafe/hazardous/illegal material. Respond with ONLY one word: APPROVED or REJECTED."""


def verify_listing(listing_text, material=None, quantity=None):

    issues = []

    if not listing_text or len(listing_text.strip()) < 5:
        issues.append("Listing text is too short or missing.")

    if quantity is not None and quantity <= 0:
        issues.append("Quantity must be greater than zero.")

    if material and not any(key in material.lower() for key in PRICE_DB):
        issues.append("Material type could not be confidently recognized.")

    if issues:
        return {"status": "rejected", "reasons": issues}

    prompt = MODERATION_PROMPT.format(listing_text=listing_text)

    verdict = ask_ai(prompt).strip().upper()

    if "REJECT" in verdict:
        return {"status": "rejected", "reasons": ["Flagged by AI moderation as spam, unsafe, or not a genuine listing."]}

    return {"status": "approved", "reasons": []}