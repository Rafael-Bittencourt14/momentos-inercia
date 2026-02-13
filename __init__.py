"""Momentos de Inércia - V4 (modular)

Pacote didático para cálculo de propriedades geométricas de seções compostas.

Uso rápido:
    from momentos_inercia_v4 import SecaoComposta, Retangulo
    secao = SecaoComposta(unidade_comprimento="cm")
    secao.adicionar(Retangulo(base=12, altura=1.2, x=0, y=6.9))
    resultados = secao.calcular(modo="quiet")  # ou modo="verbose"

"""

from .core.figuras import Retangulo, Circulo, TrianguloRetangulo, Semicirculo, QuartoCirculo
from .core.secao_composta import SecaoComposta

__all__ = [
    "Retangulo", "Circulo", "TrianguloRetangulo", "Semicirculo", "QuartoCirculo",
    "SecaoComposta",
]
