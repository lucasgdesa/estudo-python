
from veiculo import veiculo

class moto(veiculo):
    def __init__(self, marca, modelo, tipo):
        super().__init__(marca, modelo)
        self.tipo = tipo

    def __str__(self):
        return f"{super().__str__()} - tipo: {self.tipo}"

    







