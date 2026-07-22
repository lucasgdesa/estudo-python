# Configurações que dependem de uma conta pessoal sua (chaves de API) ficam separadas
# do resto do código de propósito — assim fica claro o que é "lógica do sistema" e o
# que é "segredo/config da sua conta". Se um dia esse projeto for publicado num
# repositório público (GitHub etc.), esse arquivo é o tipo de coisa que NÃO deveria
# ser compartilhado (idealmente ficaria de fora do git, num .gitignore).

# Chave de API gratuita do OpenRouteService (usada em frete.py pra calcular
# distância de rota entre a loja e o endereço do cliente).
#
# Como conseguir a sua:
# 1. Crie uma conta grátis em https://openrouteservice.org/dev/#/signup
# 2. Depois de confirmar o e-mail, entre no painel (dashboard) e clique em
#    "Request a token" (ou "Create Token") pra gerar uma chave.
# 3. Copie a chave gerada e cole aqui embaixo, no lugar de "".
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjRmYzYyY2UxNmRmOTRmYmNhNDY1YTMyZGQ2ZjM2MWI0IiwiaCI6Im11cm11cjY0In0="

# Cidade/região onde a loja entrega. Esse texto é colado automaticamente no final do
# endereço que o cliente digita (ver frete.py), pra ajudar a geocodificação a não
# confundir a rua com uma de mesmo nome em outra cidade — ou até em outro país, que foi
# exatamente o que aconteceu com "Estrada de Itacoatiara": sem essa dica, o serviço
# geocodificou pra uma rua parecida na Espanha.
CIDADE_PADRAO = "Niterói, RJ, Brasil"

# Senha única pra acessar a área de administrador (painel, cardápio, histórico).
# Não tem "usuário" separado — é uma senha só, compartilhada, porque só você
# administra a loja. Quem souber essa senha entra; troque quando quiser.
SENHA_ADMIN = "Chaves1412"
