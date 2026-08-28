from django.db import migrations


def criar_categorias_padrao(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    Categoria.objects.bulk_create(
        [Categoria(nome="Metal"), Categoria(nome="Plástico")],
        ignore_conflicts=True,
    )


def remover_categorias_padrao(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    Categoria.objects.filter(nome__in=["Metal", "Plástico"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(criar_categorias_padrao, remover_categorias_padrao),
    ]