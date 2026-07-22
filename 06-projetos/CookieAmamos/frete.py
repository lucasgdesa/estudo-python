import requests

from config import ORS_API_KEY, CIDADE_PADRAO

# Regras do frete: um valor mínimo pra distâncias curtas, e a partir daí um valor
# por quilômetro extra. Distâncias acima do limite são consideradas fora da área.
FRETE_MINIMO = 3.00              # cobrado pra qualquer entrega até FRETE_DISTANCIA_MINIMA_KM
FRETE_DISTANCIA_MINIMA_KM = 3    # até essa distância, cobra só o mínimo
FRETE_POR_KM_EXTRA = 1.10        # valor somado por km ALÉM da distância mínima
FRETE_DISTANCIA_MAXIMA_KM = 12   # acima disso, fora da área de entrega


# Calcula o valor do frete pra uma distância:
# - até FRETE_DISTANCIA_MINIMA_KM (3 km): cobra só o FRETE_MINIMO
# - de 3 km até FRETE_DISTANCIA_MAXIMA_KM (12 km): FRETE_MINIMO + R$1,10 por km que
#   passar de 3 km (ex: 5 km -> FRETE_MINIMO + 1.10 * (5 - 3))
# - acima de 12 km: devolve None (fora da área de entrega)
def valor_do_frete(distancia_km):
    if distancia_km > FRETE_DISTANCIA_MAXIMA_KM:
        return None

    if distancia_km <= FRETE_DISTANCIA_MINIMA_KM:
        return FRETE_MINIMO

    km_extras = distancia_km - FRETE_DISTANCIA_MINIMA_KM
    return FRETE_MINIMO + km_extras * FRETE_POR_KM_EXTRA


# Transforma um endereço em texto numa coordenada (latitude, longitude), usando o
# serviço de geocodificação do OpenRouteService. Devolve None se não achar o endereço.
#
# "perto_de", se informado, é uma coordenada (latitude, longitude) usada como "dica"
# pra API preferir resultados próximos dali. Sem isso, um endereço incompleto (sem
# bairro/cidade, tipo só "Estrada de Itacoatiara 357") pode ser confundido com uma rua
# de mesmo nome em qualquer lugar do mundo — foi exatamente isso que causou o erro que
# você viu: sem essa dica, o serviço achou uma rua parecida na Espanha.
def geocodificar(endereco, perto_de=None):
    params = {"api_key": ORS_API_KEY, "text": endereco, "size": 1}

    if perto_de is not None:
        latitude_referencia, longitude_referencia = perto_de
        params["focus.point.lat"] = latitude_referencia
        params["focus.point.lon"] = longitude_referencia

    resposta = requests.get(
        "https://api.openrouteservice.org/geocode/search",
        params=params,
        timeout=20,  # a API pode demorar alguns segundos pra responder; 10s às vezes era curto
    )
    resposta.raise_for_status()  # se a API devolver erro (ex: chave inválida), levanta uma exceção
    dados = resposta.json()

    if not dados["features"]:  # lista vazia = nenhum resultado encontrado pra esse endereço
        return None

    # O GeoJSON guarda a coordenada como [longitude, latitude], nessa ordem —
    # o contrário de como a gente costuma falar "latitude, longitude".
    longitude, latitude = dados["features"][0]["geometry"]["coordinates"]
    return latitude, longitude


# Calcula a distância de rota (as ruas de verdade, dirigindo) entre duas coordenadas.
# origem e destino são tuplas (latitude, longitude). Devolve a distância em quilômetros.
def calcular_distancia_km(origem, destino):
    lat_origem, lon_origem = origem
    lat_destino, lon_destino = destino

    resposta = requests.get(
        "https://api.openrouteservice.org/v2/directions/driving-car",
        params={
            "api_key": ORS_API_KEY,
            "start": f"{lon_origem},{lat_origem}",
            "end": f"{lon_destino},{lat_destino}",
        },
        timeout=20,  # a API pode demorar alguns segundos pra responder; 10s às vezes era curto
    )
    resposta.raise_for_status()
    dados = resposta.json()

    metros = dados["features"][0]["properties"]["summary"]["distance"]
    return metros / 1000


# Junta tudo: geocodifica os dois endereços, calcula a distância de rota entre eles,
# e consulta a TABELA_FRETE. Devolve sempre um dicionário:
# - em caso de sucesso: {"distancia_km": ..., "valor": ...}
# - em caso de falha: {"erro": "mensagem explicando o que aconteceu"}
# Assim quem chama (app.py) sempre sabe exatamente o que mostrar pro usuário,
# em vez de só saber que "algo deu errado".
def calcular_frete(endereco_origem, endereco_destino):
    # Checagem extra, só pra dar uma mensagem clara nesse caso específico (em vez de
    # deixar a API devolver um erro 401 genérico que cairia no except lá embaixo).
    if not ORS_API_KEY:
        return {"erro": "A chave da API do OpenRouteService ainda não foi configurada (veja config.py)."}

    try:
        origem = geocodificar(endereco_origem)

        if origem is None:
            return {"erro": "Não conseguimos encontrar o endereço da loja. Confira o endereço cadastrado no painel."}

        # Geocodifica o endereço do cliente com "origem" como dica de proximidade, e
        # completa o texto com a cidade padrão (o cliente não precisa digitar isso).
        destino = geocodificar(f"{endereco_destino}, {CIDADE_PADRAO}", perto_de=origem)

        if destino is None:
            return {"erro": "Não conseguimos encontrar esse endereço. Confira se está certo e tente de novo."}

        distancia_km = calcular_distancia_km(origem, destino)
    except requests.exceptions.RequestException:
        # Qualquer problema de rede/API (sem internet, chave inválida, serviço fora do
        # ar) cai aqui. Preferimos devolver uma mensagem e deixar quem chamou decidir
        # o que mostrar, em vez de quebrar o programa inteiro com um erro.
        return {"erro": "Não conseguimos calcular o frete agora. Tente de novo em instantes."}

    valor = valor_do_frete(distancia_km)

    if valor is None:
        return {
            "erro": f"Esse endereço fica a {distancia_km:.1f} km da loja, "
                    f"fora da nossa área de entrega (até {FRETE_DISTANCIA_MAXIMA_KM} km)."
        }

    return {"distancia_km": distancia_km, "valor": valor}
