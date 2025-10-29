from django.shortcuts import render, redirect
from .forms import UsuarioForm, LoginForm, SessaoForm
from .models import Retirada, Usuario, Sessao, Item
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum, Count
import io
import base64
from django.urls import reverse

def cadastrar_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            # Hash a senha antes de salvar
            usuario = form.save(commit=False)
            usuario.senha = make_password(form.cleaned_data['senha'])
            usuario.save()
            return redirect('login')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/cadastrar.html', {'form': form})

def sucesso(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id=usuario_id) if usuario_id else None
    nome = usuario.nome if usuario else None
    graduacao = usuario.graduacao if usuario else None
    sessoes = Sessao.objects.all()
    return render(request, 'usuarios/listar_sessoes.html', {'usuario_id': usuario_id, 'graduacao': graduacao, 'nome': nome, 'sessoes': sessoes})

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
                    return redirect('sucesso')
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

    usuario = Usuario.objects.get(id=usuario_id)

    if not usuario.is_admin:
        messages.error(request, "Acesso negado! Você não tem permissão para acessar o painel de administrador.")
        return redirect('listar_sessoes')

    try:
        user = Usuario.objects.get(id=usuario_id) if usuario_id else None
        nome = user.nome if user else None
        graduacao = user.graduacao if user else None
    except Usuario.DoesNotExist:
        request.session.flush()
        return redirect('login')
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

    if request.method == "POST":
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

    # Proteção: só o criador ou quem entrou na sessão pode adicionar
    if not request.user == sessao.criador and not request.session.get(f"sessao_{sessao.id}", False):
        messages.error(request, "Você não tem permissão!")
        return redirect("entrar_sessao", sessao_id=sessao.id)

    if request.method == "POST":
        nome = request.POST.get("nome")
        quantidade = int(request.POST.get("quantidade", 1))
        Item.objects.create(sessao=sessao, nome=nome, quantidade=quantidade)

        # 🔹 Redireciona de volta para a página de itens
        return redirect("listar_itens", sessao_id=sessao.id)

    # Se precisar de template separado (não usado no modal)
    return render(request, "adicionar_item.html", {"sessao": sessao})

def criar_sessao(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario_id = request.session.get('usuario_id')
    criador = Usuario.objects.get(id=usuario_id) if usuario_id else None

    usuario = Usuario.objects.get(id=usuario_id)

    if not usuario.is_admin:
        messages.error(request, "Acesso negado! Você não tem permissão para acessar o painel de administrador.")
        return redirect('listar_sessoes')

    if request.method == "POST":
        form = SessaoForm(request.POST)
        if form.is_valid():
            form.saveSessao(criador=criador)
            messages.success(request, "Sessão criada com sucesso!")
            return redirect("listar_sessoes")
    else:
        form = SessaoForm()

    return render(request, "usuarios/criar_sessao.html", {'form': form})

def mostrar_sessao(request):
    usuario_id = request.session.get('usuario_id')
    return HttpResponse(f"Usuário logado (usuario_id): {usuario_id}")

def listar_sessoes(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id=usuario_id)
    sessoes = Sessao.objects.all()
    usuario_admin = usuario.is_admin
    return render(request, 'usuarios/listar_sessoes.html', {'sessoes': sessoes, 'usuario': usuario, 'usuario_admin': usuario_admin})

def listar_itens(request, sessao_id):
    sessao = get_object_or_404(Sessao, id=sessao_id)

    if not request.session.get(f"sessao_{sessao.id}", False):
        return redirect("listar_sessoes")

    # Processa retirada se for POST (chama a lógica de retirar_item)
    if request.method == "POST" and 'retirar_item' in request.POST:
        item_id = request.POST.get("item_id")
        usuario_id = request.POST.get("usuario")
        quantidade = int(request.POST.get("quantidade", 1))
        item = get_object_or_404(Item, id=item_id)
        usuario = get_object_or_404(Usuario, id=usuario_id)

        if quantidade <= item.quantidade:
            # Verifica se já existe retirada para o mesmo usuário + item
            retirada_existente = Retirada.objects.filter(item=item, usuario=usuario).first()

            if retirada_existente:
                retirada_existente.quantidade += quantidade
                retirada_existente.save()
            else:
                Retirada.objects.create(
                    item=item,
                    usuario=usuario,
                    quantidade=quantidade
                )

            # Atualiza estoque
            item.quantidade -= quantidade
            item.save()
        else:
            messages.error(request, "Quantidade solicitada maior que disponível.")
        return redirect("listar_itens", sessao_id=sessao.id)

    itens = sessao.itens.all()
    usuarios = Usuario.objects.all()
    return render(request, "usuarios/listar_itens.html", {
        "sessao": sessao,
        "itens": itens,
        "usuarios": usuarios
    })

def validar_sessao(request, sessao_id):
    if request.method == "POST":
        sessao = get_object_or_404(Sessao, id=sessao_id)
        senha = request.POST.get("senha")

        if senha == sessao.senha:  # ⚠️ use hash em produção
            # salva login na sessão do usuário
            request.session[f"sessao_{sessao.id}"] = True

            return JsonResponse({
                "success": True,
                "redirect_url": reverse("listar_itens", args=[sessao.id])
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "Senha incorreta!"
            })

    return JsonResponse({"success": False, "error": "Método inválido."}, status=400)

def retirar_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        usuario_value = request.POST.get("usuario")
        # Parse the value: "id - name - graduation"
        usuario_id = usuario_value.split(" - ")[0] if " - " in usuario_value else usuario_value
        quantidade = int(request.POST.get("quantidade", 1))

        usuario = get_object_or_404(Usuario, id=usuario_id)

        if quantidade > item.quantidade:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Quantidade solicitada maior que disponível.'})
            messages.error(request, "Quantidade solicitada maior que disponível.")
            return redirect("listar_itens", sessao_id=item.sessao.id)

        # Verifica se já existe retirada para o mesmo usuário + item
        retirada_existente = Retirada.objects.filter(item=item, usuario=usuario).first()

        if retirada_existente:
            retirada_existente.quantidade += quantidade
            retirada_existente.save()
            retirada = retirada_existente
        else:
            retirada = Retirada.objects.create(
                item=item,
                usuario=usuario,
                quantidade=quantidade,
                data_retirada=timezone.now()
            )

        # Atualiza estoque
        item.quantidade -= quantidade
        item.save()

        # Gera PDF da cautela
        template_path = 'usuarios/cautela_retirada.html'
        context = {'retirada': retirada}

        template = get_template(template_path)
        html = template.render(context)

        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
        if pisa_status.err:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Erro ao gerar PDF da cautela'})
            return HttpResponse("Erro ao gerar PDF da cautela")

        pdf_data = pdf_buffer.getvalue()
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'pdf': pdf_base64,
                'filename': f"cautela_{retirada.usuario.nome}_{retirada.item.nome}_{retirada.data_retirada.strftime('%d%m%Y_%H%M')}.pdf",
                'new_quantity': item.quantidade,
                'retirada': {
                    'id': retirada.id,
                    'usuario': {'nome': retirada.usuario.nome},
                    'quantidade': retirada.quantidade,
                    'item': {'sessao': {'id': retirada.item.sessao.id}}
                }
            })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cautela_{retirada.usuario.nome}_{retirada.item.nome}_{retirada.data_retirada.strftime('%d%m%Y_%H%M')}.pdf"'
        response.write(pdf_data)
        return response

def remover_retirada(request, retirada_id):
    try:
        retirada = Retirada.objects.get(id=retirada_id)
    except Retirada.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Retirada não encontrada.'})
        messages.error(request, "Retirada não encontrada.")
        next_parts = request.GET.get('next', '').strip('/').split('/')
        sessao_id = next_parts[-2] if len(next_parts) >= 2 else 1
        return redirect("listar_itens", sessao_id=sessao_id)
    item = retirada.item
    if request.method == "POST":

        qtd_remover = int(request.POST.get("quantidade", retirada.quantidade))
        if qtd_remover > retirada.quantidade:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Quantidade inválida.'})
            messages.error(request, "Quantidade inválida.")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect("listar_itens", sessao_id=item.sessao.id)

        retirada_deleted = False
        if qtd_remover >= retirada.quantidade:
            item.quantidade += retirada.quantidade
            item.save()
            retirada.delete()
            quantidade_devolvida = retirada.quantidade
            retirada_deleted = True
        else:
            # Remove apenas parte da retirada
            item.quantidade += qtd_remover
            item.save()
            retirada.quantidade -= qtd_remover
            retirada.save()
            quantidade_devolvida = qtd_remover

        # Gera PDF da devolução
        template_path = 'usuarios/cautela_devolucao.html'
        context = {
            'retirada': retirada if not retirada_deleted else None,  # If fully deleted, pass None or adjust template
            'quantidade_devolvida': quantidade_devolvida,
            'data_devolucao': timezone.now()
        }

        template = get_template(template_path)
        html = template.render(context)

        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
        if pisa_status.err:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Erro ao gerar PDF da devolução'})
            return HttpResponse("Erro ao gerar PDF da devolução")

        pdf_data = pdf_buffer.getvalue()
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response_data = {
                'success': True,
                'pdf': pdf_base64,
                'filename': f"devolucao_{retirada.usuario.nome}_{retirada.item.nome}_{timezone.now().strftime('%d%m%Y_%H%M')}.pdf",
                'new_quantity': item.quantidade,
                'retirada_deleted': retirada_deleted
            }
            if not retirada_deleted:
                response_data['new_retirada_quantity'] = retirada.quantidade
            return JsonResponse(response_data)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="devolucao_{retirada.usuario.nome}_{retirada.item.nome}_{timezone.now().strftime('%d%m%Y_%H%M')}.pdf"'
        response.write(pdf_data)
        return response

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect("listar_itens", sessao_id=item.sessao.id)

def gerar_relatorio_pdf(request, sessao_id):
    sessao = get_object_or_404(Sessao, id=sessao_id)

    template_path = 'usuarios/relatorio_cautelas.html'
    context = {'sessao': sessao}

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="relatorio_sessao_{sessao.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF")
    return response

def excluir_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    sessao_id = item.sessao.id  # Salva o ID da sessão antes de excluir o item
    if request.method == "POST":
        item.delete()
        return redirect("listar_itens", sessao_id=sessao_id)  # Redireciona usando o ID salvo
    return render(request, "usuarios/confirmar_exclusao.html", {"item": item})

def edit_user(request, user_id):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso!")
            next_page = request.GET.get('next')
            if next_page == 'admin_panel':
                return redirect('admin_panel')
            else:
                return redirect('all_users')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'usuarios/edit_user.html', {'form': form, 'usuario': usuario})

def delete_user(request, user_id):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        usuario.delete()
        messages.success(request, "Usuário excluído com sucesso!")
        next_page = request.GET.get('next')
        if next_page == 'admin_panel':
            return redirect('admin_panel')
        else:
            return redirect('all_users')

    return render(request, 'usuarios/confirmar_exclusao_usuario.html', {'usuario': usuario})

def admin_panel(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario_id = request.session.get('usuario_id')
    usuario = Usuario.objects.get(id=usuario_id)

    if not usuario.is_admin:
        messages.error(request, "Acesso negado! Você não tem permissão para acessar o painel de administrador.")
        return redirect('listar_sessoes')

    total_usuarios = Usuario.objects.count()
    total_sessoes = Sessao.objects.count()
    total_itens = Item.objects.count()
    total_retiradas = Retirada.objects.count()

    # Estatísticas de inventário
    total_itens_disponiveis = Item.objects.aggregate(total=Sum('quantidade'))['total'] or 0
    total_itens_emprestados = Retirada.objects.aggregate(total=Sum('quantidade'))['total'] or 0
    itens_mais_requisitados = Item.objects.values('nome', 'sessao__nome').annotate(total_retiradas=Sum('retiradas__quantidade')).order_by('-total_retiradas')[:5]
    taxa_utilizacao = round((total_itens_emprestados / (total_itens_disponiveis + total_itens_emprestados)) * 100, 2) if (total_itens_disponiveis + total_itens_emprestados) > 0 else 0

    usuarios = Usuario.objects.all()
    sessoes = Sessao.objects.all()

    context = {
        'usuario': usuario,
        'total_usuarios': total_usuarios,
        'total_sessoes': total_sessoes,
        'total_itens': total_itens,
        'total_retiradas': total_retiradas,
        'total_itens_disponiveis': total_itens_disponiveis,
        'total_itens_emprestados': total_itens_emprestados,
        'itens_mais_requisitados': itens_mais_requisitados,
        'taxa_utilizacao': taxa_utilizacao,
        'usuarios': usuarios,
        'sessoes': sessoes,
    }

    return render(request, 'usuarios/admin_panel.html', context)
