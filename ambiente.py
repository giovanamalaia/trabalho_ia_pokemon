def carregar_mapa(caminho_arquivo):
    matriz_mapa = []
    coordenadas_alvos = {} # guardar as posições da origem, destino e ginásios
    
    # terrenos normais que não são alvos
    terrenos_padrao = {'F', 'R', 'M', 'A', '.'}
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        for y, linha in enumerate(arquivo):
            linha_limpa = list(linha.strip())
            if not linha_limpa:
                continue
                
            matriz_mapa.append(linha_limpa)
            for x, char in enumerate(linha_limpa):
                if char not in terrenos_padrao:
                    coordenadas_alvos[char] = (x, y)
                    
    return matriz_mapa, coordenadas_alvos

if __name__ == "__main__":
    mapa, alvos = carregar_mapa('mapa.txt')
    print(f"Tamanho do mapa: {len(mapa[0])}x{len(mapa)} (Esperado: 150x42)")
    print(f"Total de alvos encontrados: {len(alvos)} (Esperado: 26 -> Origem, Destino + 24 Ginásios)")
    print(f"Coordenada da Origem '1': {alvos.get('1')}")
    print(f"Coordenada do Destino 'U': {alvos.get('U')}")