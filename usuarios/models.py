from django.db import models
from django.utils.crypto import get_random_string

class Usuario(models.Model):
    # Lista de graduações
    GRADUACAO_CHOICES = [
        ('soldado', 'Soldado'),
        ('cabo', 'Cabo'),
        ('sargento', 'Sargento'),
        ('subtenente', 'Subtenente'),
        ('tenente', 'Tenente'),
        ('capitao', 'Capitão'),
        ('major', 'Major'),
        ('tenente_coronel', 'Tenente-Coronel'),
        ('coronel', 'Coronel'),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)  # Em produção use hashing!
    graduacao = models.CharField(max_length=20, choices=GRADUACAO_CHOICES)

    def __str__(self):
        return f"{self.nome} - {self.get_graduacao_display()}"


class Sessao(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    senha = models.CharField(max_length=100)  # pode ser armazenada criptografada
    criador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="sessoes")
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Item(models.Model):
    sessao = models.ForeignKey(Sessao, on_delete=models.CASCADE, related_name="itens")
    nome = models.CharField(max_length=100)
    quantidade = models.PositiveIntegerField(default=1)
    criado_em = models.DateTimeField(auto_now_add=True)

class Retirada(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="retiradas")
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    quantidade = models.PositiveIntegerField(default=1)
    data_retirada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} retirou {self.quantidade} de {self.item.nome} em {self.data_retirada:%d/%m/%Y}"