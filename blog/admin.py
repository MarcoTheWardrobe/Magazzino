from django.contrib import admin

from .models import MovimentoProdotto, MovimentoProdottoInline, Prodotto

admin.site.register(Prodotto, MovimentoProdottoInline, MovimentoProdotto)
