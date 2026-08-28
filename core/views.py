from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import CategoriaForm, ProdutoForm
from .models import Categoria, Produto


def lista_produtos(request):
	produtos = Produto.objects.select_related("categoria").order_by("nome")
	return render(request, "core/lista_produtos.html", {"produtos": produtos})


def detalhe_produto(request, produto_id):
	produto = get_object_or_404(Produto, pk=produto_id)
	return render(request, "core/detalhe_produto.html", {"produto": produto})


def criar_produto(request):
	form = ProdutoForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		form.save()
		return redirect("lista_produtos")
	return render(request, "core/form_produto.html", {"form": form})


def categorias(request):
	form = CategoriaForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		form.save()
		return redirect("categorias")
	return render(
		request,
		"core/categorias.html",
		{"form": form, "categorias": Categoria.objects.order_by("nome")},
	)


class ProdutoListView(ListView):
	model = Produto
	template_name = "core/lista_produtos.html"
	context_object_name = "produtos"
	ordering = ["nome"]
