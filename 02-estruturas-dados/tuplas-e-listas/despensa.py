
#Roberto está organizando sua despensa e quer verificar se determinados itens já estão armazenados antes de adicioná-los à lista de compras.
#Ajude Roberto a criar um programa que pergunte o item desejado e verifique se ele está na lista de itens disponíveis na despensa. Caso o item não esteja na lista, o programa deve informar que ele precisa ser comprado.


despensa = ['feijão', 'arroz', 'farinha']
#lista criada

item = input('pesquisar item na despensa: ')
if item in despensa:
    print(f'O item {item} tem na despensa.')
else:
    print(f'o item {item} precisa ser comprado.')
#pede o input e verifica se tem ou não na lista.
#para cada resposta um print é retornado.







