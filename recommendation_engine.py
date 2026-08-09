from engine.carbon_engine import carbon_saved
from engine.matching_engine import find_matches, BUYERS

TRANSPORT_GUIDE = {
    "wood": "Flatbed truck",
    "metal": "Flatbed truck",
    "plastic": "Van or small truck",
    "paper": "Van or small truck",
    "fabric": "Courier or van"
}


def predict_demand(material):

    matches = find_matches(material)

    demand_ratio = len(matches) / len(BUYERS) if BUYERS else 0

    if demand_ratio >= 0.4:
        level = "High"
    elif demand_ratio > 0:
        level = "Moderate"
    else:
        level = "Low"

    return {"level": level, "interested_buyers": len(matches)}


def calculate_circularity_score(data):

    material = data.get("material", "")
    quantity = data.get("quantity", 0)

    co2 = carbon_saved(material, quantity)
    demand = predict_demand(material)

    score = 0
    score += min(co2 / 10, 40)
    score += {"High": 40, "Moderate": 20, "Low": 5}.get(demand["level"], 0)
    score += 20 if demand["interested_buyers"] > 0 else 0

    return round(min(score, 100), 1)


def estimate_co2_savings(material, qty):

    return carbon_saved(material, qty)


def suggest_nearest_buyers(material, city):

    matches = find_matches(material)

    same_city = [buyer for buyer in matches if buyer.get("city", "").lower() == city.lower()]

    return same_city if same_city else matches


def recommend_transport_method(material):

    material = material.lower()

    for key, method in TRANSPORT_GUIDE.items():
        if key in material:
            return method

    return "Van or small truck"