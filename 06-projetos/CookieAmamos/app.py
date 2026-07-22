# Versão WEB do sistema (Flask). Cada "rota" (@app.route) é uma URL que o navegador
# pode acessar. Usa as MESMAS classes e o MESMO armazenamento (loja.json / pedidos.json)
# que o main.py do console — só muda a interface por cima.
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash

from restaurante import Restaurante
from prato import Prato
from pedido import Pedido
from armazenamento import carregar_loja, salvar_loja, carregar_pedidos, salvar_pedidos
from frete import calcular_frete
from config import SENHA_ADMIN

app = Flask(__name__)
# Necessário pra usar "session" (usada como carrinho de compras temporário lá embaixo,
# e também pra lembrar se o administrador está logado) e pra usar "flash" (mensagens
# de erro/aviso de uma única exibição, ver calcular_frete_pedido).
# O Flask usa essa chave pra assinar o cookie de sessão — num site publicado de verdade,
# isso deveria vir de uma variável de ambiente, não escrito direto no código.
app.secret_key = "chave-de-estudo-troque-depois"


# Um "decorator": uma função que embrulha outra função, adicionando um comportamento
# extra sem precisar copiar esse código dentro de cada rota. Aqui, o comportamento
# extra é "só deixa passar se estiver logado como admin".
#
# Pra usar, é só escrever @requer_admin em cima de qualquer rota que deva ser
# protegida (ver painel(), ver_cardapio() etc. logo abaixo).
def requer_admin(rota):
    @wraps(rota)  # preserva o nome/docstring original da função embrulhada
    def rota_protegida(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("entrar_admin"))
        return rota(*args, **kwargs)
    return rota_protegida


# Tela de login da área de administrador. GET mostra o formulário; POST confere a senha.
@app.route("/painel/entrar", methods=["GET", "POST"])
def entrar_admin():
    if request.method == "POST":
        senha_digitada = request.form.get("senha", "")

        if senha_digitada == SENHA_ADMIN:
            session["admin"] = True
            return redirect(url_for("painel"))

        flash("Senha incorreta.")

    return render_template("entrar_admin.html")


@app.route("/painel/sair", methods=["POST"])
def sair_admin():
    session["admin"] = False
    return redirect(url_for("dashboard"))


# O carrinho fica guardado na session como um dicionário {nome_do_prato: quantidade}
# — um item por prato, não uma lista de "eventos de adicionar" como era antes. Isso
# combina direto com os botões de mais/menos: cada clique só sobe ou desce o número
# daquele prato específico, nunca duplica linha.
def obter_carrinho():
    carrinho = session.get("carrinho", {})

    if not isinstance(carrinho, dict):
        # Uma sessão aberta antes dessa mudança guardava o carrinho como lista.
        # Em vez de quebrar com esse formato antigo, tratamos como carrinho vazio.
        carrinho = {}

    return carrinho


# Lê o carrinho, busca o preço atual de cada prato no cardápio (restaurante.
# buscar_prato) e calcula os totais. Reaproveitado por /pedido e por toda rota que
# mexe no carrinho — todas precisam montar os mesmos números pra mostrar na tela.
def contexto_do_carrinho(restaurante):
    carrinho = obter_carrinho()

    itens_carrinho = []
    subtotal = 0
    for nome_prato, quantidade in carrinho.items():
        prato = restaurante.buscar_prato(nome_prato)
        if prato is None:
            continue  # o prato pode ter sido removido do cardápio depois de ir pro carrinho
        itens_carrinho.append({"nome": nome_prato, "preco": prato.preco, "quantidade": quantidade})
        subtotal += prato.preco * quantidade

    frete = session.get("frete", 0.0)

    return {
        "carrinho": carrinho,
        "itens_carrinho": itens_carrinho,
        "subtotal": subtotal,
        "frete": frete,
        "distancia_km": session.get("distancia_km", 0.0),
        "endereco_cliente": session.get("endereco_cliente", ""),
        "total": subtotal + frete,
    }


# Página inicial pública (a "vitrine" da loja: hero, sabores em destaque, rodapé com contato).
@app.route("/")
def dashboard():
    restaurante = carregar_loja()

    if restaurante is None:
        # Ainda não existe loja salva (primeiro acesso) — mostra o formulário de configuração.
        return render_template("configurar_loja.html")

    destaques = restaurante.cardapio[:4]  # só os 4 primeiros pratos, pra não lotar a vitrine
    return render_template("vitrine.html", restaurante=restaurante, destaques=destaques)


# Área administrativa: editar perfil da loja e abrir/fechar.
@app.route("/painel")
@requer_admin
def painel():
    restaurante = carregar_loja()

    if restaurante is None:
        return render_template("configurar_loja.html")

    return render_template("painel.html", restaurante=restaurante)


# Histórico de pedidos, com um seletor de calendário pra escolher qualquer dia.
@app.route("/pedidos")
@requer_admin
def ver_pedidos():
    pedidos = list(reversed(carregar_pedidos()))  # mais recentes primeiro dentro de cada dia

    # Agrupa os pedidos por dia, num dicionário {dia: [pedidos daquele dia]}. A chave
    # fica no formato "DD/MM/AAAA", igual ao que já é salvo em cada pedido.
    pedidos_por_dia = {}
    for pedido in pedidos:
        dia = pedido.data_hora.split(" ")[0]  # "13/07/2026 14:30" -> "13/07/2026"
        pedidos_por_dia.setdefault(dia, []).append(pedido)

    # O <input type="date"> do navegador manda a data escolhida no formato ISO
    # "AAAA-MM-DD" (é assim que esse tipo de campo sempre funciona, não dá pra mudar).
    # Se não vier nada na URL (primeira visita), usamos o dia de hoje como padrão.
    data_iso = request.args.get("data", datetime.now().strftime("%Y-%m-%d"))
    ano, mes, dia_numero = data_iso.split("-")
    dia_selecionado = f"{dia_numero}/{mes}/{ano}"  # convertido pro formato usado nos dados salvos

    pedidos_do_dia = pedidos_por_dia.get(dia_selecionado, [])
    total_do_dia = sum(pedido.total() for pedido in pedidos_do_dia)

    return render_template(
        "pedidos.html",
        data_iso=data_iso,
        dia_selecionado=dia_selecionado,
        pedidos_do_dia=pedidos_do_dia,
        total_do_dia=total_do_dia,
    )


# Recebe o formulário de "configurar loja pela primeira vez" e cria o Restaurante.
@app.route("/loja/criar", methods=["POST"])
def criar_loja():
    restaurante = Restaurante(
        nome=request.form["nome"],               # request.form = dados enviados pelo formulário
        instagram=request.form.get("instagram", ""),
        whatsapp=request.form.get("whatsapp", ""),
        endereco=request.form.get("endereco", ""),
        horario=request.form.get("horario", ""),
    )
    salvar_loja(restaurante)
    return redirect(url_for("dashboard"))  # depois de salvar, redireciona pra vitrine


# Tela de montar um pedido novo. Cada requisição carrega a loja e o carrinho do zero,
# porque no Flask cada clique é uma requisição independente (não fica um loop
# esperando, como no console) — quem "lembra" o carrinho entre as requisições é a session.
@app.route("/pedido")
def novo_pedido():
    restaurante = carregar_loja()
    return render_template("pedido.html", restaurante=restaurante, **contexto_do_carrinho(restaurante))


# Botão "+" de um prato: soma 1 na quantidade desse prato no carrinho.
# <nome_prato> na URL identifica de qual prato veio o clique (mesmo padrão usado em
# /cardapio/remover/<nome_prato>).
@app.route("/pedido/quantidade/<nome_prato>/aumentar", methods=["POST"])
def aumentar_quantidade(nome_prato):
    restaurante = carregar_loja()

    # só aceita se a loja estiver aberta E o prato realmente existir no cardápio
    if restaurante.aberto and restaurante.buscar_prato(nome_prato) is not None:
        carrinho = obter_carrinho()
        carrinho[nome_prato] = carrinho.get(nome_prato, 0) + 1
        # Reatribuir session["carrinho"] (em vez de só alterar o dicionário) é o que
        # garante que o Flask perceba a mudança e salve a sessão de novo.
        session["carrinho"] = carrinho

    # HX-Request é um cabeçalho que o HTMX manda automaticamente em toda requisição dele.
    if request.headers.get("HX-Request"):
        return render_template("_pedido_conteudo.html", restaurante=restaurante, **contexto_do_carrinho(restaurante))

    return redirect(url_for("novo_pedido"))


# Botão "−" de um prato: subtrai 1 da quantidade. Se chegar a 0, remove o prato do
# carrinho (não faz sentido guardar "0x Kinder Bueno" ali).
@app.route("/pedido/quantidade/<nome_prato>/diminuir", methods=["POST"])
def diminuir_quantidade(nome_prato):
    restaurante = carregar_loja()

    carrinho = obter_carrinho()
    if nome_prato in carrinho:
        carrinho[nome_prato] -= 1
        if carrinho[nome_prato] <= 0:
            del carrinho[nome_prato]
        session["carrinho"] = carrinho

    if request.headers.get("HX-Request"):
        return render_template("_pedido_conteudo.html", restaurante=restaurante, **contexto_do_carrinho(restaurante))

    return redirect(url_for("novo_pedido"))


# Recebe o endereço do cliente, calcula a distância de rota até a loja (via frete.py,
# que chama a API do OpenRouteService) e guarda o valor do frete na sessão.
@app.route("/pedido/calcular-frete", methods=["POST"])
def calcular_frete_pedido():
    restaurante = carregar_loja()
    endereco_cliente = request.form.get("endereco_cliente", "").strip()

    if endereco_cliente:
        resultado = calcular_frete(restaurante.endereco, endereco_cliente)

        if "erro" in resultado:
            # flash() guarda uma mensagem de "uma exibição só": ela some sozinha depois
            # de aparecer na tela uma vez (não precisa dar session["algo"] = None manualmente).
            flash(resultado["erro"])
        else:
            session["endereco_cliente"] = endereco_cliente
            session["frete"] = resultado["valor"]
            session["distancia_km"] = resultado["distancia_km"]

    if request.headers.get("HX-Request"):
        return render_template("_pedido_conteudo.html", restaurante=restaurante, **contexto_do_carrinho(restaurante))

    return redirect(url_for("novo_pedido"))


# Transforma o carrinho (sessão) num Pedido de verdade e salva no histórico.
@app.route("/pedido/finalizar", methods=["POST"])
def finalizar_pedido():
    restaurante = carregar_loja()
    carrinho = obter_carrinho()

    if not carrinho:
        return redirect(url_for("ver_pedidos"))

    if not session.get("endereco_cliente"):
        flash("Informe o endereço de entrega antes de finalizar o pedido.")
        return redirect(url_for("novo_pedido"))

    pedido = Pedido(
        endereco_cliente=session.get("endereco_cliente", ""),
        frete=session.get("frete", 0.0),
        distancia_km=session.get("distancia_km", 0.0),
    )
    for nome_prato, quantidade in carrinho.items():
        prato = restaurante.buscar_prato(nome_prato)
        if prato is not None:
            pedido.adicionar_item(prato.nome, prato.preco, quantidade)

    pedidos = carregar_pedidos()
    pedidos.append(pedido)
    salvar_pedidos(pedidos)

    # Esvazia tudo que era desse pedido: carrinho, endereço e frete.
    session["carrinho"] = {}
    session["endereco_cliente"] = ""
    session["frete"] = 0.0
    session["distancia_km"] = 0.0

    return redirect(url_for("ver_pedidos"))


# Descarta o carrinho atual sem salvar nenhum pedido.
@app.route("/pedido/cancelar", methods=["POST"])
def cancelar_pedido():
    session["carrinho"] = {}
    session["endereco_cliente"] = ""
    session["frete"] = 0.0
    session["distancia_km"] = 0.0
    return redirect(url_for("novo_pedido"))


@app.route("/cardapio")
@requer_admin
def ver_cardapio():
    restaurante = carregar_loja()
    return render_template("cardapio.html", restaurante=restaurante)


@app.route("/cardapio/adicionar", methods=["POST"])
@requer_admin
def adicionar_prato():
    restaurante = carregar_loja()

    prato = Prato(
        nome=request.form["nome"],
        preco=float(request.form["preco"]),
        descricao=request.form.get("descricao", ""),
    )
    restaurante.adicionar_prato(prato)
    salvar_loja(restaurante)
    return redirect(url_for("ver_cardapio"))


# <nome_prato> na URL é um "segmento dinâmico": o Flask captura o que vier ali
# (ex: /cardapio/remover/Tradicional) e passa como argumento pra função.
@app.route("/cardapio/remover/<nome_prato>", methods=["POST"])
@requer_admin
def remover_prato(nome_prato):
    restaurante = carregar_loja()
    restaurante.remover_prato(nome_prato)
    salvar_loja(restaurante)
    return redirect(url_for("ver_cardapio"))


@app.route("/loja/alternar", methods=["POST"])
@requer_admin
def alternar_abertura():
    restaurante = carregar_loja()

    if restaurante.aberto:
        restaurante.fechar()
    else:
        restaurante.abrir()

    salvar_loja(restaurante)
    return redirect(url_for("painel"))  # volta pro painel (foi de lá que a ação veio)


@app.route("/loja/editar", methods=["POST"])
@requer_admin
def editar_perfil():
    restaurante = carregar_loja()

    restaurante.nome = request.form["nome"]
    restaurante.instagram = request.form.get("instagram", "")
    restaurante.whatsapp = request.form.get("whatsapp", "")
    restaurante.endereco = request.form.get("endereco", "")
    restaurante.horario = request.form.get("horario", "")

    salvar_loja(restaurante)
    return redirect(url_for("painel"))


# Só inicia o servidor quando rodamos "python app.py" diretamente.
# debug=True liga as páginas de erro detalhadas e o recarregamento automático
# do servidor quando um arquivo é salvo — bom pra estudar, mas deve ser desligado
# se esse site for publicado de verdade algum dia.
if __name__ == "__main__":
    app.run(debug=True)
