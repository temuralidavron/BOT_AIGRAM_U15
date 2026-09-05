# ============================================================
#  2-DARS — Mahsulotlar ro'yxati
#  Hozircha baza YO'Q. Oddiy Python lug'ati. 6-darsda Django keladi.
# ============================================================

CATEGORIES = {
    "burger": {
        "nom": "🍔 Burgerlar",
        "mahsulotlar": [
            {"id": 1, "nom": "Klassik burger", "narx": 32000, "tavsif": "Mol go'shti, pishloq, pomidor"},
            {"id": 2, "nom": "Chizburger", "narx": 38000, "tavsif": "Ikki qavat cheddar"},
            {"id": 3, "nom": "Double burger", "narx": 52000, "tavsif": "Ikkita kotlet, bekon"},
        ],
    },
    "pizza": {
        "nom": "🍕 Pitsalar",
        "mahsulotlar": [
            {"id": 4, "nom": "Margarita", "narx": 65000, "tavsif": "Mozzarella, rayhon"},
            {"id": 5, "nom": "Pepperoni", "narx": 85000, "tavsif": "Achchiq kolbasa"},
        ],
    },
    "ichimlik": {
        "nom": "🥤 Ichimliklar",
        "mahsulotlar": [
            {"id": 6, "nom": "Coca-Cola 0.5", "narx": 12000, "tavsif": "Sovutilgan"},
            {"id": 7, "nom": "Suv 0.5", "narx": 5000, "tavsif": "Gazsiz"},
        ],
    },
}


def narx(son: int) -> str:
    """32000 -> '32 000 so'm'"""
    return f"{son:,}".replace(",", " ") + " so'm"


def mahsulot_top(mahsulot_id: int) -> dict | None:
    for kategoriya in CATEGORIES.values():
        for m in kategoriya["mahsulotlar"]:
            if m["id"] == mahsulot_id:
                return m
    return None
