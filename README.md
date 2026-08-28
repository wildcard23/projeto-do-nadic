# Django do zero

Guia prático dos fundamentos do Django, usando um projeto chamado `config` e um app chamado `core`.

## 1. Configuração inicial

```bash
python3 -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate       # Windows
python -m pip install --upgrade pip
python -m pip install django

django-admin startproject config .
python manage.py startapp core
python manage.py runserver
```

Abra `http://127.0.0.1:8000/`. Adicione o app em `config/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "core",
]
```

## 2. Estrutura MTV

O Django separa responsabilidades no padrão MTV:

- **Model**: representa os dados e regras de persistência.
- **Template**: apresenta os dados em HTML.
- **View**: recebe a requisição, executa a lógica e devolve uma resposta.

Estrutura essencial:

```text
config/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── core/
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    └── templates/core/
```

`manage.py` executa comandos administrativos; `config/settings.py` concentra configurações; `config/urls.py` encaminha rotas; o app reúne uma funcionalidade do domínio.

## 3. URLs e rotas

Em `core/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_produtos, name="lista_produtos"),
    path("produto/<int:produto_id>/", views.detalhe_produto, name="detalhe_produto"),
]
```

Inclua as rotas do app em `config/urls.py`:

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]
```

`<int:produto_id>` captura um inteiro e o entrega à view. Outros conversores comuns são `str`, `slug`, `uuid` e `path`.

## 4. Models

Em `core/models.py`:

```python
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=120)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
    )
    relacionados = models.ManyToManyField("self", blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
```

`CharField` armazena texto limitado, `DecimalField` valores decimais, `DateTimeField` datas e horas. `ForeignKey` cria uma relação muitos-para-um; `ManyToManyField` permite vários registros em ambos os lados. `PROTECT` impede apagar uma categoria que ainda tenha produtos.

Crie e aplique as migrações:

```bash
python manage.py makemigrations
python manage.py migrate
```

Migrações versionam alterações do model e sincronizam o schema do banco. Não edite migrações já aplicadas sem entender o impacto nos dados.

## 5. Views

### Function-Based View (FBV)

Em `core/views.py`:

```python
from django.shortcuts import get_object_or_404, render
from .models import Produto


def lista_produtos(request):
    produtos = Produto.objects.select_related("categoria").order_by("nome")
    return render(request, "core/lista_produtos.html", {"produtos": produtos})


def detalhe_produto(request, produto_id):
    produto = get_object_or_404(Produto, pk=produto_id)
    return render(request, "core/detalhe_produto.html", {"produto": produto})
```

FBVs são diretas e boas para fluxos curtos ou muito específicos. Use `request` para consultar método, usuário, parâmetros e dados enviados; a resposta pode ser criada com `HttpResponse`, `JsonResponse` ou `render`.

### Class-Based View (CBV)

Para uma listagem convencional, a mesma ideia pode usar uma CBV:

```python
from django.views.generic import ListView
from .models import Produto


class ProdutoListView(ListView):
    model = Produto
    template_name = "core/lista_produtos.html"
    context_object_name = "produtos"
    ordering = ["nome"]
```

No `core/urls.py`, use `ProdutoListView.as_view()`. CBVs são úteis quando o comportamento se encaixa em uma classe genérica e precisa ser reutilizado ou estendido. Escolha FBV pela clareza do fluxo e CBV pela reutilização e convenções prontas.

## 6. Templates

Crie `core/templates/core/lista_produtos.html`:

```html
{% extends "core/base.html" %}

{% block content %}
  <h1>Produtos</h1>
  <ul>
    {% for produto in produtos %}
      <li>
        <a href="{% url 'detalhe_produto' produto.id %}">
          {{ produto.nome|title }} - R$ {{ produto.preco|floatformat:2 }}
        </a>
      </li>
    {% empty %}
      <li>Nenhum produto cadastrado.</li>
    {% endfor %}
  </ul>
{% endblock %}
```

Template tags executam lógica de apresentação, como `{% for %}` e `{% url %}`. Filters transformam valores, como `|title` e `|floatformat`. A herança evita repetição: `base.html` define blocos e páginas filhas os preenchem.

## 7. Forms

Para um formulário baseado no model, crie `core/forms.py`:

```python
from django import forms
from .models import Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "preco", "categoria"]

    def clean_preco(self):
        preco = self.cleaned_data["preco"]
        if preco <= 0:
            raise forms.ValidationError("O preço deve ser maior que zero.")
        return preco
```

A view pode validar e salvar com o padrão POST/Redirect/GET:

```python
from django.shortcuts import redirect, render
from .forms import ProdutoForm


def criar_produto(request):
    form = ProdutoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("lista_produtos")
    return render(request, "core/form_produto.html", {"form": form})
```

No template, inclua `{% csrf_token %}` dentro de todo `<form method="post">`. Esse template tag gera um campo oculto com um token, validado pelo middleware CSRF antes de aceitar o POST:

```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Salvar</button>
</form>
```

O projeto já aplica essa proteção nos formulários de produto e categoria. `is_valid()` executa validações dos campos e do método `clean_*`.

## 8. Admin Interface

Registre os models em `core/admin.py`:

```python
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
```

Crie um usuário administrador e acesse `/admin/`:

```bash
python manage.py createsuperuser
python manage.py runserver
```

`list_display` define colunas, `list_filter` adiciona filtros e `search_fields` habilita busca. O admin é ótimo para operação interna; para fluxos públicos, crie views e forms próprios.

## Comandos úteis

```bash
python manage.py check
python manage.py showmigrations
python manage.py shell
python manage.py test
```
