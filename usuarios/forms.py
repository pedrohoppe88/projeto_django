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