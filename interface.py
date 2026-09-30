import pygame
import sys

CORES = {
    "M": (139, 69, 19),   # montanha (marrom)
    "A": (30, 144, 255),  # agua (azul)
    "F": (34, 139, 34),   # floresta (verde)
    "R": (128, 128, 128), # rochoso (cinza)
    ".": (245, 245, 245), # livre (branco)
    "1": (255, 215, 0),   # origem (amarelo)
    "U": (255, 0, 0),     # destino (vermelho)
    "AGENTE": (0, 0, 0)   # posição atual (preto)
}

CORES_ESTADOS = {
    "FRONTEIRA": (255, 165, 0),  # laranja: caminhos que está avaliando
    "VISITADO": (173, 216, 230), # azul: caminhos que já explorou
    "CAMINHO": (0, 255, 0)       # verde: a rota final encontrada
}

class InterfaceGrafica:
    def __init__(self, matriz_mapa, tamanho_celula=8):
        pygame.init()
        self.matriz = matriz_mapa
        self.tamanho_celula = tamanho_celula
        self.largura = len(matriz_mapa[0]) * tamanho_celula
        self.altura = len(matriz_mapa) * tamanho_celula
        
        self.tela = pygame.display.set_mode((self.largura, self.altura))
        pygame.display.set_caption("Rota Pokémon")

    def desenhar_busca(self, posicao_agente=None, visitados=None, fronteira=None, caminho_final=None):
        """
        Desenha o mapa base e sobrepõe as informações do algoritmo de busca.
        """
        visitados = visitados or []
        fronteira = fronteira or []
        caminho_final = caminho_final or []

        for y, linha in enumerate(self.matriz):
            for x, char in enumerate(linha):
                cor = CORES.get(char, (200, 200, 200))
                
                # ginásios em roxo 
                if char not in CORES and char.isalnum():
                    cor = (148, 0, 211) 

                pygame.draw.rect(
                    self.tela, 
                    cor, 
                    (x * self.tamanho_celula, y * self.tamanho_celula, self.tamanho_celula, self.tamanho_celula)
                )

        # estados já visitados
        for x, y in visitados:
            pygame.draw.rect(
                self.tela, 
                CORES_ESTADOS["VISITADO"], 
                (x * self.tamanho_celula, y * self.tamanho_celula, self.tamanho_celula, self.tamanho_celula)
            )

        # fronteira
        for x, y in fronteira:
            pygame.draw.rect(
                self.tela, 
                CORES_ESTADOS["FRONTEIRA"], 
                (x * self.tamanho_celula, y * self.tamanho_celula, self.tamanho_celula, self.tamanho_celula)
            )

        # rota final 
        for x, y in caminho_final:
            pygame.draw.rect(
                self.tela, 
                CORES_ESTADOS["CAMINHO"], 
                (x * self.tamanho_celula, y * self.tamanho_celula, self.tamanho_celula, self.tamanho_celula)
            )

        if posicao_agente:
            ax, ay = posicao_agente
            pygame.draw.rect(
                self.tela, 
                CORES["AGENTE"], 
                (ax * self.tamanho_celula, ay * self.tamanho_celula, self.tamanho_celula, self.tamanho_celula)
            )

        pygame.display.flip()

    def manter_aberto(self):
        executando = True
        while executando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    executando = False
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    from ambiente import carregar_mapa
    mapa, alvos = carregar_mapa('mapa.txt')
    
    ui = InterfaceGrafica(mapa, tamanho_celula=8)
    
    origem = alvos.get('1', (0,0))
    teste_visitados = [(origem[0]+1, origem[1]), (origem[0]+2, origem[1])]
    teste_fronteira = [(origem[0]+3, origem[1]), (origem[0]+2, origem[1]+1)]
    teste_caminho = [(origem[0], origem[1]), (origem[0]+1, origem[1]), (origem[0]+2, origem[1])]
    teste_agente = (origem[0]+2, origem[1])

    ui.desenhar_busca(
        posicao_agente=teste_agente,
        visitados=teste_visitados,
        fronteira=teste_fronteira,
        caminho_final=teste_caminho
    )
    
    ui.manter_aberto()