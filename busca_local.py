
import math
from copy import deepcopy
import random

from config import POKEMONS_PODER, GINASIOS_DIFICULDADE

POKEMONS = list(POKEMONS_PODER.keys())
GINASIOS = list(GINASIOS_DIFICULDADE.keys())

ENERGIA_INICIAL = 6


# =========================================================
# 1. CRIACAO E VALIDACAO DE SOLUCOES
# =========================================================

def criar_solucao_inicial():
    """
    Cria uma solucao inicial valida.
    Cada ginasio recebe pelo menos um Pokemon.
    """

    while True:
        solucao = [
            [random.choice(POKEMONS)]
            for _ in GINASIOS
        ]

        if solucao_valida(solucao):
            return solucao


def calcular_energia(solucao):
    """
    Cada Pokemon comeca com 6 pontos.
    Cada participacao em batalha consome 1 ponto.
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
    Verifica as restricoes de energia e de distribuicao.
    """

    if len(solucao) != len(GINASIOS):
        return False

    for batalha in solucao:

        if not batalha:
            return False

        if len(batalha) != len(set(batalha)):
            return False

        if any(pokemon not in POKEMONS for pokemon in batalha):
            return False

    energia = calcular_energia(solucao)

    if any(valor < 0 for valor in energia.values()):
        return False

    if not any(valor >= 1 for valor in energia.values()):
        return False

    return True


# =========================================================
# 2. CALCULO DOS CUSTOS
# =========================================================

def calcular_custo_batalha(ginasio, pokemons):
    """
    Tempo = dificuldade do ginasio / poder total dos Pokemon.
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
    Calcula o custo total das batalhas.
    Quanto menor o custo, melhor a solucao.
    """

    if not solucao_valida(solucao):
        return float("inf")

    return sum(
        calcular_custo_batalha(
            GINASIOS[indice],
            batalha
        )
        for indice, batalha in enumerate(solucao)
    )


# =========================================================
# 3. GERACAO DE VIZINHOS
# =========================================================

def gerar_vizinho(solucao):
    """
    Cria uma solucao vizinha usando uma das operacoes:
    - adicionar Pokemon;
    - remover Pokemon;
    - substituir Pokemon;
    - transferir Pokemon entre ginasios.
    """

    vizinho = deepcopy(solucao)

    operacao = random.choice([
        "adicionar",
        "remover",
        "substituir",
        "transferir"
    ])

    if operacao == "transferir":

        indice_origem = random.randrange(len(vizinho))
        indice_destino = random.randrange(len(vizinho))

        while indice_destino == indice_origem:
            indice_destino = random.randrange(len(vizinho))

        origem = vizinho[indice_origem]
        destino = vizinho[indice_destino]

        if len(origem) > 1:

            disponiveis = [
                pokemon
                for pokemon in origem
                if pokemon not in destino
            ]

            if disponiveis:
                pokemon = random.choice(disponiveis)

                origem.remove(pokemon)
                destino.append(pokemon)

        return vizinho

    indice = random.randrange(len(vizinho))
    batalha = vizinho[indice]

    if operacao == "adicionar":

        disponiveis = [
            pokemon
            for pokemon in POKEMONS
            if pokemon not in batalha
        ]

        if disponiveis:
            batalha.append(random.choice(disponiveis))

    elif operacao == "remover":

        if len(batalha) > 1:
            batalha.remove(random.choice(batalha))

    elif operacao == "substituir":

        disponiveis = [
            pokemon
            for pokemon in POKEMONS
            if pokemon not in batalha
        ]

        if batalha and disponiveis:

            remover = random.choice(batalha)
            adicionar = random.choice(disponiveis)

            batalha.remove(remover)
            batalha.append(adicionar)

    return vizinho


def gerar_vizinho_valido(solucao, max_tentativas=30):
    """
    Tenta encontrar um vizinho valido.
    Se nao encontrar, conserva a solucao original.
    """

    for _ in range(max_tentativas):

        vizinho = gerar_vizinho(solucao)

        if solucao_valida(vizinho):
            return vizinho

    return deepcopy(solucao)


# =========================================================
# 4. SIMULATED ANNEALING
# =========================================================

def simulated_annealing(
    solucao_inicial=None,
    max_iteracoes=50000,
    temperatura_inicial=50.0,
    temperatura_minima=0.01,
    taxa_resfriamento=0.99985
):
    """
    Explora o espaco de solucoes usando Simulated Annealing.

    Aceita solucoes melhores e, probabilisticamente,
    tambem pode aceitar solucoes piores.

    Retorna a melhor solucao encontrada durante a busca.
    """

    if solucao_inicial is None:
        solucao_atual = criar_solucao_inicial()
    else:
        if not solucao_valida(solucao_inicial):
            raise ValueError("A solucao inicial precisa ser valida.")

        solucao_atual = deepcopy(solucao_inicial)

    custo_atual = calcular_custo(solucao_atual)

    melhor_solucao = deepcopy(solucao_atual)
    melhor_custo = custo_atual

    temperatura = temperatura_inicial

    for _ in range(max_iteracoes):

        if temperatura < temperatura_minima:
            break

        vizinho = gerar_vizinho_valido(solucao_atual)
        custo_vizinho = calcular_custo(vizinho)

        diferenca = custo_vizinho - custo_atual

        if diferenca <= 0:

            solucao_atual = vizinho
            custo_atual = custo_vizinho

        else:

            probabilidade = math.exp(
                -diferenca / temperatura
            )

            if random.random() < probabilidade:
                solucao_atual = vizinho
                custo_atual = custo_vizinho

        if custo_atual < melhor_custo:

            melhor_solucao = deepcopy(solucao_atual)
            melhor_custo = custo_atual

        temperatura *= taxa_resfriamento

    return melhor_solucao, melhor_custo


# =========================================================
# 5. REFINAMENTO POR BUSCA LOCAL
# =========================================================

def refinar_solucao(
    solucao,
    max_iteracoes=1000,
    vizinhos_por_iteracao=50
):
    """
    Tenta melhorar a solucao encontrada pelo SA.

    Em cada rodada:
    1. Gera varios vizinhos validos.
    2. Identifica o vizinho de menor custo.
    3. Aceita a mudanca somente se houver melhoria.
    4. Para se nao encontrar uma melhoria na rodada.

    O resultado nunca tem custo maior que a solucao recebida.
    """

    melhor_solucao = deepcopy(solucao)
    melhor_custo = calcular_custo(melhor_solucao)

    for _ in range(max_iteracoes):

        melhor_vizinho = None
        custo_melhor_vizinho = melhor_custo

        for _ in range(vizinhos_por_iteracao):

            vizinho = gerar_vizinho_valido(melhor_solucao)
            custo_vizinho = calcular_custo(vizinho)

            if custo_vizinho < custo_melhor_vizinho:

                melhor_vizinho = vizinho
                custo_melhor_vizinho = custo_vizinho

        # Nenhum vizinho melhor foi encontrado.
        if melhor_vizinho is None:
            break

        # Avanca somente para uma solucao melhor.
        melhor_solucao = deepcopy(melhor_vizinho)
        melhor_custo = custo_melhor_vizinho

    return melhor_solucao, melhor_custo


# =========================================================
# 6. ALGORITMO HIBRIDO: SA + BUSCA LOCAL
# =========================================================

def algoritmo_hibrido(
    max_iteracoes_sa=50000,
    max_iteracoes_local=1000,
    vizinhos_por_iteracao=50
):
    """
    Executa o SA e depois refina a melhor solucao encontrada.

    A busca local recebe a melhor solucao do SA.
    """

    # Primeira etapa: exploracao com Simulated Annealing.
    solucao_sa, custo_sa = simulated_annealing(
        max_iteracoes=max_iteracoes_sa
    )

    # Segunda etapa: refinamento local.
    solucao_final, custo_final = refinar_solucao(
        solucao_sa,
        max_iteracoes=max_iteracoes_local,
        vizinhos_por_iteracao=vizinhos_por_iteracao
    )

    return solucao_final, custo_final


# =========================================================
# 7. EXPERIMENTOS
# =========================================================

def executar_experimentos(numero_execucoes=30):
    """
    Executa o algoritmo hibrido varias vezes.

    Retorna:
    - melhor solucao global encontrada nos experimentos;
    - melhor custo;
    - media dos custos finais;
    - desvio padrao amostral;
    - numero de execucoes.
    """

    if numero_execucoes < 1:
        raise ValueError(
            "O numero de execucoes deve ser pelo menos 1."
        )

    resultados = []

    melhor_solucao = None
    melhor_custo = float("inf")

    for execucao in range(numero_execucoes):

        solucao, custo = algoritmo_hibrido()

        resultados.append(custo)

        if custo < melhor_custo:

            melhor_custo = custo
            melhor_solucao = deepcopy(solucao)

        print(
            f"Execucao {execucao + 1}/{numero_execucoes} "
            f"| Custo final: {custo:.2f} "
            f"| Melhor ate agora: {melhor_custo:.2f}"
        )

    media = sum(resultados) / len(resultados)

    if len(resultados) > 1:

        desvio_padrao = math.sqrt(
            sum(
                (custo - media) ** 2
                for custo in resultados
            ) / (len(resultados) - 1)
        )

    else:
        desvio_padrao = 0.0

    return (
        melhor_solucao,
        melhor_custo,
        media,
        desvio_padrao,
        numero_execucoes
    )


# =========================================================
# 8. EXIBICAO DOS RESULTADOS
# =========================================================

def mostrar_resultado(
    solucao,
    custo_total,
    media,
    desvio_padrao,
    numero_execucoes
):
    """
    Exibe a melhor solucao e as estatisticas dos experimentos.
    """

    print("\n")
    print("=" * 60)
    print("RESULTADO DO ALGORITMO HIBRIDO (SA + BUSCA LOCAL)")
    print("=" * 60)

    print(f"Numero de execucoes: {numero_execucoes}")
    print(f"Melhor custo: {custo_total:.2f}")
    print(f"Media dos custos: {media:.2f}")
    print(f"Desvio padrao: {desvio_padrao:.2f}")

    print(
        "\nPokemon utilizados em cada ginasio: "
        f"(TOTAL = {len(GINASIOS)} ginasios)"
    )

    for indice, batalha in enumerate(solucao):

        ginasio = GINASIOS[indice]

        custo = calcular_custo_batalha(
            ginasio,
            batalha
        )

        print(
            f"Ginasio {ginasio}: "
            f"{', '.join(batalha)} "
            f"-> custo: {custo:.2f}"
        )

    energia_final = calcular_energia(solucao)

    print("\nEnergia final dos Pokemon:")

    for pokemon, energia in energia_final.items():
        print(f"{pokemon}: {energia}")

    print("=" * 60)


# =========================================================
# 9. EXECUCAO PRINCIPAL
# =========================================================

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
