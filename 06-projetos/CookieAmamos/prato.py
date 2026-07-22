# Representa um item do cardápio (um sabor de cookie, por exemplo).
# É usado tanto pelo Restaurante (dentro do cardápio) quanto pelos Pedidos.
class Prato:
    def __init__(self, nome, preco, descricao=""):
        self.nome = nome
        self.preco = preco
        self.descricao = descricao  # opcional, por isso o valor padrão ""

    # Chamado automaticamente quando fazemos print(prato) ou usamos {{ prato }} num template.
    def __str__(self):
        texto = f"{self.nome} - R$ {self.preco:.2f}"  # :.2f = número com 2 casas decimais
        if self.descricao:  # string vazia "" é "falsa" em Python, então só entra aqui se tiver descrição
            texto += f" ({self.descricao})"
        return texto

    # Converte o objeto num dicionário simples, pra poder salvar em JSON
    # (o módulo json não sabe salvar objetos Python direto, só dict/list/str/número).
    def to_dict(self):
        return {"nome": self.nome, "preco": self.preco, "descricao": self.descricao}

    # Caminho inverso do to_dict: recebe um dicionário (lido do JSON) e reconstrói o objeto Prato.
    # @staticmethod porque não precisa de um Prato já existente pra funcionar.
    @staticmethod
    def from_dict(dados):
        return Prato(
            nome=dados["nome"],
            preco=dados["preco"],
            descricao=dados.get("descricao", ""),  # .get com padrão: não quebra se a chave não existir
        )
