from decimal import Decimal

from django.test import TestCase

from .forms import ProdutoForm
from .models import Categoria, Produto


class CatalogoTests(TestCase):
	def setUp(self):
		self.categoria = Categoria.objects.create(nome="Livros")
		self.produto = Produto.objects.create(
			nome="Django na prática",
			preco=Decimal("49.90"),
			categoria=self.categoria,
		)

	def test_lista_e_detalhe(self):
		lista = self.client.get("/")
		detalhe = self.client.get(f"/produto/{self.produto.id}/")

		self.assertEqual(lista.status_code, 200)
		self.assertContains(lista, self.produto.nome)
		self.assertEqual(detalhe.status_code, 200)
		self.assertContains(detalhe, self.produto.nome)

	def test_formulario_rejeita_preco_invalido(self):
		form = ProdutoForm(
			data={"nome": "Produto inválido", "preco": "0", "categoria": self.categoria.id}
		)

		self.assertFalse(form.is_valid())
		self.assertIn("preco", form.errors)

	def test_cria_categoria_pelo_formulario(self):
		response = self.client.post("/categorias/", {"nome": "Eletrônicos"})

		self.assertRedirects(response, "/categorias/")
		self.assertTrue(Categoria.objects.filter(nome="Eletrônicos").exists())

	def test_novo_produto_exibe_materiais_padrao(self):
		response = self.client.get("/produto/novo/")

		self.assertContains(response, "Metal")
		self.assertContains(response, "Plástico")
		self.assertContains(response, 'name="csrfmiddlewaretoken"')

	def test_formulario_de_categorias_tem_protecao_csrf(self):
		response = self.client.get("/categorias/")

		self.assertContains(response, 'name="csrfmiddlewaretoken"')

# Create your tests here.
