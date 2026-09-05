# ============================================================
#  Savat — hozircha XOTIRADA (oddiy lug'at).
#  Bot o'chsa — yo'qoladi. 8-darsda bazaga ko'chiramiz.
#
#  Struktura:  {user_id: {product_id: soni}}
# ============================================================

from data import mahsulot_top

_SAVATLAR: dict[int, dict[int, int]] = {}


def qoshish(user_id: int, product_id: int, soni: int = 1) -> int:
    savat = _SAVATLAR.setdefault(user_id, {})
    savat[product_id] = savat.get(product_id, 0) + soni
    return savat[product_id]


def ozgartirish(user_id: int, product_id: int, farq: int) -> int:
    savat = _SAVATLAR.setdefault(user_id, {})
    yangi = savat.get(product_id, 0) + farq
    if yangi < 1:
        savat.pop(product_id, None)
        return 0
    savat[product_id] = yangi
    return yangi


def ochirish(user_id: int, product_id: int) -> None:
    _SAVATLAR.get(user_id, {}).pop(product_id, None)


def tozalash(user_id: int) -> None:
    _SAVATLAR.pop(user_id, None)


def olish(user_id: int) -> list[dict]:
    """[{'id':1,'nom':'...','narx':32000,'soni':2,'summa':64000}, ...]"""
    natija = []
    for product_id, soni in _SAVATLAR.get(user_id, {}).items():
        m = mahsulot_top(product_id)
        if m:
            natija.append({**m, "soni": soni, "summa": m["narx"] * soni})
    return natija


def jami(user_id: int) -> int:
    return sum(x["summa"] for x in olish(user_id))


def dona(user_id: int) -> int:
    return sum(_SAVATLAR.get(user_id, {}).values())
