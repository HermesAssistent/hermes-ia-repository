class PromptFactory:

    def __init__(self, strategies):
        self.strategies = strategies

    def obter_strategy(self, tipo):
        tipo = tipo.upper()

        for s in self.strategies:
            if s.tipo_sinistro() == tipo:
                return s

        raise ValueError(f"Tipo de sinistro não suportado: {tipo}")
