"""Funções utilitárias de validação/entrada.

Observação:
- Para o modo 'biblioteca' (importando em outros scripts), você normalmente não usa input().
- Para o modo CLI (linha de comando), estas funções ajudam a ler números com validação.
"""

from __future__ import annotations

def ler_float(
    mensagem: str,
    *,
    permitir_zero: bool = False,
    permitir_negativo: bool = False,
) -> float:
    """Lê um float via input() com validação."""
    while True:
        try:
            valor = float(input(mensagem))
        except ValueError:
            print("❌ Digite apenas números (ex: 10 ou 10.5).")
            continue

        if (not permitir_zero) and valor == 0:
            print("❌ O valor não pode ser zero.")
            continue
        if (not permitir_negativo) and valor < 0:
            print("❌ O valor não pode ser negativo.")
            continue
        if (not permitir_zero) and (not permitir_negativo) and valor <= 0:
            print("❌ O valor deve ser maior que zero.")
            continue

        return valor


def ler_bool_sim_nao(mensagem: str) -> bool:
    """Lê sim/não e devolve True/False."""
    while True:
        resp = input(mensagem + " (s/n): ").strip().lower()
        if resp in {"s", "sim", "y", "yes"}:
            return True
        if resp in {"n", "nao", "não", "no"}:
            return False
        print("❌ Digite 's' para sim ou 'n' para não.")


def ler_sinal(mensagem: str = "Sinal do Ixy (+1 ou -1): ") -> int:
    """Lê +1 ou -1 para o sinal do Ixy em figuras não simétricas."""
    while True:
        try:
            sinal = int(input(mensagem))
        except ValueError:
            print("❌ Digite apenas +1 ou -1.")
            continue

        if sinal not in (1, -1):
            print("❌ Digite apenas +1 ou -1.")
            continue
        return sinal
