from datetime import datetime


# Representa UM item dentro de um pedido: um prato + a quantidade escolhida.
# Repara que guardamos nome_prato e preco_unitario como uma "fotografia" do momento da compra
# (não uma referência direta ao objeto Prato do cardápio). Assim, se o preço do prato mudar
# depois no cardápio, os pedidos antigos continuam mostrando o preço que foi cobrado na hora.
class ItemPedido:
    def __init__(self, nome_prato, preco_unitario, quantidade):
        self.nome_prato = nome_prato
        self.preco_unitario = preco_unitario
        self.quantidade = quantidade

    def subtotal(self):
        return self.preco_unitario * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.nome_prato} - R$ {self.subtotal():.2f}"

    def to_dict(self):
        return {
            "nome_prato": self.nome_prato,
            "preco_unitario": self.preco_unitario,
            "quantidade": self.quantidade,
        }

    @staticmethod
    def from_dict(dados):
        return ItemPedido(
            nome_prato=dados["nome_prato"],
            preco_unitario=dados["preco_unitario"],
            quantidade=dados["quantidade"],
        )


# Representa um pedido completo: os itens, quando foi feito, e pra onde vai (endereço
# de entrega + o frete calculado até lá — ver frete.py).
class Pedido:
    def __init__(self, itens=None, data_hora=None, endereco_cliente="", frete=0.0, distancia_km=0.0):
        self.itens = itens if itens is not None else []  # mesmo truque do cardapio=None no Restaurante
        # Não dá pra usar data_hora=datetime.now() direto no parâmetro: o Python calcularia isso
        # UMA VEZ SÓ, quando o arquivo é carregado — todo pedido pegaria a mesma hora (a hora
        # que o programa abriu). Usando None e calculando aqui dentro, cada pedido pega a hora certa.
        self.data_hora = data_hora if data_hora is not None else datetime.now().strftime("%d/%m/%Y %H:%M")
        self.endereco_cliente = endereco_cliente
        self.frete = frete
        self.distancia_km = distancia_km

    # Cria um ItemPedido novo e adiciona na lista de itens deste pedido.
    def adicionar_item(self, nome_prato, preco_unitario, quantidade):
        self.itens.append(ItemPedido(nome_prato, preco_unitario, quantidade))

    # Soma só o subtotal dos pratos, SEM o frete. "sum(x for x in y)" é uma generator
    # expression: como uma list comprehension, mas sem criar uma lista intermediária.
    def subtotal_itens(self):
        return sum(item.subtotal() for item in self.itens)

    # Total de verdade do pedido: os pratos + o frete da entrega.
    def total(self):
        return self.subtotal_itens() + self.frete

    # Monta um "recibo" em texto: uma linha por item, o frete, e o total no final.
    def __str__(self):
        linhas = [f"Pedido de {self.data_hora}"]
        for item in self.itens:
            linhas.append(f"  {item}")
        if self.endereco_cliente:
            linhas.append(f"Entrega: {self.endereco_cliente} ({self.distancia_km:.1f} km)")
            linhas.append(f"Frete: R$ {self.frete:.2f}")
        linhas.append(f"Total: R$ {self.total():.2f}")
        return "\n".join(linhas)

    def to_dict(self):
        return {
            "data_hora": self.data_hora,
            "itens": [item.to_dict() for item in self.itens],
            "endereco_cliente": self.endereco_cliente,
            "frete": self.frete,
            "distancia_km": self.distancia_km,
        }

    @staticmethod
    def from_dict(dados):
        itens = [ItemPedido.from_dict(item) for item in dados.get("itens", [])]
        return Pedido(
            itens=itens,
            data_hora=dados.get("data_hora"),
            endereco_cliente=dados.get("endereco_cliente", ""),
            frete=dados.get("frete", 0.0),
            distancia_km=dados.get("distancia_km", 0.0),
        )
