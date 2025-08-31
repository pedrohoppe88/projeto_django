from django import forms
from .models import Usuario
from django.contrib.auth.hashers import make_password

class UsuarioForm(forms.ModelForm):
    senha = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha', 'graduacao']

    def save(self, commit=True):
        usuario = super().save(commit=False)
        # Hash da senha antes de salvar
        usuario.senha = make_password(self.cleaned_data['senha'])
        if commit:
            usuario.save()
        return usuario


class LoginForm(forms.Form):
    email = forms.EmailField(label="E-mail")
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput)
    
class SessaoForm(forms.Form):
    nome = forms.CharField(label="Nome da Sessão", max_length=100)
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput)
    
    def saveSessao(self, criador):
        from .models import Sessao
        sessao = Sessao(
            nome=self.cleaned_data['nome'],
            senha=self.cleaned_data['senha'],
            criador=criador
        )
        sessao.save()
        return sessao