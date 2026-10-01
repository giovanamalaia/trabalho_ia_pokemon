import math
from copy import deepcopy
import random

from config import POKEMONS_PODER, GINASIOS_DIFICULDADE

POKEMONS = list(POKEMONS_PODER.keys())
GINASIOS = list(GINASIOS_DIFICULDADE.keys())

ENERGIA_INICIAL = 6



def criar_solucao_inicial():
    """
    Cria uma solução inicial aleatória.

    Cada ginásio recebe pelo menos um Pokémon.
    A solução é uma lista com 24 posições:
    
        índice 0 -> ginásio 2
        índice 1 -> ginásio 3
        ...
        índice 23 -> ginásio T
    """

    solucao = []

    for _ in GINASIOS:

        # Escolhe pelo menos um Pokémon para a batalha
        pokemon = random.choice(POKEMONS)

        solucao.append([pokemon])

    return solucao


def calcular_energia(solucao):
    """
    Calcula quantas vezes cada Pokémon participou de batalhas
    e determina sua energia final.

    Cada Pokémon começa com 6 pontos.
    Cada participação consome 1 ponto.
    """

    energia = {
        pokemon: ENERGIA_INICIAL
        for pokemon in POKEMONS
    }

    for batalha in solucao:

        for pokemon in batalha:

            energia[pokemon] -= 1

    return energia



def solucao_valida(solucao):
    """
    Verifica se uma solução respeita as regras de energia.

    Regras:
    - nenhum Pokémon pode ficar com energia negativa;
    - pelo menos um Pokémon deve terminar com energia >= 1;
    - cada ginásio deve possuir pelo menos um Pokémon.
    """

    
    for batalha in solucao:

        if len(batalha) == 0:
            return False

    energia = calcular_energia(solucao)

    
    for valor in energia.values():

        if valor < 0:
            return False

    if not any(valor >= 1 for valor in energia.values()):
        return False

    return True



def calcular_custo_batalha(ginasio, pokemons):
    """
    Calcula o tempo de uma batalha.

    Fórmula:

        Tempo = dificuldade do ginásio /
                soma dos poderes dos Pokémon
    """

    dificuldade = GINASIOS_DIFICULDADE[ginasio]

    poder_total = sum(
        POKEMONS_PODER[pokemon]
        for pokemon in pokemons
    )

    if poder_total == 0:
        return float("inf")

    return dificuldade / poder_total



def calcular_custo(solucao):
    """
    Calcula o custo total das 24 batalhas.

    Quanto menor o custo, melhor a solução.
    """

    if not solucao_valida(solucao):
        return float("inf")

    custo_total = 0

    for indice, batalha in enumerate(solucao):

        ginasio = GINASIOS[indice]

        custo = calcular_custo_batalha(
            ginasio,
            batalha
        )

        custo_total += custo

    return custo_total



def gerar_vizinho(solucao):
    """
    Cria uma nova solução modificando apenas uma batalha.

    As possíveis alterações são:
    - adicionar um Pokémon;
    - remover um Pokémon;
    - substituir um Pokémon por outro.
    """

    vizinho = deepcopy(solucao)

    # Escolhe aleatoriamente um dos ginásios
    indice_batalha = random.randrange(len(vizinho))

    batalha = vizinho[indice_batalha]

    # Escolhe uma operação
    operacao = random.choice([
        "adicionar",
        "remover",
        "substituir"
    ])


    if operacao == "adicionar":

        disponiveis = [
            pokemon
            for pokemon in POKEMONS
            if pokemon not in batalha
        ]

        if disponiveis:

            pokemon = random.choice(disponiveis)

            batalha.append(pokemon)

    elif operacao == "remover":

        # Uma batalha nunca pode ficar sem Pokémon
        if len(batalha) > 1:

            pokemon = random.choice(batalha)

            batalha.remove(pokemon)

    elif operacao == "substituir":

        # Só podemos substituir se houver pelo menos
        # um Pokémon na batalha
        if len(batalha) > 0:

            disponiveis = [
                pokemon
                for pokemon in POKEMONS
                if pokemon not in batalha
            ]

            if disponiveis:

                pokemon_remover = random.choice(batalha)
                pokemon_adicionar = random.choice(disponiveis)

                batalha.remove(pokemon_remover)
                batalha.append(pokemon_adicionar)

    return vizinho


def hill_climbing(max_iteracoes=1000):
    """
    Executa o algoritmo Hill Climbing.

    O algoritmo começa com uma solução aleatória
    e tenta encontrar vizinhos com custo menor.

    Como estamos minimizando o tempo:

        custo menor = solução melhor
    """

    solucao_atual = criar_solucao_inicial()

    while not solucao_valida(solucao_atual):

        solucao_atual = criar_solucao_inicial()

    custo_atual = calcular_custo(solucao_atual)

    for _ in range(max_iteracoes):

        vizinho = gerar_vizinho(solucao_atual)

        # Ignora vizinhos inválidos
        if not solucao_valida(vizinho):
            continue

        custo_vizinho = calcular_custo(vizinho)

        # Se o vizinho for melhor, caminhamos para ele
        if custo_vizinho < custo_atual:

            solucao_atual = vizinho
            custo_atual = custo_vizinho

    return solucao_atual, custo_atual


def executar_experimentos(numero_execucoes=30):
    """
    Executa o Hill Climbing várias vezes.

    Retorna:
    - melhor solução;
    - melhor custo;
    - média dos custos;
    - desvio padrão;
    - número de execuções.
    """

    resultados = []

    melhor_solucao = None
    melhor_custo = float("inf")

    for _ in range(numero_execucoes):

        solucao, custo = hill_climbing()

        resultados.append(custo)

        if custo < melhor_custo:

            melhor_custo = custo
            melhor_solucao = solucao

    media = sum(resultados) / len(resultados)

    if len(resultados) > 1:

        desvio_padrao = math.sqrt(
            sum(
                (custo - media) ** 2
                for custo in resultados
            ) / (len(resultados) - 1)
        )

    else:

        desvio_padrao = 0

    return (
        melhor_solucao,
        melhor_custo,
        media,
        desvio_padrao,
        numero_execucoes
    )



def mostrar_resultado(
    solucao,
    custo_total,
    media,
    desvio_padrao,
    numero_execucoes
):
    """
    Mostra no terminal o resultado final da busca local.
    """

    print("\n")
    print("=" * 60)
    print("RESULTADO DA BUSCA LOCAL")
    print("=" * 60)

    print(f"Número de execuções: {numero_execucoes}")
    print(f"Melhor custo: {custo_total:.2f}")
    print(f"Média dos custos: {media:.2f}")
    print(f"Desvio padrão: {desvio_padrao:.2f}")

    print("\nPokémon utilizados em cada ginásio: (TOTAL = 24 ginásios)")

    for indice, batalha in enumerate(solucao):

        ginasio = GINASIOS[indice]

        custo = calcular_custo_batalha(
            ginasio,
            batalha
        )

        print(
            f"Ginásio {ginasio}: "
            f"{', '.join(batalha)} "
            f"-> custo: {custo:.2f}"
        )

    energia_final = calcular_energia(solucao)

    print("\nEnergia final dos Pokémon:")

    for pokemon, energia in energia_final.items():

        print(
            f"{pokemon}: {energia}"
        )

    print("=" * 60)


if __name__ == "__main__":

    (
        melhor_solucao,
        melhor_custo,
        media,
        desvio_padrao,
        numero_execucoes
    ) = executar_experimentos(30)

    mostrar_resultado(
        melhor_solucao,
        melhor_custo,
        media,
        desvio_padrao,
        numero_execucoes
    )