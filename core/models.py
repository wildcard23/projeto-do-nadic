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
