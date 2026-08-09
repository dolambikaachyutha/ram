PRICE_DB = {
    "wood": 10,
    "fabric": 18,
    "plastic": 15,
    "paper": 8,
    "metal": 25
}

def get_price(material):

    material = material.lower()

    for key in PRICE_DB:
        if key in material:
            return PRICE_DB[key]

    return 5