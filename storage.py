# ============================================================
#  7-DARS — Savat endi FAQAT id va sonini saqlaydi.
#
#  Oldin: savat mahsulot nomini ham bilardi (data.py dan).
#  Endi:  savat faqat {mahsulot_id: soni} biladi.
#         Nom va narxni handler servisdan oladi.
#
#  Nima uchun: savat bazani bilmasligi kerak. Uning vazifasi —
#  "kim nimadan nechta olgan" ni eslash, boshqa hech nima.
#
#  (Hali xotirada. 8-darsda bazaga ko'chiramiz.)
# ============================================================

_SAVATLAR: dict[int, dict[int, int]] = {}


def qoshish(user_id: int, mahsulot_id: int, soni: int = 1) -> int:
    savat = _SAVATLAR.setdefault(user_id, {})
    savat[mahsulot_id] = savat.get(mahsulot_id, 0) + soni
    return savat[mahsulot_id]


def ozgartirish(user_id: int, mahsulot_id: int, farq: int) -> int:
    savat = _SAVATLAR.setdefault(user_id, {})
    yangi = savat.get(mahsulot_id, 0) + farq
    if yangi < 1:
        savat.pop(mahsulot_id, None)
        return 0
    savat[mahsulot_id] = yangi
    return yangi


def ochirish(user_id: int, mahsulot_id: int) -> None:
    _SAVATLAR.get(user_id, {}).pop(mahsulot_id, None)


def tozalash(user_id: int) -> None:
    _SAVATLAR.pop(user_id, None)


def xom(user_id: int) -> dict[int, int]:
    """{mahsulot_id: soni} — tayyorlanmagan holda."""
    return dict(_SAVATLAR.get(user_id, {}))


def soni(user_id: int, mahsulot_id: int) -> int:
    return _SAVATLAR.get(user_id, {}).get(mahsulot_id, 0)


def dona(user_id: int) -> int:
    return sum(_SAVATLAR.get(user_id, {}).values())
