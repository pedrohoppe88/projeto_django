from django.shortcuts import render, redirect
from .forms import UsuarioForm
from .forms import UsuarioForm, LoginForm
from .models import Retirada, Usuario
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Sessao, Item
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            # Aqui você poderia hash a senha se quiser
            form.save()
            return redirect('login')
           # return redirect('sucesso')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/cadastrar.html', {'form': form})

@login_required
def sucesso(request):
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id=usuario_id) if usuario_id else None
    nome = usuario.nome if usuario else None
    graduacao = usuario.graduacao if usuario else None
    return render(request, 'usuarios/sucesso.html', {'usuario_id': usuario_id, 'graduacao': graduacao, 'nome': nome})

def login_usuario(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            senha = form.cleaned_data['senha']

            try:
                usuario = Usuario.objects.get(email=email)
                if check_password(senha, usuario.senha):
                    request.session['usuario_id'] = usuario.id  # salva sessão
                    return redirect('home')
                else:
                    form.add_error('senha', 'Senha incorreta.')
            except Usuario.DoesNotExist:
                form.add_error('email', 'Usuário não encontrado.')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_usuario(request):
    request.session.flush()  # remove todas as sessões
    return redirect('login')

def listar_usuarios(request):
    if 'usuario_id' not in request.session:
        return redirect('login')  # protege a página
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/all_users.html', {'usuarios': usuarios})

def all_users(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    usuarios = Usuario.objects.all()
    usuario_id = request.session.get('usuario_id')
    user = Usuario.objects.get(id=usuario_id) if usuario_id else None
    nome = user.nome if user else None
    graduacao = user.graduacao if user else None
    quant_id = Usuario.objects.count()
    return render(request, 'usuarios/all_users.html', {
        'usuarios': usuarios,
        'id_usuario': usuario_id,
        'nome': nome,
        'graduacao': graduacao,
        'quantidade': quant_id
    })
    
def dashboard(request):
    if 'usuario_id' not in request.session:
        return redirect('login')  # protege a página
    
    usuarios = Usuario.objects.all()
    
    # Contagem para os cards de estatísticas
    total_usuarios = usuarios.count()
    usuarios_ativos = usuarios.filter(status='ativo').count()  # se você tiver campo status
    graduados_recentes = usuarios.order_by('-id')[:5].count()  # últimos 5 cadastrados
    
    context = {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios,
        'usuarios_ativos': usuarios_ativos,
        'graduados_recentes': graduados_recentes,
    }
    
    
def entrar_sessao(request, sessao_id):
    sessao = get_object_or_404(Sessao, id=sessao_id)
    
    if request.method  == "POST":
        senha = request.POST.get('senha')
        if sessao.senha == senha:
            request.session[f"sessao_{sessao.id}"] = True;
            return redirect('detalhes_sessao', sessao_id=sessao.id)
        else:
            messages.error(request, 'Senha incorreta.')
            return render(request, "entrar_sessao.html", {"sessao": sessao})
    
def detalhes_sessao(request, sessao_id):
    sessao = get_object_or_404(Sessao, id=sessao_id)

    # Só entra se for admin ou se tiver a senha
    if not request.user == sessao.criador and not request.session.get(f"sessao_{sessao.id}", False):
        messages.error(request, "Acesso negado!")
        return redirect("entrar_sessao", sessao_id=sessao.id)

    itens = sessao.itens.all()
    return render(request, "detalhes_sessao.html", {"sessao": sessao, "itens": itens})

def adicionar_item(request, sessao_id):
    sessao = get_object_or_404(Sessao, id=sessao_id)

    if not request.user == sessao.criador and not request.session.get(f"sessao_{sessao.id}", False):
        messages.error(request, "Você não tem permissão!")
        return redirect("entrar_sessao", sessao_id=sessao.id)

    if request.method == "POST":
        nome = request.POST.get("nome")
        quantidade = request.POST.get("quantidade", 1)
        Item.objects.create(sessao=sessao, nome=nome, quantidade=quantidade)
        return redirect("detalhes_sessao", sessao_id=sessao.id)

    return render(request, "adicionar_item.html", {"sessao": sessao})


def excluir_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    sessao = item.sessao

    if not request.user == sessao.criador and not request.session.get(f"sessao_{sessao.id}", False):
        messages.error(request, "Você não tem permissão para deletar!")
        return redirect("entrar_sessao", sessao_id=sessao.id)

    item.delete()
    return redirect("detalhes_sessao", sessao_id=sessao.id)

@login_required
def criar_sessao(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        senha = request.POST.get("senha")

        if Sessao.objects.filter(nome=nome).exists():
            messages.error(request, "Já existe uma sessão com esse nome.")
        else:
            Sessao.objects.create(nome=nome, senha=senha, criador=request.user)
            messages.success(request, "Sessão criada com sucesso!")
            return redirect("listar_sessoes")

    return render(request, "usuarios/criar_sessao.html")

def mostrar_sessao(request):
    usuario_id = request.session.get('usuario_id')
    return HttpResponse(f"Usuário logado (usuario_id): {usuario_id}")

def retirar_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        quantidade = int(request.POST.get("quantidade", 1))

        if quantidade <= item.quantidade:
            # cria registro da retirada
            Retirada.objects.create(
            item=item,
                usuario=request.user,
                quantidade=quantidade
            )

            # atualiza estoque
            item.quantidade -= quantidade
            item.save()
        else:
            messages.error(request, "Quantidade solicitada maior que disponível.")

        return redirect("detalhes_sessao", sessao_id=item.sessao.id)