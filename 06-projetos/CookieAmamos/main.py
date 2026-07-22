# Versão em CONSOLE do sistema (sem navegador). Usa as mesmas classes e o mesmo
# armazenamento (loja.json / pedidos.json) que a versão web (app.py) — são duas
# "interfaces" diferentes por cima do mesmo "motor".
import os

from restaurante import Restaurante
from prato import Prato
from pedido import Pedido
from armazenamento import carregar_loja, salvar_loja, carregar_pedidos, salvar_pedidos


# Roda uma vez, no início do programa. Se já existe uma loja salva, só carrega ela.
# Se não existe (primeira vez rodando), pergunta os dados e cria a loja.
def obter_ou_criar_loja():
    restaurante = carregar_loja()

    if restaurante is not None:
        return restaurante  # early return: se já existe, nem entra no resto da função

    os.system("cls")
    print("Bem-vindo! Vamos configurar sua loja pela primeira vez.\n")
    nome = input("Nome da loja: ")
    instagram = input("Instagram (opcional): ")
    whatsapp = input("WhatsApp (opcional): ")
    endereco = input("Endereço (opcional): ")
    horario = input("Horário de funcionamento (opcional): ")

    restaurante = Restaurante(nome, instagram, whatsapp, endereco, horario)
    salvar_loja(restaurante)
    return restaurante


def exibir_cabecalho(restaurante):
    print(f"=== {restaurante} ===\n")  # usa o __str__ do Restaurante


def exibir_opcoes():
    print("1. Ver cardápio")
    print("2. Adicionar prato")
    print("3. Remover prato")
    print("4. Abrir/Fechar loja")
    print("5. Editar perfil da loja")
    print("6. Fazer pedido")
    print("7. Ver pedidos")
    print("8. Sair\n")


def listar_cardapio(restaurante):
    os.system("cls")
    print(f"Cardápio - {restaurante.nome}\n")

    if not restaurante.cardapio:  # lista vazia também é "falsa" em Python
        print("Nenhum prato cadastrado ainda.")
    else:
        for prato in restaurante.cardapio:
            print(f"- {prato}")

    input("\nDigite uma tecla para voltar ao menu: ")


def adicionar_prato(restaurante):
    os.system("cls")
    print("Adicionar novo prato\n")

    nome = input("Nome do prato: ")
    preco = float(input("Preço (ex: 19.90): "))  # converte o texto digitado pra número decimal
    descricao = input("Descrição (opcional): ")

    prato = Prato(nome, preco, descricao)
    restaurante.adicionar_prato(prato)
    salvar_loja(restaurante)  # salva no arquivo pra não perder ao fechar o programa

    print(f"\nPrato '{nome}' adicionado ao cardápio!")
    input("\nDigite uma tecla para voltar ao menu: ")


def remover_prato(restaurante):
    os.system("cls")

    if not restaurante.cardapio:
        print("Nenhum prato cadastrado ainda.")
        input("\nDigite uma tecla para voltar ao menu: ")
        return

    print(f"Cardápio - {restaurante.nome}\n")
    for prato in restaurante.cardapio:
        print(f"- {prato}")

    nome = input("\nNome do prato que deseja remover: ")
    prato_encontrado = restaurante.buscar_prato(nome)

    if prato_encontrado is None:
        print(f"\nNenhum prato chamado '{nome}' foi encontrado.")
    else:
        restaurante.remover_prato(nome)
        salvar_loja(restaurante)
        print(f"\nPrato '{nome}' removido.")

    input("\nDigite uma tecla para voltar ao menu: ")


def alternar_abertura(restaurante):
    # Chama os métodos da classe (abrir/fechar) em vez de mexer direto em restaurante.aberto.
    if restaurante.aberto:
        restaurante.fechar()
    else:
        restaurante.abrir()

    salvar_loja(restaurante)

    os.system("cls")
    status = "aberta" if restaurante.aberto else "fechada"
    print(f"A loja agora está {status}.")
    input("\nDigite uma tecla para voltar ao menu: ")


def editar_perfil(restaurante):
    os.system("cls")
    print("Editar perfil da loja")
    print("(deixe em branco pra manter o valor atual)\n")

    # Mostra o valor atual entre colchetes; se o usuário só der Enter, input() devolve "",
    # que é "falso" em Python, então o "if nome:" abaixo não atualiza esse campo.
    nome = input(f"Nome [{restaurante.nome}]: ")
    instagram = input(f"Instagram [{restaurante.instagram}]: ")
    whatsapp = input(f"WhatsApp [{restaurante.whatsapp}]: ")
    endereco = input(f"Endereço [{restaurante.endereco}]: ")
    horario = input(f"Horário [{restaurante.horario}]: ")

    if nome:
        restaurante.nome = nome
    if instagram:
        restaurante.instagram = instagram
    if whatsapp:
        restaurante.whatsapp = whatsapp
    if endereco:
        restaurante.endereco = endereco
    if horario:
        restaurante.horario = horario

    salvar_loja(restaurante)
    print("\nPerfil atualizado!")
    input("\nDigite uma tecla para voltar ao menu: ")


def fazer_pedido(restaurante, pedidos):
    os.system("cls")

    # Duas condições que impedem o pedido: loja fechada, ou sem nada no cardápio.
    if not restaurante.aberto:
        print("A loja está fechada no momento. Não é possível fazer pedidos.")
        input("\nDigite uma tecla para voltar ao menu: ")
        return

    if not restaurante.cardapio:
        print("O cardápio está vazio, não há o que pedir.")
        input("\nDigite uma tecla para voltar ao menu: ")
        return

    pedido = Pedido()  # pedido novo, vazio

    # Loop que deixa escolher pratos um a um, até o usuário só apertar Enter (finalizar).
    while True:
        os.system("cls")
        print(f"Novo pedido - {restaurante.nome}\n")
        print("Cardápio:")
        for prato in restaurante.cardapio:
            print(f"- {prato}")

        if pedido.itens:
            print("\nItens no pedido até agora:")
            for item in pedido.itens:
                print(f"  {item}")
            print(f"Subtotal: R$ {pedido.total():.2f}")

        nome_prato = input("\nNome do prato para adicionar (em branco para finalizar): ")

        if not nome_prato:
            break  # sai do while True — pedido finalizado

        prato_escolhido = restaurante.buscar_prato(nome_prato)

        if prato_escolhido is None:
            print(f"\nPrato '{nome_prato}' não encontrado no cardápio.")
            input("Digite uma tecla para continuar: ")
            continue  # volta pro início do while, sem adicionar nada

        quantidade = int(input(f"Quantidade de '{prato_escolhido.nome}': "))
        # Passa nome e preço (não o objeto Prato inteiro) — é a "fotografia do preço" do ItemPedido.
        pedido.adicionar_item(prato_escolhido.nome, prato_escolhido.preco, quantidade)

    if not pedido.itens:
        print("\nNenhum item adicionado. Pedido cancelado.")
        input("\nDigite uma tecla para voltar ao menu: ")
        return

    pedidos.append(pedido)      # adiciona na lista de histórico que veio de main()
    salvar_pedidos(pedidos)     # regrava o pedidos.json inteiro

    os.system("cls")
    print("Pedido finalizado!\n")
    print(pedido)  # usa o __str__ do Pedido (o "recibo")
    input("\n\nDigite uma tecla para voltar ao menu: ")


def ver_pedidos(pedidos):
    os.system("cls")
    print("Histórico de pedidos\n")

    if not pedidos:
        print("Nenhum pedido registrado ainda.")
    else:
        for pedido in pedidos:
            print(pedido)
            print("-" * 30)  # linha separadora (repete o caractere "-" 30 vezes)

    input("\nDigite uma tecla para voltar ao menu: ")


def main():
    restaurante = obter_ou_criar_loja()  # carrega (ou cria) a loja UMA VEZ
    pedidos = carregar_pedidos()         # carrega o histórico UMA VEZ

    # Loop principal do menu. Fica rodando até a opção "Sair" dar break.
    while True:
        os.system("cls")
        exibir_cabecalho(restaurante)
        exibir_opcoes()

        try:
            opcao = int(input("Escolha uma opção: "))
        except ValueError:
            # Se o usuário digitar algo que não é número, cai aqui e opcao vira 0
            # (que não bate com nenhuma opção, então vai direto pro "else" de opção inválida).
            opcao = 0

        if opcao == 1:
            listar_cardapio(restaurante)
        elif opcao == 2:
            adicionar_prato(restaurante)
        elif opcao == 3:
            remover_prato(restaurante)
        elif opcao == 4:
            alternar_abertura(restaurante)
        elif opcao == 5:
            editar_perfil(restaurante)
        elif opcao == 6:
            fazer_pedido(restaurante, pedidos)
        elif opcao == 7:
            ver_pedidos(pedidos)
        elif opcao == 8:
            os.system("cls")
            print("Até mais!")
            break
        else:
            print("Opção inválida.")
            input("Digite uma tecla para voltar ao menu: ")


# Só roda main() quando este arquivo é executado diretamente (python main.py),
# não quando é importado por outro arquivo.
if __name__ == "__main__":
    main()
