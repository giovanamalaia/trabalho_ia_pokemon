from ambiente import carregar_mapa
from interface import InterfaceGrafica

def main():
    print("carregar o mapa e coordenadas...")
    matriz_mapa, alvos = carregar_mapa('mapa.txt')
    
    custo_batalhas = 0 # mock ate tarefa 1 estar pronta
    origem = alvos.get('1')
    custo_rota = 0     # mock
    caminho = [origem] 
    visitados = []
    fronteira = []
    
    # calculo do custo total 
    custo_total = custo_rota + custo_batalhas
    
    # relatório final 
    print("\n" + "="*60)
    print("RELATÓRIO:")
    print(f"- Ordem de visita aos 24 ginásios: [mock]")
    print(f"- Pokémon usados em cada batalha: [mock]")
    print(f"- Energia final de cada Pokémon: [mock]")
    print(f"- Custo das Batalhas (C_batalhas): {custo_batalhas}")
    print(f"- Custo da Rota (C_rota): {custo_rota}")
    print(f"- Custo Total (C_total = C_rota + C_batalhas): {custo_total}")
    print("="*60 + "\n")
    
    print("abrindo interface gráfica...")
    ui = InterfaceGrafica(matriz_mapa, tamanho_celula=8)
    
    ui.desenhar_busca(
        posicao_agente=origem, 
        visitados=visitados, 
        fronteira=fronteira, 
        caminho_final=caminho
    )
    
    ui.manter_aberto()

if __name__ == "__main__":
    main()