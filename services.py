# ============================================================
#  7-DARS — SERVIS QATLAMI
#
#  Bu — bot bilan baza orasidagi YAGONA ko'prik.
#  Handler hech qachon to'g'ridan-to'g'ri Product.objects ga tegmaydi.
#
#  IKKI QOIDA:
#   1. Har bir funksiya @sync_to_async bilan o'ralgan
#   2. Har bir funksiya dict qaytaradi, model obyektini EMAS
# ============================================================

from asgiref.sync import sync_to_async

from shop.models import Category, Product


def narx(son) -> str:
    """Decimal(32000) -> '32 000 so'm'"""
    return f"{int(son):,}".replace(",", " ") + " so'm"


def _kategoriya_dict(k: Category) -> dict:
    return {"id": k.pk, "nom": k.nom, "emoji": k.emoji,
            "toliq_nom": f"{k.emoji} {k.nom}".strip()}


def _mahsulot_dict(m: Product) -> dict:
    return {"id": m.pk, "nom": m.nom, "tavsif": m.tavsif,
            "narx": int(m.narx), "kategoriya_id": m.kategoriya_id}


@sync_to_async
def kategoriyalar() -> list[dict]:
    """Faqat ichida mahsuloti bor kategoriyalar."""
    qs = Category.objects.filter(faol=True, mahsulotlar__faol=True).distinct()
    return [_kategoriya_dict(k) for k in qs]


@sync_to_async
def kategoriya_top(kategoriya_id: int) -> dict | None:
    k = Category.objects.filter(pk=kategoriya_id, faol=True).first()
    return _kategoriya_dict(k) if k else None


@sync_to_async
def mahsulotlar(kategoriya_id: int) -> list[dict]:
    qs = Product.objects.filter(kategoriya_id=kategoriya_id, faol=True)
    return [_mahsulot_dict(m) for m in qs]


@sync_to_async
def mahsulot_top(mahsulot_id: int) -> dict | None:
    m = Product.objects.filter(pk=mahsulot_id, faol=True).first()
    return _mahsulot_dict(m) if m else None


@sync_to_async
def mahsulotlar_by_ids(idlar: list[int]) -> dict[int, dict]:
    """Savat uchun: {id: mahsulot_dict} ko'rinishida qaytaradi."""
    qs = Product.objects.filter(pk__in=idlar, faol=True)
    return {m.pk: _mahsulot_dict(m) for m in qs}
