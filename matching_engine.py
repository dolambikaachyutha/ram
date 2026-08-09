BUYERS = [
    {
        "company": "GreenBoard",
        "material": "wood",
        "city": "Bengaluru"
    },
    {
        "company": "EcoWeave",
        "material": "fabric",
        "city": "Mumbai"
    },
    {
        "company": "PaperAgain",
        "material": "paper",
        "city": "Delhi"
    },
    {
        "company": "PlastiReform",
        "material": "plastic",
        "city": "Hyderabad"
    },
    {
        "company": "MetalWorks",
        "material": "metal",
        "city": "Chennai"
    }
]


def find_matches(material):

    matches = []

    material = material.lower()

    for buyer in BUYERS:

        if buyer["material"] in material:
            matches.append(buyer)

    return matches