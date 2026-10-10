import pygame
import sys

CORES = {
    "M": (139, 69, 19),
    "A": (30, 144, 255),
    "F": (34, 139, 34),
    "R": (128, 128, 128),
    ".": (245, 245, 245),
    "1": (255, 215, 0),
    "U": (255, 0, 0),
    "AGENTE": (0, 0, 0)
}

CORES_ESTADOS = {
    "FRONTEIRA": (255, 165, 0),
    "VISITADO": (80, 150, 255),
    "CAMINHO": (0, 255, 0)
}


class InterfaceGrafica:
    def __init__(self, matriz_mapa, tamanho_celula=8):
        pygame.init()

        self.matriz = matriz_mapa
        self.tamanho_celula = tamanho_celula

        self.largura = len(matriz_mapa[0]) * tamanho_celula
        self.altura = len(matriz_mapa) * tamanho_celula

        self.tela = pygame.display.set_mode(
            (self.largura, self.altura)
        )

        pygame.display.set_caption("Rota Pokémon")

    def desenhar_mapa(self):
        for y, linha in enumerate(self.matriz):
            for x, char in enumerate(linha):
                cor = CORES.get(char, (200, 200, 200))

                if char not in CORES and char.isalnum():
                    cor = (148, 0, 211)

                pygame.draw.rect(
                    self.tela,
                    cor,
                    (
                        x * self.tamanho_celula,
                        y * self.tamanho_celula,
                        self.tamanho_celula,
                        self.tamanho_celula
                    )
                )

    def desenhar_visitados(self, visitados):
        camada = pygame.Surface(
            (self.largura, self.altura),
            pygame.SRCALPHA
        )

        for x, y in visitados:
            pygame.draw.circle(
                camada,
                (
                    CORES_ESTADOS["VISITADO"][0],
                    CORES_ESTADOS["VISITADO"][1],
                    CORES_ESTADOS["VISITADO"][2],
                    45
                ),
                (
                    x * self.tamanho_celula + self.tamanho_celula // 2,
                    y * self.tamanho_celula + self.tamanho_celula // 2
                ),
                1
            )

        self.tela.blit(camada, (0, 0))

    def desenhar_fronteira(self, fronteira):
        for x, y in fronteira:
            centro = (
                x * self.tamanho_celula + self.tamanho_celula // 2,
                y * self.tamanho_celula + self.tamanho_celula // 2
            )

            pygame.draw.circle(
                self.tela,
                CORES_ESTADOS["FRONTEIRA"],
                centro,
                2
            )

    def desenhar_caminho(self, caminho_final):
        if len(caminho_final) < 2:
            return

        pontos = []

        for x, y in caminho_final:
            pontos.append(
                (
                    x * self.tamanho_celula + self.tamanho_celula // 2,
                    y * self.tamanho_celula + self.tamanho_celula // 2
                )
            )

        pygame.draw.lines(
            self.tela,
            CORES_ESTADOS["CAMINHO"],
            False,
            pontos,
            4
        )

    def desenhar_agente(self, posicao_agente):
        if posicao_agente is None:
            return

        ax, ay = posicao_agente

        centro = (
            ax * self.tamanho_celula + self.tamanho_celula // 2,
            ay * self.tamanho_celula + self.tamanho_celula // 2
        )

        pygame.draw.circle(
            self.tela,
            CORES["AGENTE"],
            centro,
            max(2, self.tamanho_celula // 3)
        )

    def desenhar_busca(
        self,
        posicao_agente=None,
        visitados=None,
        fronteira=None,
        caminho_final=None
    ):
        visitados = visitados or []
        fronteira = fronteira or []
        caminho_final = caminho_final or []

        self.desenhar_mapa()
        self.desenhar_visitados(visitados)
        self.desenhar_fronteira(fronteira)
        self.desenhar_caminho(caminho_final)
        self.desenhar_agente(posicao_agente)

        pygame.display.flip()

    def manter_aberto(self):
        executando = True

        while executando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    executando = False

            pygame.display.flip()

        pygame.quit()

    def animar_passo(self, posicao_atual, visitados=None, fronteira=None, caminho_final=None):
        """
        Atualiza a tela em tempo real para cada passo do agente.
        """
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        visitados = visitados or []
        fronteira = fronteira or []
        caminho_final = caminho_final or []

        self.desenhar_mapa()
        self.desenhar_visitados(visitados)
        self.desenhar_fronteira(fronteira)
        self.desenhar_caminho(caminho_final)
        self.desenhar_agente(posicao_atual)

        pygame.display.flip()


if __name__ == "__main__":
    from ambiente import carregar_mapa

    mapa, alvos = carregar_mapa("mapa.txt")

    ui = InterfaceGrafica(
        mapa,
        tamanho_celula=8
    )

    origem = alvos.get("1", (0, 0))

    teste_visitados = [
        (origem[0] + 1, origem[1]),
        (origem[0] + 2, origem[1])
    ]

    teste_fronteira = [
        (origem[0] + 3, origem[1]),
        (origem[0] + 2, origem[1] + 1)
    ]

    teste_caminho = [
        (origem[0], origem[1]),
        (origem[0] + 1, origem[1]),
        (origem[0] + 2, origem[1]),
        (origem[0] + 3, origem[1]),
        (origem[0] + 3, origem[1] + 1)
    ]

    teste_agente = (
        origem[0] + 3,
        origem[1]
    )

    ui.desenhar_busca(
        posicao_agente=teste_agente,
        visitados=teste_visitados,
        fronteira=teste_fronteira,
        caminho_final=teste_caminho
    )

    ui.manter_aberto()