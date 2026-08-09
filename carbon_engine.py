CARBON_FACTORS = {
    "wood": 0.45,
    "plastic": 1.8,
    "paper": 1.2,
    "fabric": 2.0,
    "metal": 1.5
}

def carbon_saved(material, quantity):

    material = material.lower()

    factor = 0.5

    for key in CARBON_FACTORS:
        if key in material:
            factor = CARBON_FACTORS[key]

    return quantity * factor