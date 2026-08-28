from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_produtos, name="lista_produtos"),
    path("produto/<int:produto_id>/", views.detalhe_produto, name="detalhe_produto"),
    path("produto/novo/", views.criar_produto, name="criar_produto"),
    path("categorias/", views.categorias, name="categorias"),
    path("produtos/cbv/", views.ProdutoListView.as_view(), name="produtos_cbv"),
]