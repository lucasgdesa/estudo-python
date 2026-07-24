from veiculo import veiculo

class carro(veiculo):
    def __init__(self, marca, modelo, portas):
        super().__init__(marca, modelo)
        self.portas = portas

    def __str__(self):
        return f"{super().__str__()} - Portas: {self.portas}"








