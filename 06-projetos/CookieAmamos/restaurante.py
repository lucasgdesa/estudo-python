from prato import Prato


# Representa A LOJA (só existe uma no sistema — não é uma lista de restaurantes).
# Guarda tanto o "perfil" da loja (nome, redes sociais...) quanto o cardápio inteiro.
class Restaurante:
    def __init__(self, nome, instagram="", whatsapp="", endereco="", horario="", aberto=False, cardapio=None):
        self.nome = nome
        self.instagram = instagram
        self.whatsapp = whatsapp
        self.endereco = endereco
        self.horario = horario
        self.aberto = aberto
        # Truque importante: NUNCA usar cardapio=[] direto no parâmetro (lista mutável),
        # porque essa mesma lista seria compartilhada por todo Restaurante criado sem passar cardápio.
        # Usando None e criando a lista aqui dentro, cada loja tem sua própria lista.
        self.cardapio = cardapio if cardapio is not None else []

    # Métodos que mudam o estado da loja. Preferimos chamar esses métodos
    # em vez de fazer restaurante.aberto = True direto de fora da classe.
    def abrir(self):
        self.aberto = True

    def fechar(self):
        self.aberto = False

    def adicionar_prato(self, prato):
        self.cardapio.append(prato)

    # Reconstrói a lista de pratos SEM o prato com esse nome (em vez de procurar e remover um item).
    def remover_prato(self, nome_prato):
        self.cardapio = [prato for prato in self.cardapio if prato.nome != nome_prato]

    # Procura um prato pelo nome. Devolve None se não achar (é assim que quem chama
    # sabe diferenciar "achei o prato" de "não existe esse prato").
    def buscar_prato(self, nome_prato):
        for prato in self.cardapio:
            if prato.nome == nome_prato:
                return prato
        return None

    # Usado em print(restaurante) e em {{ restaurante }} nos templates.
    def __str__(self):
        status = "aberta" if self.aberto else "fechada"
        return f"{self.nome} - {status}"

    # Vira um dicionário simples pra poder ser salvo em JSON (ver armazenamento.py).
    # Repara que cada prato do cardápio também usa o próprio to_dict() dele —
    # o Restaurante não precisa saber os detalhes internos do Prato.
    def to_dict(self):
        return {
            "nome": self.nome,
            "instagram": self.instagram,
            "whatsapp": self.whatsapp,
            "endereco": self.endereco,
            "horario": self.horario,
            "aberto": self.aberto,
            "cardapio": [prato.to_dict() for prato in self.cardapio],
        }

    # Caminho inverso: recebe um dicionário (lido do loja.json) e reconstrói o objeto Restaurante,
    # incluindo reconstruir cada Prato do cardápio a partir dos dicionários salvos.
    @staticmethod
    def from_dict(dados):
        cardapio = [Prato.from_dict(item) for item in dados.get("cardapio", [])]
        return Restaurante(
            nome=dados["nome"],
            instagram=dados.get("instagram", ""),
            whatsapp=dados.get("whatsapp", ""),
            endereco=dados.get("endereco", ""),
            horario=dados.get("horario", ""),
            aberto=dados.get("aberto", False),
            cardapio=cardapio,
        )
