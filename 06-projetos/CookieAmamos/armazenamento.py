import json
import os

from restaurante import Restaurante
from pedido import Pedido

# __file__ é o caminho deste próprio arquivo (armazenamento.py). Pegando a pasta dele
# (em vez de usar só "loja.json" direto), garantimos que os arquivos de dados sejam
# sempre lidos/salvos na pasta do projeto, não importa de onde o programa for executado
# (isso importa principalmente rodando pelo servidor Flask, que pode ter uma pasta de
# trabalho diferente da pasta do projeto).
PASTA_DO_PROJETO = os.path.dirname(os.path.abspath(__file__))
CAMINHO_ARQUIVO = os.path.join(PASTA_DO_PROJETO, "loja.json")     # guarda UM restaurante (a loja)
CAMINHO_PEDIDOS = os.path.join(PASTA_DO_PROJETO, "pedidos.json")  # guarda uma LISTA de pedidos (histórico)


# Lê o loja.json e devolve um objeto Restaurante já pronto.
# Se o arquivo ainda não existe (primeira vez rodando o programa), devolve None —
# main.py e app.py usam isso pra saber que precisam pedir os dados iniciais da loja.
def carregar_loja():
    if not os.path.exists(CAMINHO_ARQUIVO):
        return None

    with open(CAMINHO_ARQUIVO, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)  # lê o texto JSON e transforma num dicionário Python

    return Restaurante.from_dict(dados)


# Salva o restaurante inteiro (perfil + cardápio) no loja.json, sobrescrevendo o arquivo.
def salvar_loja(restaurante):
    with open(CAMINHO_ARQUIVO, "w", encoding="utf-8") as arquivo:
        # indent=2 deixa o arquivo formatado/legível; ensure_ascii=False mantém acentos
        # normais no arquivo, em vez de vira código tipo ç.
        json.dump(restaurante.to_dict(), arquivo, indent=2, ensure_ascii=False)


# Mesma lógica do carregar_loja, mas para o HISTÓRICO de pedidos (uma lista, não um objeto só).
def carregar_pedidos():
    if not os.path.exists(CAMINHO_PEDIDOS):
        return []

    with open(CAMINHO_PEDIDOS, "r", encoding="utf-8") as arquivo:
        lista_de_dicionarios = json.load(arquivo)

    return [Pedido.from_dict(d) for d in lista_de_dicionarios]


# Salva a lista inteira de pedidos no pedidos.json (sempre reescreve o arquivo todo).
def salvar_pedidos(pedidos):
    lista_de_dicionarios = [p.to_dict() for p in pedidos]

    with open(CAMINHO_PEDIDOS, "w", encoding="utf-8") as arquivo:
        json.dump(lista_de_dicionarios, arquivo, indent=2, ensure_ascii=False)
