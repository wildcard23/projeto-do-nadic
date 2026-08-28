from django import forms

from .models import Categoria, Produto


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome"]


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "preco", "categoria"]
        labels = {
            "nome": "Nome do produto",
            "preco": "Preço",
            "categoria": "Material",
        }
        widgets = {
            "categoria": forms.Select(
                attrs={"title": "Escolha o material do produto"}
            ),
        }

    def clean_preco(self):
        preco = self.cleaned_data["preco"]
        if preco <= 0:
            raise forms.ValidationError("O preço deve ser maior que zero.")
        return preco