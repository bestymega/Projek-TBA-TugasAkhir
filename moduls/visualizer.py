"""
moduls/visualizer.py - Pembuat graf Graphviz untuk DFA dan NFA.

Menyediakan fungsi untuk menghasilkan objek graphviz.Digraph dari model
DFA dan NFA, dengan dukungan highlighting state aktif untuk animasi simulasi.
"""

import graphviz


# ── Warna Tema ─────────────────────────────────────────────────────────────────
_COLOR_BG       = "transparent"
_COLOR_FILL     = "#1a1a1a"
_COLOR_TEXT     = "#e0e0e0"
_COLOR_EDGE     = "#555555"
_COLOR_BORDER   = "#444444"
_COLOR_ACCEPT   = "#3a7d52"
_COLOR_START    = "#8b1a2c"
_COLOR_ACTIVE   = "#c0392b"        # State sedang aktif (animasi)
_COLOR_ACTIVE_BORDER = "#ff6b6b"   # Border state aktif


def _apply_graph_defaults(dot: graphviz.Digraph) -> None:
    """Terapkan atribut default untuk konsistensi styling."""
    dot.attr(rankdir="LR", bgcolor=_COLOR_BG, pad="0.4")
    dot.attr("node",
             style="filled",
             fillcolor=_COLOR_FILL,
             color=_COLOR_BORDER,
             fontcolor=_COLOR_TEXT,
             fontname="JetBrains Mono",
             fontsize="11",
             penwidth="1.5")
    dot.attr("edge",
             color=_COLOR_EDGE,
             fontcolor=_COLOR_TEXT,
             fontname="JetBrains Mono",
             fontsize="10",
             penwidth="1.2")


def generate_dfa_graph(dfa, active_states=None) -> graphviz.Digraph:
    """
    Buat Digraph untuk sebuah DFA.

    Args:
        dfa           : Objek DFA dari models/dfa.py.
        active_states : Set state yang sedang aktif (disorot untuk animasi).
                        Jika None, tidak ada highlighting.

    Returns:
        graphviz.Digraph yang siap dirender.
    """
    active_states = active_states or set()
    dot = graphviz.Digraph(engine="dot")
    _apply_graph_defaults(dot)

    # Node tersembunyi sebagai titik masuk panah start
    dot.node("__start__", shape="none", label="", width="0.1")

    for state in sorted(dfa.states, key=str):
        s = str(state)
        is_accept  = state in dfa.accept_states
        is_active  = state in active_states

        shape    = "doublecircle" if is_accept else "circle"
        if is_active:
            fill  = _COLOR_ACTIVE
            color = _COLOR_ACTIVE_BORDER
            pw    = "2.5"
        elif is_accept:
            fill  = "#0a1f12"
            color = _COLOR_ACCEPT
            pw    = "2.0"
        else:
            fill  = _COLOR_FILL
            color = _COLOR_BORDER
            pw    = "1.5"

        dot.node(s, shape=shape, fillcolor=fill, color=color, penwidth=pw)

        if state == dfa.start_state:
            dot.edge("__start__", s, color=_COLOR_START, penwidth="1.5", arrowsize="0.9")

    # Gabungkan label transisi dengan tujuan yang sama
    edge_map: dict = {}
    for (src, sym), dst in dfa.transitions.items():
        if dst is not None:
            key = (str(src), str(dst))
            edge_map.setdefault(key, []).append(str(sym))

    for (src, dst), syms in edge_map.items():
        label = ", ".join(sorted(syms))
        dot.edge(src, dst, label=f" {label} ")

    return dot


def generate_nfa_graph(nfa, active_states=None) -> graphviz.Digraph:
    """
    Buat Digraph untuk sebuah NFA.

    Args:
        nfa           : Objek NFA dari models/nfa.py.
        active_states : Set state yang sedang aktif (disorot untuk animasi).
                        Jika None, tidak ada highlighting.

    Returns:
        graphviz.Digraph yang siap dirender.
    """
    active_states = active_states or set()
    EPS = nfa.EPSILON
    dot = graphviz.Digraph(engine="dot")
    _apply_graph_defaults(dot)

    dot.node("__start__", shape="none", label="", width="0.1")

    for state in sorted(nfa.states, key=str):
        s = str(state)
        is_accept = state in nfa.accept_states
        is_active = state in active_states

        shape = "doublecircle" if is_accept else "circle"
        if is_active:
            fill  = _COLOR_ACTIVE
            color = _COLOR_ACTIVE_BORDER
            pw    = "2.5"
        elif is_accept:
            fill  = "#0a1f12"
            color = _COLOR_ACCEPT
            pw    = "2.0"
        else:
            fill  = _COLOR_FILL
            color = _COLOR_BORDER
            pw    = "1.5"

        dot.node(s, shape=shape, fillcolor=fill, color=color, penwidth=pw)

        if state == nfa.start_state:
            dot.edge("__start__", s, color=_COLOR_START, penwidth="1.5", arrowsize="0.9")

    # Gabungkan label transisi dengan sumber dan tujuan yang sama
    edge_map: dict = {}
    for (src, sym), targets in nfa.transitions.items():
        sym_lbl = "ε" if sym == EPS else str(sym)
        for dst in targets:
            key = (str(src), str(dst))
            edge_map.setdefault(key, []).append(sym_lbl)

    for (src, dst), syms in edge_map.items():
        label = ", ".join(sorted(syms))
        # Buat epsilon terlihat berbeda
        is_eps_only = all(s == "ε" for s in syms)
        style = "dashed" if is_eps_only else "solid"
        dot.edge(src, dst, label=f" {label} ", style=style)

    return dot
