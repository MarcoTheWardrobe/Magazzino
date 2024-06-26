from django.conf import settings
from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.utils.html import format_html


class Prodotto(models.Model):
    class Meta:
        verbose_name = "Prodotto a Catalogo"
        verbose_name_plural = "Prodotti a Catalogo"
        ordering = [
            "nome",
        ]

    ts_created = models.DateTimeField(auto_now_add=True, verbose_name="Inserimento")
    ts = models.DateTimeField(auto_now=True, verbose_name="Ultima Modifica")
    is_attivo = models.BooleanField(default=True, verbose_name="E' Attivo?")
    codice = models.CharField(max_length=128, unique=True)
    nome = models.CharField(max_length=1024)
    descrizione = models.TextField(null=True, blank=True)

    def get_totale_magazzino(self):
        tot_prelievo = sum(
            [m.quantita for m in self.movimentoprodotto_set.filter(azione="prelievo")]
        )
        tot_deposito = sum(
            [m.quantita for m in self.movimentoprodotto_set.filter(azione="deposito")]
        )
        return tot_deposito - tot_prelievo

    @admin.display(description="QTA Magazzino")
    def admin_quantita_magazzino(self):
        tot = self.get_totale_magazzino()
        if tot > 0:
            return format_html(
                '<strong><span style="color: green">{}</span></strong>', tot
            )
        else:
            return format_html(
                '<strong><span style="color: red">{}</span></strong>', tot * -1
            )

    def save(self, *args, **kwargs):
        if bool(self.nome):
            self.nome = self.nome.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Prodotto a Catalogo: {}".format(self.nome)


class MovimentoProdotto(models.Model):
    class Meta:
        verbose_name = "Movimento Prodotto"
        verbose_name_plural = "Movimento Prodotti"
        ordering = [
            "-ts",
        ]

    ts_created = models.DateTimeField(auto_now_add=True, verbose_name="Inserimento")
    ts = models.DateTimeField(auto_now=True, verbose_name="Ultima Modifica")
    prodotto = models.ForeignKey("Prodotto", on_delete=models.CASCADE)
    azione = models.CharField(
        max_length=128,
        default="deposito",
        choices=(("prelievo", "Prelievo"), ("deposito", "Deposito")),
    )
    quantita = models.PositiveIntegerField(default=0)
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return "Movimento di {} | {} di {}".format(
            self.prodotto.nome, self.get_azione_display(), self.quantita
        )


class MovimentoProdottoInline(admin.StackedInline):
    model = MovimentoProdotto
    extra = 0
    # Sarebbero tutti da mettere read only
    # readonly_fields = []


@admin.register(Prodotto)
class ProdottoAdmin(admin.ModelAdmin):
    list_display = ["nome", "codice", "is_attivo", "admin_quantita_magazzino"]
    search_fields = ["nome", "codice"]
    inlines = [MovimentoProdottoInline]
