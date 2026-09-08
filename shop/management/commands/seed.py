# ============================================================
#  data.py dagi eski lug'atni BAZAGA ko'chiradi.
#  Ishlatish:  python manage.py seed
#
#  Bu buyruq bir marta ishlatiladi — keyin hamma narsa
#  admin panel orqali boshqariladi.
# ============================================================

from decimal import Decimal

from django.core.management.base import BaseCommand

from data import CATEGORIES
from shop.models import Category, Product


class Command(BaseCommand):
    help = "data.py dagi mahsulotlarni bazaga ko'chiradi"

    def handle(self, *args, **options):
        kategoriya_soni = mahsulot_soni = 0

        for tartib, (kalit, kat) in enumerate(CATEGORIES.items(), 1):
            emoji, _, nom = kat["nom"].partition(" ")
            kategoriya, yangi = Category.objects.get_or_create(
                nom=nom or kalit,
                defaults={"emoji": emoji, "tartib": tartib},
            )
            kategoriya_soni += int(yangi)

            for i, m in enumerate(kat["mahsulotlar"], 1):
                _, yaratildi = Product.objects.get_or_create(
                    kategoriya=kategoriya,
                    nom=m["nom"],
                    defaults={
                        "tavsif": m["tavsif"],
                        "narx": Decimal(m["narx"]),
                        "tartib": i,
                    },
                )
                mahsulot_soni += int(yaratildi)

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: +{kategoriya_soni} kategoriya, +{mahsulot_soni} mahsulot.\n"
            f"Bazada jami: {Category.objects.count()} kategoriya, "
            f"{Product.objects.count()} mahsulot."
        ))
