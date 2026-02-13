"""CLI simples para debug (LEGACY).

Este CLI é útil para:
- conferir cálculos do core rapidamente
- depurar sem depender da interface Streamlit

A UI principal do projeto é o Streamlit em: interface/app_streamlit.py
"""

from __future__ import annotations

from ..core.secao_composta import SecaoComposta
from ..core.figuras import Retangulo, Circulo, TrianguloRetangulo, Semicirculo, QuartoCirculo
from ..utils.validacao import ler_float, ler_bool_sim_nao, ler_sinal


def rodar_cli() -> None:
    print("=" * 70)
    print("MOMENTOS DE INÉRCIA - V4 (CLI)  [LEGACY/DEBUG]")
    print("=" * 70)

    unidade = input("Unidade de comprimento (ex: mm, cm, m) [cm]: ").strip() or "cm"
    secao = SecaoComposta(unidade_comprimento=unidade)

    while True:
        print("\nFiguras disponíveis:")
        print("1 - Retângulo")
        print("2 - Círculo")
        print("3 - Triângulo Retângulo")
        print("4 - Semicírculo")
        print("5 - Quarto de Círculo")
        print("6 - Calcular (verbose)")
        print("7 - Calcular (quiet) + resumo")
        print("8 - Remover figura")
        print("0 - Sair")

        op = input("Escolha: ").strip()

        if op == "0":
            break

        if op in {"1", "2", "3", "4", "5"}:
            furo = ler_bool_sim_nao("É um furo?")

            x = ler_float("x do centroide: ", permitir_zero=True, permitir_negativo=True)
            y = ler_float("y do centroide: ", permitir_zero=True, permitir_negativo=True)

            if op == "1":
                base = ler_float("Base: ", permitir_negativo=False)
                altura = ler_float("Altura: ", permitir_negativo=False)
                secao.adicionar(Retangulo(base=base, altura=altura, x=x, y=y, furo=furo))

            elif op == "2":
                raio = ler_float("Raio: ", permitir_negativo=False)
                secao.adicionar(Circulo(raio=raio, x=x, y=y, furo=furo))

            elif op == "3":
                base = ler_float("Base: ", permitir_negativo=False)
                altura = ler_float("Altura: ", permitir_negativo=False)
                sinal = ler_sinal()
                secao.adicionar(TrianguloRetangulo(base=base, altura=altura, x=x, y=y, sinal_ixy=sinal, furo=furo))

            elif op == "4":
                raio = ler_float("Raio: ", permitir_negativo=False)
                secao.adicionar(Semicirculo(raio=raio, x=x, y=y, furo=furo))

            elif op == "5":
                raio = ler_float("Raio: ", permitir_negativo=False)
                txt = input("Sinal do Ixy do 1/4 círculo (+1 ou -1) [-1]: ").strip()
                sinal = -1 if txt == "" else int(txt)
                secao.adicionar(QuartoCirculo(raio=raio, x=x, y=y, sinal_ixy=sinal, furo=furo))

            print("✅ Figura adicionada.")
            continue

        if op == "6":
            if not secao.figuras:
                print("⚠️ Nenhuma figura adicionada. Adicione pelo menos 1 figura antes de calcular.")
                continue
            r = secao.calcular(modo="verbose")
            print(secao.resumo(r))
            continue

        if op == "7":
            if not secao.figuras:
                print("⚠️ Nenhuma figura adicionada. Adicione pelo menos 1 figura antes de calcular.")
                continue
            r = secao.calcular(modo="quiet")
            print(secao.resumo(r))
            continue

        if op == "8":
            if not secao.figuras:
                print("⚠️ Não há figuras para remover.")
                continue

            print("\nFiguras na seção:")
            for i, fig in enumerate(secao.figuras, start=1):
                nome = getattr(fig, "nome", fig.__class__.__name__)
                tipo = "FURO" if getattr(fig, "furo", False) else "Sólido"
                x = getattr(fig, "x", 0.0)
                y = getattr(fig, "y", 0.0)
                print(f"{i} - {nome} [{tipo}] (x={x}, y={y})")

            idx_str = input("Digite o número da figura para remover (ou Enter para cancelar): ").strip()
            if not idx_str:
                print("✅ Remoção cancelada.")
                continue

            try:
                idx = int(idx_str)
                if idx < 1 or idx > len(secao.figuras):
                    print("❌ Índice inválido.")
                    continue
            except ValueError:
                print("❌ Digite um número válido.")
                continue

            removida = secao.figuras.pop(idx - 1)
            nome = getattr(removida, "nome", removida.__class__.__name__)
            print(f"🗑️ Figura removida: {nome}")
            continue

        print("❌ Opção inválida.")
