from django.contrib import admin
from .models import Categoria, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
	search_fields = ["nome"]


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
	list_display = ["nome", "preco", "categoria", "criado_em"]
	list_filter = ["categoria"]
	search_fields = ["nome"]
	list_select_related = ["categoria"]
