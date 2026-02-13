from __future__ import annotations

import streamlit as st


def init_state() -> None:
    """Garante que as chaves mínimas existam."""
    if "figs" not in st.session_state:
        st.session_state["figs"] = []
    if "_next_id" not in st.session_state:
        st.session_state["_next_id"] = 1
    if "unidade" not in st.session_state:
        st.session_state["unidade"] = "cm"


def new_id() -> int:
    return int(st.session_state.get("_next_id", 1))


def bump_id() -> None:
    st.session_state["_next_id"] = new_id() + 1


def reset_state_deep(*, manter_unidade: str | None = None) -> None:
    """Limpeza 'profunda' do estado.

    - remove figuras
    - reseta contador de IDs
    - remove estados de widgets antigos (keys dinâmicas)
    - mantém a unidade selecionada (opcional)
    """
    unidade = manter_unidade if manter_unidade is not None else st.session_state.get("unidade", "cm")

    for k in list(st.session_state.keys()):
        del st.session_state[k]

    st.session_state["figs"] = []
    st.session_state["_next_id"] = 1
    st.session_state["unidade"] = unidade
