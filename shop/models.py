# ============================================================
#  6-DARS — Django modellari
#
#  data.py dagi lug'at endi BAZA jadvaliga aylanadi.
#
#  Har bir class  -> bitta jadval
#  Har bir field  -> bitta ustun
# ============================================================

from django.db import models


class Category(models.Model):
    nom = models.CharField("Nomi", max_length=120, unique=True)
    emoji = models.CharField("Emoji", max_length=8, blank=True, default="")
    tartib = models.PositiveIntegerField("Tartib", default=0)
    faol = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ("tartib", "nom")

    def __str__(self):
        return f"{self.emoji} {self.nom}".strip()


class Product(models.Model):
    kategoriya = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="mahsulotlar",
        verbose_name="Kategoriya",
    )
    nom = models.CharField("Nomi", max_length=180)
    tavsif = models.TextField("Tavsif", blank=True, default="")
    narx = models.DecimalField("Narx", max_digits=12, decimal_places=2)
    faol = models.BooleanField("Faol", default=True)
    tartib = models.PositiveIntegerField("Tartib", default=0)
    yaratilgan = models.DateTimeField("Yaratilgan", auto_now_add=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ("tartib", "nom")

    def __str__(self):
        return self.nom
