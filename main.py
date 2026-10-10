from ambiente import carregar_mapa
from interface import InterfaceGrafica
from busca_a_estrela import resolver_rota
from busca_local import executar_experimentos, calcular_energia, GINASIOS
import pygame

def main():
    print("carregar o mapa e coordenadas...")
    matriz_mapa, alvos = carregar_mapa('mapa.txt')

    origem = alvos.get('1')

    if origem is None:
        print("Erro: origem '1' não encontrada no mapa.")
        return

    print("\nExecutando busca local...")

    melhor_solucao, custo_batalhas, media, desvio_padrao, numero_execucoes = executar_experimentos(30)

    energia_final = calcular_energia(melhor_solucao)

    batalhas_por_ginasio = {ginasio: melhor_solucao[i] for i, ginasio in enumerate(GINASIOS)}

    print("\nExecutando A* para encontrar a rota...")

    resultado_rota = resolver_rota(matriz_mapa, alvos, imprimir_expandidos=False)

    ordem_ginasios = resultado_rota["ordem_ginasios"]
    caminho = resultado_rota["caminho"]
    custo_rota = resultado_rota["custo_rota"]

    visitados = resultado_rota["visitados"]
    fronteira = resultado_rota["fronteira"]
    custo_total = custo_rota + custo_batalhas

    
    # relatório final
    print("\n" + "=" * 60)
    print("RELATÓRIO:")

    print("\n- Ordem de visita aos 24 ginásios:")
    for i, ginasio in enumerate(ordem_ginasios, start=1):
        print(f"{i:2d}. Ginásio {ginasio}")

    print("\n- Pokémon usados em cada batalha:")
    for ginasio in ordem_ginasios:
        pokemons = batalhas_por_ginasio[ginasio]
        print(f"Ginásio {ginasio}: {', '.join(pokemons)}")

    print("\n- Energia final de cada Pokémon:")
    for pokemon, energia in energia_final.items():
        print(f"{pokemon}: {energia}")

    print(f"\n- Custo das Batalhas (C_batalhas): {custo_batalhas:.2f}")
    print(f"- Custo da Rota (C_rota): {custo_rota:.2f}")
    print(f"- Custo Total (C_total = C_rota + C_batalhas): {custo_total:.2f}")
    print("=" * 60)

    print("\nESTATÍSTICAS DA BUSCA LOCAL:")
    print(f"Número de execuções: {numero_execucoes}")
    print(f"Melhor custo das batalhas: {custo_batalhas:.2f}")
    print(f"Média dos custos: {media:.2f}")
    print(f"Desvio padrão: {desvio_padrao:.2f}")

    print("\nESTATÍSTICAS DO A*:")
    print(f"Estados expandidos no grid: {resultado_rota['estados_expandidos_grid']}")
    print(f"Estados expandidos na busca dos ginásios: {resultado_rota['estados_expandidos_ginasios']}")
    print(f"Tamanho do caminho encontrado: {len(caminho)} posições")
    print("=" * 70)

    
    print("Iniciando animação passo a passo do agente...")
    ui = InterfaceGrafica(matriz_mapa, tamanho_celula=8)
    
    caminho_percorrido = []
    visitados_parcial = []

    for passo in caminho:
        caminho_percorrido.append(passo)
        visitados_parcial.append(passo)
        
        ui.animar_passo(
            posicao_atual=passo,
            visitados=visitados_parcial,
            fronteira=fronteira,
            caminho_final=caminho_percorrido
        )
        pygame.time.delay(20)

    print("Animação concluída! Feche a janela para encerrar.")
    ui.manter_aberto()

if __name__ == "__main__":
    main()