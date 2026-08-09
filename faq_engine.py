from engine.llm_client import ask_ai

PLATFORM_CONTEXT = """You are the support assistant for an AI-driven circular economy marketplace.
Companies list waste materials (wood scraps, excess fabric, plastic offcuts, paper, metal) and the
platform's AI reads each listing and matches it with companies that can use that material as a raw
input. The platform also estimates a suggested price and CO2 savings for each listing.

Answer the user's question about the platform clearly, in 2-4 sentences.
"""

PRESET_FAQS = {
    "how does matching work": "Our AI reads the text of each waste listing, identifies the material type, and matches it against companies registered as buyers of that material.",
    "how is price calculated": "We estimate a suggested price from a base rate per material type, which can be adjusted for quantity and condition.",
    "how is co2 calculated": "CO2 savings are estimated using standard emission factors per material type, multiplied by the quantity being diverted from landfill.",
    "is listing free": "Yes, listing your waste materials is free. We may add an optional fee once a match turns into a completed transaction."
}


def answer_faq(question):

    normalized = question.lower().strip().strip("?")

    for key, answer in PRESET_FAQS.items():
        if key in normalized or normalized in key:
            return answer

    prompt = PLATFORM_CONTEXT + f"\nUser question: {question}\nAnswer:"

    return ask_ai(prompt)