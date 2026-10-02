"""
A* da Pessoa 1: menor rota saindo de '1', passando pelos 24 ginásios e
terminando em 'U'.

Funciona em 3 degraus:
  1) a_estrela_grid       -> A* célula a célula no mapa (custos de terreno)
  2) calcular_distancias  -> usa o degrau 1 entre todos os pares de pontos
  3) a_estrela_ginasios   -> A* sobre a ORDEM de visita dos ginásios

POR QUE A HEURÍSTICA DO DEGRAU 3 É ADMISSÍVEL (nunca superestima):
  O que falta fazer é uma LINHA: sai do ponto atual, passa por todos os
  ginásios que faltam e termina em 'U'. Nessa linha, o ponto atual e o 'U'
  são as pontas (1 ligação cada) e cada ginásio tem 2 ligações. Ela custa
  pelo menos:
    a) a ligação mais barata do ponto atual até um ginásio que falta;
    b) + a Árvore Geradora Mínima (MST) entre os ginásios que faltam
       (toda forma de ligar pontos custa pelo menos a MST deles);
    c) + a ligação mais barata do 'U' até um ginásio que falta.
  Para deixar o palpite mais forte, cada ginásio ganha uma "penalidade"
  por ligação (limite de Held-Karp). Na rota real cada ginásio tem
  exatamente 2 ligações, então descontamos 2 x penalidade de cada um e o
  valor continua SEMPRE <= ao custo real que falta, para qualquer
  penalidade. Como a heurística nunca superestima, o A* garante a rota de
  menor custo (ótimo global).
"""

import heapq   
import math
import time   

from config import CUSTO_TERRENO, GINASIOS_DIFICULDADE

# Cada par é (dx, dy). No mapa, o y CRESCE PARA BAIXO,
# então (0, -1) é "subir uma linha".
MOVIMENTOS = [
    (0, -1),   # cima
    (0, 1),    # baixo
    (-1, 0),   # esquerda
    (1, 0),    # direita
]

ORIGEM = "1"
DESTINO = "U"

def custo_celula(mapa, x, y):
    return CUSTO_TERRENO.get(mapa[y][x], 1)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_estrela_grid(mapa, inicio, fim):
    """
    Encontra o caminho de MENOR CUSTO de 'inicio' até 'fim' no grid.

    Parâmetros:
        mapa   -> matriz vinda do ambiente.py (mapa[y][x])
        inicio -> tupla (x, y)
        fim    -> tupla (x, y)

    Retorna uma tupla (caminho, custo, expandidos, fronteira_final):
        caminho         -> lista de (x, y) do início até o fim, inclusive
        custo           -> soma dos custos das células em que ENTROU
                           (a célula inicial não é cobrada aqui)
        expandidos      -> células na ordem em que foram expandidas
                           (a interface pinta como "visitados")
        fronteira_final -> células que ainda estavam na fila quando achou o fim
                           (a interface pinta como "fronteira")

    Ideia do A*:
        Para cada célula n, f(n) = g(n) + h(n)
            g(n) = custo REAL já gasto do início até n
            h(n) = PALPITE de quanto falta de n até o fim (Manhattan)
        Sempre expandimos a célula com MENOR f. Assim gastamos esforço só
        nas direções promissoras, em vez de espalhar para todo lado.
    """
    altura = len(mapa)        # número de linhas (42)
    largura = len(mapa[0])    # número de colunas (150)

    fronteira = [(manhattan(inicio, fim), 0, inicio)]

    g = {inicio: 0}

    veio_de = {inicio: None} #de qual célula viemos para chegar em pos pelo melhor

    fechados = set()

    expandidos = []

    while fronteira:
        f_atual, g_atual, atual = heapq.heappop(fronteira)

        if atual in fechados:
            continue
        fechados.add(atual)
        expandidos.append(atual)

        if atual == fim:
            caminho = []
            while atual is not None:
                caminho.append(atual)
                atual = veio_de[atual]
            caminho.reverse()   # tava fim->início, agora fica início->fim

            fronteira_final = [pos for (_, _, pos) in fronteira if pos not in fechados]
            return caminho, g_atual, expandidos, fronteira_final

        # Cria os vizinhos (cima, baixo, esquerda, direita)
        x, y = atual
        for dx, dy in MOVIMENTOS:
            nx, ny = x + dx, y + dy

            # Ignora vizinhos fora do mapa
            if not (0 <= nx < largura and 0 <= ny < altura):
                continue

            vizinho = (nx, ny)

            # Custo de chegar no vizinho passando pela célula atual
            novo_g = g_atual + custo_celula(mapa, nx, ny)

            # Se é a primeira vez que vemos esse vizinho, ou se achamos um
            # caminho mais barato até ele, então atualiza e coloca na fronteira
            if vizinho not in g or novo_g < g[vizinho]:
                g[vizinho] = novo_g
                veio_de[vizinho] = atual
                f = novo_g + manhattan(vizinho, fim)
                heapq.heappush(fronteira, (f, novo_g, vizinho))

    # Se a fronteira esvaziou sem chegar no fim, não existe caminho
    return None, float("inf"), expandidos, []

def calcular_distancias(mapa, alvos):
    nomes = list(alvos.keys())   
    custo = {}
    caminhos = {}
    todos_expandidos = set()
    toda_fronteira = set()

    for i, a in enumerate(nomes):
        for b in nomes[i + 1:]:           # só pares com a "antes" de b
            pa, pb = alvos[a], alvos[b]
            cam, c, exp, fron = a_estrela_grid(mapa, pa, pb)

            # ida: a -> b
            custo[(a, b)] = c
            caminhos[(a, b)] = cam

            # mesmo caminho ao contrário
            custo[(b, a)] = c - custo_celula(mapa, *pb) + custo_celula(mapa, *pa)
            caminhos[(b, a)] = list(reversed(cam))

            todos_expandidos.update(exp)
            toda_fronteira.update(fron)

    toda_fronteira -= todos_expandidos  
    return custo, caminhos, todos_expandidos, toda_fronteira

def arvore_minima(pontos, custo, penalidade):
    """
    Árvore Geradora Mínima (algoritmo de Prim) ligando todos os 'pontos'.
    Cada ligação a-b custa custo[(a, b)] + penalidade[a] + penalidade[b].

    Retorna (custo_da_arvore, grau), onde grau[p] = quantas ligações
    o ponto p recebeu na árvore.
    """
    pontos = list(pontos)
    grau = {p: 0 for p in pontos}
    if len(pontos) <= 1:
        return 0, grau

    primeiro = pontos[0]
    # perto[p] = (menor ligação de p até a árvore, ponto da árvore que liga)
    perto = {p: (custo[(primeiro, p)] + penalidade[primeiro] + penalidade[p], primeiro)
             for p in pontos[1:]}
    total = 0

    while perto:
        escolhido = min(perto, key=lambda p: perto[p][0])
        d, pai = perto.pop(escolhido)
        total += d
        grau[escolhido] += 1
        grau[pai] += 1
        # atualiza a distância dos outros
        for p in perto:
            d = custo[(escolhido, p)] + penalidade[escolhido] + penalidade[p]
            if d < perto[p][0]:
                perto[p] = (d, escolhido)

    return total, grau


def limite_inferior(atual, faltam, custo, penalidade, destino=DESTINO):
    """
    Limite inferior para "sair de 'atual', passar por todos os 'faltam'
    e terminar em 'destino'".

    Esse trajeto é uma linha: 'atual' e 'destino' são as pontas (1 ligação
    cada) e cada ginásio do meio tem 2 ligações. Então ele custa pelo menos:
        ligação mais barata de 'atual' até um ginásio que falta
      + árvore mínima entre os ginásios que faltam
      + ligação mais barata do 'destino' até um ginásio que falta
    Com penalidades, cada ponto paga 'penalidade' por ligação. No trajeto
    real isso soma penalidade*grau, que descontamos no final.

    Retorna (limite, grau) - o grau é usado para ajustar as penalidades.
    """
    faltam = list(faltam)
    total, grau = arvore_minima(faltam, custo, penalidade)

    mais_perto_atual = min(faltam, key=lambda x: custo[(atual, x)] + penalidade[x])
    mais_perto_destino = min(faltam, key=lambda x: custo[(destino, x)] + penalidade[x])
    total += custo[(atual, mais_perto_atual)] + penalidade[atual] + penalidade[mais_perto_atual]
    total += custo[(destino, mais_perto_destino)] + penalidade[destino] + penalidade[mais_perto_destino]
    grau[mais_perto_atual] += 1
    grau[mais_perto_destino] += 1

    desconto = penalidade[atual] + penalidade[destino] + 2 * sum(penalidade[x] for x in faltam)
    return total - desconto, grau


def calcular_penalidades(custo, ginasios, origem=ORIGEM, destino=DESTINO, iteracoes=2000):
    """
    Ajusta as penalidades para o limite_inferior ficar o mais alto possível
    (limite de Held-Karp). A ideia: na rota real, todo ginásio tem
    exatamente 2 ligações. Se na árvore um ginásio ficou com MAIS de 2,
    ele fica "mais caro" (penalidade sobe); com MENOS de 2, fica mais
    barato. Repetindo isso, a árvore vai ficando parecida com uma rota.

    Qualquer penalidade gera um limite que nunca passa do custo real,
    então isso só deixa a heurística mais forte, sem perder a garantia.
    """
    penalidade = {p: 0.0 for p in list(ginasios) + [origem, destino]}
    melhor_valor = float("-inf")
    melhor = dict(penalidade)
    passo = 2.0

    for _ in range(iteracoes):
        valor, grau = limite_inferior(origem, ginasios, custo, penalidade, destino)
        if valor > melhor_valor:
            melhor_valor = valor
            melhor = dict(penalidade)
        if all(grau[x] == 2 for x in ginasios):
            break   # a árvore já virou uma rota: não dá para melhorar
        for x in ginasios:
            penalidade[x] += passo * (grau[x] - 2)
        passo *= 0.995

    return melhor


def a_estrela_ginasios(custo, ginasios, origem=ORIGEM, destino=DESTINO, imprimir=False):
    todos = frozenset(ginasios)
    penalidade = calcular_penalidades(custo, ginasios, origem, destino)

    # O mesmo conjunto "faltam" aparece em vários estados, então guardamos
    # a parte do limite que só depende dele.
    cache = {}

    def heuristica(atual, visitados):
        """
        h(estado) = limite_inferior(atual, ginásios que faltam) - ver acima.
        Admissível (nunca superestima). Explicação no topo do arquivo.
        """
        if atual == destino:
            return 0
        faltam = todos - visitados
        if not faltam:
            return custo[(atual, destino)]   # só falta ir para 'U'
        if faltam not in cache:
            arvore, _ = arvore_minima(faltam, custo, penalidade)
            ligacao_destino = min(custo[(destino, x)] + penalidade[x] for x in faltam)
            desconto = penalidade[destino] + 2 * sum(penalidade[x] for x in faltam)
            cache[faltam] = arvore + ligacao_destino - desconto
        ligacao_atual = min(custo[(atual, x)] + penalidade[x] for x in faltam)
        # os custos reais são inteiros, então podemos arredondar para cima
        return math.ceil(cache[faltam] + ligacao_atual - 1e-9)

    estado_inicial = (origem, frozenset())
    contador = 0
    fronteira = [(heuristica(origem, frozenset()), 0, contador, estado_inicial)]
    g = {estado_inicial: 0}
    veio_de = {estado_inicial: None}
    expandidos = []

    while fronteira:
        f_atual, g_atual, _, estado = heapq.heappop(fronteira)

        # Cópia antiga na fila (já achamos um caminho mais barato até este
        # estado depois que ela foi colocada): ignora.
        if g_atual > g[estado]:
            continue

        atual, visitados = estado
        expandidos.append((atual, visitados, g_atual, f_atual))
        if imprimir:
            print(f"  Expandido #{len(expandidos)}: em '{atual}', "
                  f"visitados {len(visitados)}/{len(todos)} "
                  f"{{{', '.join(sorted(visitados))}}}, g={g_atual}, f={f_atual}")

        if atual == destino:
            ordem = []
            while estado is not None:
                ordem.append(estado[0])      # estado[0] = ponto_atual
                estado = veio_de[estado]
            ordem.reverse()
            return ordem, g_atual, expandidos

        # ações possíveis a partir deste estado
        faltam = todos - visitados
        proximos = faltam if faltam else [destino]

        for prox in proximos:
            if prox == destino:
                novo_visitados = visitados
            else:
                novo_visitados = visitados | {prox}

            novo_estado = (prox, novo_visitados)
            novo_g = g_atual + custo[(atual, prox)]

            if novo_estado not in g or novo_g < g[novo_estado]:
                g[novo_estado] = novo_g
                veio_de[novo_estado] = estado
                f = novo_g + heuristica(prox, novo_visitados)
                contador += 1
                heapq.heappush(fronteira, (f, novo_g, contador, novo_estado))

    return None, float("inf"), expandidos


def resolver_rota(mapa, alvos, imprimir_expandidos=False):
    ginasios = list(GINASIOS_DIFICULDADE.keys())
    custo, caminhos, expandidos_grid, fronteira_grid = calcular_distancias(mapa, alvos)
    ordem, custo_trechos_total, expandidos_gin = a_estrela_ginasios(
        custo, ginasios, imprimir=imprimir_expandidos)
    caminho = [alvos[ORIGEM]]
    trechos = []

    for a, b in zip(ordem, ordem[1:]):
        caminho.extend(caminhos[(a, b)][1:])
        trechos.append((a, b, custo[(a, b)]))

    origem_x, origem_y = alvos[ORIGEM]
    custo_rota = custo_trechos_total + custo_celula(mapa, origem_x, origem_y)

    return {
        "ordem": ordem,
        "ordem_ginasios": ordem[1:-1],
        "caminho": caminho,
        "custo_rota": custo_rota,
        "custo_trechos": trechos,
        "visitados": list(expandidos_grid),
        "fronteira": list(fronteira_grid),
        "estados_expandidos_grid": len(expandidos_grid),
        "estados_expandidos_ginasios": len(expandidos_gin),
        "lista_estados_expandidos": expandidos_gin,
    }

if __name__ == "__main__":

    # Roda o A* no mapa real (mapa.txt)
    from ambiente import carregar_mapa
    mapa, alvos = carregar_mapa("mapa.txt")

    inicio = time.time()
    print("ESTADOS EXPANDIDOS (degrau 3):")
    r = resolver_rota(mapa, alvos, imprimir_expandidos=True)
    print()
    duracao = time.time() - inicio

    print("=" * 60)
    print("RESULTADO DO A* (ROTA)")
    print("=" * 60)
    print("Ordem de visita:", " -> ".join(r["ordem"]))
    print()
    print("Custo de cada trecho:")
    for a, b, c in r["custo_trechos"]:
        print(f"  {a} -> {b}: {c}")
    print()
    print(f"Custo da rota (C_rota): {r['custo_rota']}")
    print(f"Tamanho do caminho: {len(r['caminho'])} células")
    print(f"Células expandidas (degrau 1): {r['estados_expandidos_grid']}")
    print(f"Estados expandidos (degrau 3): {r['estados_expandidos_ginasios']}")
    print(f"Tempo: {duracao:.1f}s")
