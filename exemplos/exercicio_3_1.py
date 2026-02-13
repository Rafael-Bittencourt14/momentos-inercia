"""Exercício 3.1 (Perfil I) - validação rápida.

Configuração (igual à planilha):
- Mesa superior: 12 × 1.2 cm
- Alma: 0.8 × 12.6 cm
- Mesa inferior: 8 × 1.2 cm

Resultado esperado (aprox):
- I1 ~ 1246 cm^4
- I2 ~ 224.5 cm^4
"""

from __future__ import annotations

from momentos_inercia_v4 import SecaoComposta, Retangulo

def main():
    secao = SecaoComposta(unidade_comprimento="cm")

    secao.adicionar(Retangulo(base=12, altura=1.2, x=0, y=6.9))
    secao.adicionar(Retangulo(base=0.8, altura=12.6, x=0, y=0))
    secao.adicionar(Retangulo(base=8, altura=1.2, x=0, y=-6.9))

    r = secao.calcular(modo="quiet")
    print(secao.resumo(r))

if __name__ == "__main__":
    main()
