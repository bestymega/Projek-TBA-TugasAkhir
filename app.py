"""
app.py - DFA Command Center (Streamlit App)

Antarmuka utama untuk:
  1. DFA Simulator   — simulasi & animasi step-by-step
  2. Regex to NFA    — konversi Thompson Construction
  3. NFA Simulator   — simulasi epsilon-closure
  4. DFA Minimizer   — minimisasi dengan Table-Filling
  5. DFA Equivalence — pengecekan ekuivalensi dua DFA
"""

import io
import sys
import copy
import time

import streamlit as st

from models.dfa import DFA
from models.nfa import NFA as NFAModel
from moduls.dfa_minimizer import minimize_dfa
from moduls.dfa_equivalence import check_equivalence
from moduls.dfa_simulator import simulate_dfa
from moduls.regex_to_nfa import regex_to_nfa
from moduls.nfa_simulator import NFASimulator
from moduls.visualizer import generate_dfa_graph, generate_nfa_graph


# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DFA Command Center",
    page_icon="D",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --black:      #0B0B0B;
  --panel:      #111111;
  --card:       #1A1A1A;
  --input-bg:   #0B0B0B;
  --border:     #272727;
  --wine:       #8B1A2C;
  --wine-hover: #A31F35;
  --wine-dim:   #3D0B13;
  --white:      #F2F2F2;
  --gray:       #8A8A8A;
  --gray-dim:   #404040;
  --green:      #3A7D52;
  --green-text: #6DBF82;
  --green-bg:   #0A1F12;
}

*, html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  box-sizing: border-box;
}

.stApp { background: var(--black); }
.main .block-container { padding: 0 !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }

/* NAVBAR */
.navbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center;
  padding: 0 1.5rem; height: 54px;
}
.navbar-brand {
  font-size: 0.85rem; font-weight: 700;
  letter-spacing: 0.15em; text-transform: uppercase;
  color: var(--white);
}
.navbar-brand span {
  background: var(--wine); color: var(--white);
  padding: 2px 8px; border-radius: 3px;
  margin-right: 10px; font-size: 0.8rem;
}
.navbar-spacer { flex: 1; }

/* SIDENAV */
.sidenav-header {
  padding: 0 0 1rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
}
.sidenav-title {
  font-size: 0.7rem; font-weight: 700;
  letter-spacing: 0.12em; text-transform: uppercase;
  color: var(--gray);
}
.sidenav-sub {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem; color: var(--gray-dim); margin-top: 2px;
}

/* RADIO NAV */
div[data-testid="stRadio"] > label { display: none !important; }
div[role="radiogroup"] { gap: 2px !important; }
div[role="radiogroup"] > label {
  background: transparent !important;
  padding: 9px 10px !important;
  border-radius: 4px !important;
  border-left: 2px solid transparent !important;
  transition: all 0.12s ease;
  margin: 0 !important;
}
div[role="radiogroup"] > label:hover { background: var(--card) !important; }
div[role="radiogroup"] > label[data-checked="true"],
div[role="radiogroup"] > label[aria-checked="true"] {
  background: var(--wine-dim) !important;
  border-left: 2px solid var(--wine) !important;
}
div[role="radiogroup"] > label[data-checked="true"] p,
div[role="radiogroup"] > label[aria-checked="true"] p { color: var(--white) !important; }
div[role="radiogroup"] > label span[data-baseweb="radio"] { display: none !important; }
div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] { margin-left: 0 !important; }
div[role="radiogroup"] > label p {
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  color: var(--gray) !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
  margin: 0 !important;
}

/* INPUTS */
div[data-testid="stTextInput"] input {
  background: var(--input-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  color: var(--white) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.82rem !important;
  padding: 8px 12px !important;
  min-height: 38px !important;
}
div[data-testid="stTextInput"] input:focus {
  border-color: var(--wine) !important;
  box-shadow: 0 0 0 1px var(--wine) !important;
}
div[data-testid="stTextInput"] > label { display: none !important; }

/* SELECTBOX */
div[data-testid="stSelectbox"] > div > div {
  background: var(--input-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  color: var(--white) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.82rem !important;
  min-height: 38px !important;
}
div[data-testid="stSelectbox"] > label { display: none !important; }

/* MULTISELECT */
div[data-testid="stMultiSelect"] > div > div {
  background: var(--input-bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  color: var(--white) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.82rem !important;
  min-height: 38px !important;
}
div[data-testid="stMultiSelect"] > div > div:focus-within { border-color: var(--wine) !important; }
div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
  background: var(--wine-dim) !important;
  color: var(--white) !important;
  border: 1px solid var(--wine) !important;
  font-size: 0.72rem !important;
}
div[data-testid="stMultiSelect"] > label { display: none !important; }

/* BUTTONS */
div[data-testid="stButton"] button[kind="primary"] {
  background: var(--wine) !important;
  border: none !important; border-radius: 4px !important;
  color: var(--white) !important; font-weight: 600 !important;
  font-size: 0.75rem !important; letter-spacing: 0.07em !important;
  text-transform: uppercase !important; min-height: 40px !important;
}
div[data-testid="stButton"] button[kind="primary"]:hover { background: var(--wine-hover) !important; }
div[data-testid="stButton"] button[kind="primary"]:disabled {
  background: var(--gray-dim) !important;
  color: var(--gray) !important;
}
div[data-testid="stButton"] button[kind="secondary"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important; border-radius: 4px !important;
  color: var(--gray) !important; font-weight: 600 !important;
  font-size: 0.75rem !important; text-transform: uppercase !important;
  min-height: 40px !important;
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
  border-color: var(--gray) !important;
  color: var(--white) !important;
}

/* TYPOGRAPHY */
.field-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--gray); margin-bottom: 4px; margin-top: 0.9rem;
}
.section-title {
  font-size: 1rem; font-weight: 700;
  color: var(--white); margin-bottom: 1.2rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--border);
}
h1, h2, h3 { color: var(--white) !important; }
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* TRANSITION TABLE */
.trans-table {
  border: 1px solid var(--border);
  border-radius: 5px; overflow: hidden;
  margin: 0.5rem 0; width: 100%;
}
.trans-table table { width: 100%; border-collapse: collapse; }
.trans-table th {
  background: var(--card); color: var(--gray);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem; font-weight: 600;
  padding: 8px 12px; text-align: center;
  border-bottom: 1px solid var(--border);
  letter-spacing: 0.06em; text-transform: uppercase;
}
.trans-table td {
  color: var(--white); font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; padding: 8px 12px;
  text-align: center; border-bottom: 1px solid var(--border);
}
.trans-table tr:last-child td { border-bottom: none; }
.trans-table tr:hover td { background: var(--card); }
.td-start  { color: var(--wine-hover) !important; }
.td-accept { color: var(--green-text) !important; }
.td-dead   { color: var(--gray-dim) !important; }

/* STATE BADGES */
.badges-row {
  display: flex; flex-wrap: wrap; gap: 6px;
  justify-content: center; padding: 0.8rem 0;
}
.badge {
  display: inline-flex; font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem; font-weight: 600;
  padding: 4px 10px; border-radius: 3px;
  border: 1px solid var(--border);
  background: var(--card); color: var(--gray);
}
.badge-start  { border-color: var(--wine); color: var(--white); background: var(--wine-dim); }
.badge-accept { border-color: var(--green); color: var(--green-text); background: var(--green-bg); }
.badge-both   { border-color: var(--wine); color: var(--white); background: var(--wine-dim); }

/* RESULT BOXES */
.result-accept {
  background: var(--green-bg); border: 1px solid var(--green);
  border-left: 3px solid var(--green-text);
  border-radius: 4px; padding: 0.85rem 1rem;
  color: var(--green-text); font-size: 0.82rem;
  margin: 0.6rem 0; line-height: 1.5;
}
.result-reject {
  background: var(--wine-dim); border: 1px solid var(--wine);
  border-left: 3px solid var(--wine-hover);
  border-radius: 4px; padding: 0.85rem 1rem;
  color: var(--white); font-size: 0.82rem;
  margin: 0.6rem 0; line-height: 1.5;
}

/* LOG BOX */
.log-box {
  background: var(--input-bg); border: 1px solid var(--border);
  border-radius: 4px; padding: 0.8rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem; color: var(--gray);
  white-space: pre-wrap; max-height: 160px;
  overflow-y: auto; line-height: 1.7; margin-top: 6px;
}

/* INFO NOTE */
.info-note {
  border-top: 1px solid var(--border);
  padding-top: 0.8rem; margin-top: 1rem;
  font-size: 0.72rem; color: var(--gray); line-height: 1.6;
}

/* DISPLAY AREA */
.display-area {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 5px; min-height: 280px; padding: 1.2rem;
  margin-bottom: 0.8rem;
  display: flex; flex-direction: column;
  justify-content: center; align-items: center;
}
.idle-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem; color: var(--gray-dim);
  text-align: center; letter-spacing: 0.06em;
}

/* VERDICT BOX */
.verdict-yes {
  background: var(--green-bg); border: 1px solid var(--green);
  border-radius: 5px; padding: 1.5rem; text-align: center; color: var(--green-text);
}
.verdict-no {
  background: var(--wine-dim); border: 1px solid var(--wine);
  border-radius: 5px; padding: 1.5rem; text-align: center; color: var(--white);
}
.verdict-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--gray); margin-bottom: 4px;
}
.verdict-main { font-size: 1.1rem; font-weight: 700; letter-spacing: 0.05em; }
.verdict-sub  { font-size: 0.75rem; font-weight: 400; margin-top: 6px; opacity: 0.75; }

/* FORM TABLE */
.th-row {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem; font-weight: 600;
  color: var(--gray); text-transform: uppercase;
  letter-spacing: 0.06em; padding: 6px 0;
  border-bottom: 1px solid var(--border);
}
.state-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 600;
  color: var(--white); padding-top: 7px;
}
.state-label.is-start  { color: var(--wine-hover); }
.state-label.is-accept { color: var(--green-text); }
.state-label.is-both   { color: var(--wine-hover); }

/* STAT CARD */
.stat-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 5px; padding: 0.9rem; text-align: center;
}
.stat-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem; color: var(--gray);
  text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;
}
.stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.3rem; font-weight: 700; color: var(--white);
}

/* DFA TAG (untuk Equivalence) */
.dfa-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  padding: 2px 8px; border-radius: 3px;
  margin-bottom: 0.8rem; display: inline-block;
}
.dfa-tag-1 { background: var(--wine-dim); color: var(--wine-hover); border: 1px solid var(--wine); }
.dfa-tag-2 { background: var(--card); color: var(--gray); border: 1px solid var(--border); }

/* ANIMATION STATUS BAR */
.anim-status {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem; color: var(--gray);
  text-align: center; padding: 4px 0;
}
</style>
""", unsafe_allow_html=True)


# ── Helper Functions ───────────────────────────────────────────────────────────

def capture(fn, *args, **kwargs):
    """Jalankan fn, kembalikan (result, stdout_string)."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    result = fn(*args, **kwargs)
    sys.stdout = old
    return result, buf.getvalue()


def build_dfa(prefix: str, states: list, alphabet: list) -> DFA:
    """Bangun objek DFA dari session state Streamlit."""
    start_raw  = st.session_state.get(f"{prefix}start", "").strip()
    accept_raw = st.session_state.get(f"{prefix}accept", "").replace(",", " ").strip()
    dfa = DFA()

    for s in states:
        dfa.states.add(s)
    for a in alphabet:
        dfa.alphabet.add(a)
    if start_raw:
        dfa.set_start(start_raw)
    for a in accept_raw.split():
        if a in states:
            dfa.add_accept(a)
    for s in states:
        for sym in alphabet:
            val = st.session_state.get(f"{prefix}t_{s}_{sym}", "-")
            if val and val != "-":
                dfa.add_transition(s, sym, val)
    return dfa


def render_state_badges(states, start_state, accept_states) -> str:
    """Kembalikan HTML badge-badge state."""
    html = ""
    for s in sorted(states):
        is_s = s == start_state
        is_a = s in accept_states
        if is_s and is_a:
            html += f"<span class='badge badge-both'>-&gt;* {s}</span>"
        elif is_s:
            html += f"<span class='badge badge-start'>-&gt; {s}</span>"
        elif is_a:
            html += f"<span class='badge badge-accept'>* {s}</span>"
        else:
            html += f"<span class='badge'>{s}</span>"
    return f"<div class='badges-row'>{html}</div>"


def render_dfa_table(dfa) -> str:
    """Kembalikan HTML tabel transisi DFA."""
    alphabet = sorted(dfa.alphabet)
    states   = sorted(dfa.states)
    rows = ""
    for s in states:
        is_s = s == dfa.start_state
        is_a = s in dfa.accept_states
        if is_s and is_a:
            lbl, cls = f"-&gt;* {s}", "td-start"
        elif is_s:
            lbl, cls = f"-&gt; {s}", "td-start"
        elif is_a:
            lbl, cls = f"* {s}", "td-accept"
        else:
            lbl, cls = s, ""

        row = f"<tr><td class='{cls}' style='text-align:left;padding-left:12px'><b>{lbl}</b></td>"
        for sym in alphabet:
            ns = dfa.transitions.get((s, sym))
            if ns:
                nc = "td-accept" if ns in dfa.accept_states else ("td-start" if ns == dfa.start_state else "")
                row += f"<td class='{nc}'>{ns}</td>"
            else:
                row += "<td class='td-dead'>-</td>"
        rows += row + "</tr>"

    hdr = "<th style='text-align:left'>State</th>" + "".join(f"<th>{a}</th>" for a in alphabet)
    return f"<div class='trans-table'><table><tr>{hdr}</tr>{rows}</table></div>"


def render_nfa_table(nfa) -> str:
    """Kembalikan HTML tabel transisi NFA (dengan kolom epsilon)."""
    EPS      = "\u03b5"
    all_syms = sorted(nfa.alphabet) + [EPS]
    states   = sorted(nfa.states)
    rows = ""
    for s in states:
        is_s = s == nfa.start_state
        is_a = s in nfa.accept_states
        if is_s and is_a:
            lbl, cls = f"-&gt;* {s}", "td-start"
        elif is_s:
            lbl, cls = f"-&gt; {s}", "td-start"
        elif is_a:
            lbl, cls = f"* {s}", "td-accept"
        else:
            lbl, cls = str(s), ""

        row = f"<tr><td class='{cls}' style='text-align:left;padding-left:12px'><b>{lbl}</b></td>"
        for sym in all_syms:
            targets = nfa.transitions.get((s, sym), set())
            if targets:
                cell = "{" + ", ".join(str(t) for t in sorted(targets)) + "}"
                row += f"<td>{cell}</td>"
            else:
                row += "<td class='td-dead'>-</td>"
        rows += row + "</tr>"

    hdr = "<th style='text-align:left'>State</th>" + "".join(
        "<th>&epsilon;</th>" if sym == EPS else f"<th>{sym}</th>"
        for sym in all_syms
    )
    return f"<div class='trans-table'><table><tr>{hdr}</tr>{rows}</table></div>"


def dfa_config_form(prefix: str):
    """
    Render form konfigurasi DFA.
    Mengembalikan (states, alphabet, is_ready).
    """
    st.markdown("<div class='section-title'>Configuration</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='field-label'>States</div>", unsafe_allow_html=True)
        st.text_input("s", key=f"{prefix}states_raw", placeholder="q0, q1, q2", label_visibility="collapsed")
        st.markdown("<div class='field-label'>Start State</div>", unsafe_allow_html=True)
        st.text_input("st", key=f"{prefix}start", placeholder="q0", label_visibility="collapsed")
    with c2:
        st.markdown("<div class='field-label'>Alphabet</div>", unsafe_allow_html=True)
        st.text_input("a", key=f"{prefix}alpha_raw", placeholder="a, b", label_visibility="collapsed")
        st.markdown("<div class='field-label'>Accept States</div>", unsafe_allow_html=True)
        st.text_input("ac", key=f"{prefix}accept", placeholder="q1", label_visibility="collapsed")

    states_raw = st.session_state.get(f"{prefix}states_raw", "").replace(",", " ").strip()
    alpha_raw  = st.session_state.get(f"{prefix}alpha_raw",  "").replace(",", " ").strip()

    if not states_raw or not alpha_raw:
        st.markdown("""
        <div class='info-note'>
          Fill in states and alphabet to configure transitions.
          DFA requires exactly one transition per symbol for each state.
        </div>""", unsafe_allow_html=True)
        return [], [], False

    states   = states_raw.split()
    alphabet = alpha_raw.split()
    options  = ["-"] + states

    # Bersihkan nilai selectbox yang sudah tidak valid
    for s in states:
        for sym in alphabet:
            key = f"{prefix}t_{s}_{sym}"
            if key in st.session_state and st.session_state[key] not in options:
                del st.session_state[key]

    st.markdown("<div class='field-label' style='margin-top:1.2rem'>Transition Function</div>", unsafe_allow_html=True)

    start_raw  = st.session_state.get(f"{prefix}start", "").strip()
    accept_set = set(st.session_state.get(f"{prefix}accept", "").replace(",", " ").split())

    # Header tabel
    hcols = st.columns([1.5] + [1] * len(alphabet))
    with hcols[0]:
        st.markdown("<div class='th-row'>State</div>", unsafe_allow_html=True)
    for i, sym in enumerate(alphabet):
        with hcols[i + 1]:
            st.markdown(f"<div class='th-row' style='text-align:center'>{sym.upper()}</div>", unsafe_allow_html=True)

    # Baris-baris transisi
    for s in states:
        is_s = s == start_raw
        is_a = s in accept_set
        if is_s and is_a:
            cls, lbl = "is-both",   f"-&gt;* {s}"
        elif is_s:
            cls, lbl = "is-start",  f"-&gt; {s}"
        elif is_a:
            cls, lbl = "is-accept", f"* {s}"
        else:
            cls, lbl = "",          s

        rcols = st.columns([1.5] + [1] * len(alphabet))
        with rcols[0]:
            st.markdown(f"<div class='state-label {cls}'>{lbl}</div>", unsafe_allow_html=True)
        for i, sym in enumerate(alphabet):
            with rcols[i + 1]:
                st.selectbox("x", options, key=f"{prefix}t_{s}_{sym}", label_visibility="collapsed")

    return states, alphabet, True


def animate_dfa(dfa: DFA, input_string: str, graph_placeholder, status_placeholder):
    """
    Animasi simulasi DFA step-by-step.
    Setiap langkah: sorot state aktif di graf, lalu tunggu sebentar.
    Mengembalikan (accepted: bool, log: str).
    """
    current = dfa.start_state
    log_lines = [f"Input : '{input_string}'", f"Start : {current}"]

    # Tampilkan state awal
    graph_placeholder.graphviz_chart(
        generate_dfa_graph(dfa, active_states={current}),
        use_container_width=True
    )
    status_placeholder.markdown(
        f"<div class='anim-status'>State: <b>{current}</b> | Membaca...</div>",
        unsafe_allow_html=True
    )
    time.sleep(0.7)

    for symbol in input_string:
        if symbol not in dfa.alphabet:
            log_lines.append(f"ERROR: simbol '{symbol}' tidak ada di alphabet!")
            break

        next_state = dfa.get_next_state(current, symbol)
        if next_state is None:
            log_lines.append(f"Step  : {current} --({symbol})--> DEAD STATE")
            log_lines.append("Result: REJECTED")
            graph_placeholder.graphviz_chart(
                generate_dfa_graph(dfa, active_states=set()),
                use_container_width=True
            )
            status_placeholder.markdown(
                "<div class='anim-status' style='color:#A31F35'>Dead state — ditolak.</div>",
                unsafe_allow_html=True
            )
            return False, "\n".join(log_lines)

        log_lines.append(f"Step  : {current} --({symbol})--> {next_state}")
        current = next_state

        graph_placeholder.graphviz_chart(
            generate_dfa_graph(dfa, active_states={current}),
            use_container_width=True
        )
        status_placeholder.markdown(
            f"<div class='anim-status'>Baca '<b>{symbol}</b>' → state: <b>{current}</b></div>",
            unsafe_allow_html=True
        )
        time.sleep(0.7)

    accepted = current in dfa.accept_states
    log_lines.append(f"End   : {current}")
    log_lines.append(f"Result: {'ACCEPTED' if accepted else 'REJECTED'}")

    # Sorot warna akhir (accept=hijau, reject=merah)
    if accepted:
        final_active = {current}
        status_text  = f"<div class='anim-status' style='color:#6DBF82'>Diterima di state <b>{current}</b></div>"
    else:
        final_active = set()
        status_text  = f"<div class='anim-status' style='color:#A31F35'>Ditolak di state <b>{current}</b></div>"

    graph_placeholder.graphviz_chart(
        generate_dfa_graph(dfa, active_states=final_active),
        use_container_width=True
    )
    status_placeholder.markdown(status_text, unsafe_allow_html=True)

    return accepted, "\n".join(log_lines)


def animate_nfa(nfa, input_string: str, graph_placeholder, status_placeholder):
    """
    Animasi simulasi NFA step-by-step menggunakan epsilon-closure.
    Mengembalikan (accepted: bool, log: str).
    """
    sim = NFASimulator()
    log_lines = [f"Input : '{input_string}'"]

    current_states = sim.epsilon_closure(nfa, {nfa.start_state})
    log_lines.append(f"ε-closure awal: {sorted(current_states)}")

    graph_placeholder.graphviz_chart(
        generate_nfa_graph(nfa, active_states=current_states),
        use_container_width=True
    )
    status_placeholder.markdown(
        f"<div class='anim-status'>Initial ε-closure: <b>{sorted(current_states)}</b></div>",
        unsafe_allow_html=True
    )
    time.sleep(0.7)

    for symbol in input_string:
        if symbol not in nfa.alphabet:
            log_lines.append(f"ERROR: simbol '{symbol}' tidak ada di alphabet!")
            break

        next_raw       = sim.move(nfa, current_states, symbol)
        current_states = sim.epsilon_closure(nfa, next_raw)

        log_lines.append(f"Baca '{symbol}' → move: {sorted(next_raw)} → ε-closure: {sorted(current_states)}")

        graph_placeholder.graphviz_chart(
            generate_nfa_graph(nfa, active_states=current_states),
            use_container_width=True
        )
        status_placeholder.markdown(
            f"<div class='anim-status'>Baca '<b>{symbol}</b>' → states: <b>{sorted(current_states)}</b></div>",
            unsafe_allow_html=True
        )
        time.sleep(0.7)

    accepted = bool(current_states & nfa.accept_states)
    log_lines.append(f"Final states : {sorted(current_states)}")
    log_lines.append(f"Accept states: {sorted(nfa.accept_states)}")
    log_lines.append(f"Result       : {'ACCEPTED' if accepted else 'REJECTED'}")

    final_active = current_states if accepted else set()
    status_text  = (
        f"<div class='anim-status' style='color:#6DBF82'>Diterima — states akhir: <b>{sorted(current_states)}</b></div>"
        if accepted else
        f"<div class='anim-status' style='color:#A31F35'>Ditolak — tidak ada state akhir yang cocok.</div>"
    )
    graph_placeholder.graphviz_chart(
        generate_nfa_graph(nfa, active_states=final_active),
        use_container_width=True
    )
    status_placeholder.markdown(status_text, unsafe_allow_html=True)

    return accepted, "\n".join(log_lines)


# ── Navbar ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='navbar'>
  <div class='navbar-brand'><span>DFA</span> Command Center</div>
  <div class='navbar-spacer'></div>
</div>
<div style='height:54px'></div>
""", unsafe_allow_html=True)


# ── Layout Utama ───────────────────────────────────────────────────────────────
nav_col, content_col = st.columns([1, 4.5], gap="large")

with nav_col:
    st.markdown("""
    <div class='sidenav-header'>
      <div class='sidenav-title'>Menu</div>
      <div class='sidenav-sub'>TBA / Tugas Akhir</div>
    </div>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "nav",
        ["DFA Simulator", "Regex to NFA", "NFA Simulator", "DFA Minimizer", "DFA Equivalence"],
        label_visibility="collapsed",
    )


# ── Content ────────────────────────────────────────────────────────────────────
with content_col:
    st.markdown("<div style='padding-top:1rem'></div>", unsafe_allow_html=True)

    # ── 1. DFA SIMULATOR ──────────────────────────────────────────────────────
    if menu == "DFA Simulator":
        left, right = st.columns([1, 1.8], gap="large")

        with left:
            states, alphabet, ready = dfa_config_form("sim_")
            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

            bc1, bc2 = st.columns([4, 1])
            with bc1:
                deploy = st.button("Deploy DFA", use_container_width=True, type="primary", disabled=not ready)
            with bc2:
                if st.button("Reset", use_container_width=True, type="secondary", key="sim_reset"):
                    for k in list(st.session_state.keys()):
                        if k.startswith("sim_"):
                            del st.session_state[k]
                    st.rerun()

        with right:
            st.markdown("<div class='section-title'>DFA Visualization</div>", unsafe_allow_html=True)

            if deploy and ready:
                dfa = build_dfa("sim_", states, alphabet)
                st.session_state["sim_dfa"]   = dfa
                st.session_state["sim_ready"] = True

            graph_ph  = st.empty()
            status_ph = st.empty()

            if st.session_state.get("sim_ready"):
                dfa = st.session_state["sim_dfa"]
                graph_ph.graphviz_chart(generate_dfa_graph(dfa), use_container_width=True)

                content = render_state_badges(dfa.states, dfa.start_state, dfa.accept_states)
                content += render_dfa_table(dfa)
                st.markdown(f"<div class='display-area'>{content}</div>", unsafe_allow_html=True)

                st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)
                sc1, sc2 = st.columns([3, 1.2])
                with sc1:
                    test_str = st.text_input(
                        "test", placeholder="Enter string to test...",
                        key="sim_test_str", label_visibility="collapsed"
                    )
                with sc2:
                    run = st.button("Run", type="primary", use_container_width=True, key="sim_run")

                if run:
                    label = f'"{test_str}"' if test_str else "empty string"
                    accepted, log = animate_dfa(dfa, test_str, graph_ph, status_ph)
                    if accepted:
                        st.markdown(f"<div class='result-accept'><b>Accepted</b> &mdash; {label}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='result-reject'><b>Rejected</b> &mdash; {label}</div>", unsafe_allow_html=True)
                    st.markdown("<div class='field-label' style='margin-top:0.8rem'>Execution Log</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='log-box'>{log.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

            else:
                graph_ph.markdown("<div class='display-area'><div class='idle-text'>Deploy a DFA to view it here.</div></div>", unsafe_allow_html=True)

    # ── 2. REGEX TO NFA ───────────────────────────────────────────────────────
    elif menu == "Regex to NFA":
        left, right = st.columns([1, 1.8], gap="large")

        with left:
            st.markdown("<div class='section-title'>Regex Configuration</div>", unsafe_allow_html=True)
            st.markdown("<div class='field-label'>Regular Expression</div>", unsafe_allow_html=True)
            regex_input = st.text_input(
                "reg", placeholder="(a|b)*abb",
                key="regex_in", label_visibility="collapsed"
            )
            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
            gen_btn = st.button("Generate NFA", use_container_width=True, type="primary")

            st.markdown("""
            <div class='info-note'>
              Converts the regular expression to an NFA using Thompson Construction.<br>
              Supported: letters (a-z), union (|), Kleene star (*), parentheses.
            </div>""", unsafe_allow_html=True)

        with right:
            st.markdown("<div class='section-title'>NFA Visualization</div>", unsafe_allow_html=True)

            if gen_btn and regex_input:
                try:
                    nfa = regex_to_nfa(regex_input)
                    st.session_state["regex_nfa"]   = nfa
                    st.session_state["regex_input"] = regex_input
                    st.session_state["regex_ready"] = True
                    st.session_state.pop("regex_error", None)
                except Exception as e:
                    st.session_state["regex_error"] = str(e)
                    st.session_state["regex_ready"] = False

            graph_ph  = st.empty()
            status_ph = st.empty()

            if st.session_state.get("regex_ready"):
                nfa   = st.session_state["regex_nfa"]
                regex = st.session_state["regex_input"]
                graph_ph.graphviz_chart(generate_nfa_graph(nfa), use_container_width=True)

                content  = f"<div style='font-family:JetBrains Mono;color:var(--wine-hover);font-size:1rem;font-weight:700;margin-bottom:0.8rem;text-align:center'>{regex}</div>"
                content += render_state_badges(nfa.states, nfa.start_state, nfa.accept_states)
                content += render_nfa_table(nfa)
                st.markdown(f"<div class='display-area'>{content}</div>", unsafe_allow_html=True)

                st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)
                rc1, rc2 = st.columns([3, 1.2])
                with rc1:
                    test_regex = st.text_input(
                        "tregex", placeholder="Enter string to test...",
                        key="regex_test_str", label_visibility="collapsed"
                    )
                with rc2:
                    run_regex = st.button("Run", type="primary", use_container_width=True, key="regex_run")

                if run_regex:
                    label = f'"{test_regex}"' if test_regex else "empty string"
                    try:
                        accepted, log = animate_nfa(nfa, test_regex, graph_ph, status_ph)
                        if accepted:
                            st.markdown(f"<div class='result-accept'><b>Accepted</b> &mdash; {label}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='result-reject'><b>Rejected</b> &mdash; {label}</div>", unsafe_allow_html=True)
                        st.markdown("<div class='field-label' style='margin-top:0.8rem'>Simulation Log</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='log-box'>{log.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    except ValueError as e:
                        st.markdown(f"<div class='result-reject'><b>Error:</b> {e}</div>", unsafe_allow_html=True)

            elif st.session_state.get("regex_error"):
                content = f"<div style='color:var(--wine-hover);font-family:JetBrains Mono;font-size:0.82rem'>Error: {st.session_state['regex_error']}</div>"
                graph_ph.markdown(f"<div class='display-area'>{content}</div>", unsafe_allow_html=True)
            else:
                graph_ph.markdown("<div class='display-area'><div class='idle-text'>Enter a regex and click Generate NFA.</div></div>", unsafe_allow_html=True)

    # ── 3. NFA SIMULATOR ──────────────────────────────────────────────────────
    elif menu == "NFA Simulator":
        left, right = st.columns([1, 1.8], gap="large")

        with left:
            st.markdown("<div class='section-title'>NFA Configuration</div>", unsafe_allow_html=True)

            st.markdown("<div class='field-label'>States</div>", unsafe_allow_html=True)
            st.text_input("ns", key="nsim_states", placeholder="q0, q1, q2, q3", label_visibility="collapsed")

            nc1, nc2 = st.columns(2)
            with nc1:
                st.markdown("<div class='field-label'>Alphabet</div>", unsafe_allow_html=True)
                st.text_input("na", key="nsim_alpha", placeholder="a, b", label_visibility="collapsed")
            with nc2:
                st.markdown("<div class='field-label'>Start State</div>", unsafe_allow_html=True)
                st.text_input("nst", key="nsim_start", placeholder="q0", label_visibility="collapsed")

            st.markdown("<div class='field-label'>Accept States</div>", unsafe_allow_html=True)
            st.text_input("nac", key="nsim_accept", placeholder="q3", label_visibility="collapsed")

            # Parse input
            nsim_states_raw = st.session_state.get("nsim_states", "").replace(",", " ").strip()
            nsim_alpha_raw  = st.session_state.get("nsim_alpha",  "").replace(",", " ").strip()
            nsim_start      = st.session_state.get("nsim_start",  "").strip()
            nsim_accept_raw = st.session_state.get("nsim_accept", "").replace(",", " ").strip()

            nsim_states_list = nsim_states_raw.split() if nsim_states_raw else []
            nsim_alpha_list  = nsim_alpha_raw.split()  if nsim_alpha_raw  else []
            nsim_accept_set  = set(nsim_accept_raw.split())
            nsim_ready       = bool(nsim_states_raw and nsim_alpha_raw and nsim_start)

            EPS          = "\u03b5"
            all_syms_nfa = nsim_alpha_list + [EPS]

            if nsim_ready:
                st.markdown("<div class='field-label' style='margin-top:1.2rem'>TABEL FUNGSI TRANSISI NFA (&Delta;) - MASUKKAN TARGET DIPISAH KOMA (CONTOH: q0, q1)</div>", unsafe_allow_html=True)

                hcols = st.columns([1.5] + [1] * len(all_syms_nfa))
                with hcols[0]:
                    st.markdown("<div class='th-row'>State</div>", unsafe_allow_html=True)
                for i, sym in enumerate(all_syms_nfa):
                    with hcols[i + 1]:
                        disp = "&epsilon;" if sym == EPS else sym.upper()
                        st.markdown(f"<div class='th-row' style='text-align:center'>{disp}</div>", unsafe_allow_html=True)

                for s in nsim_states_list:
                    is_s = s == nsim_start
                    is_a = s in nsim_accept_set
                    if is_s and is_a:
                        cls, lbl = "is-both",   f"-&gt;* {s}"
                    elif is_s:
                        cls, lbl = "is-start",  f"-&gt; {s}"
                    elif is_a:
                        cls, lbl = "is-accept", f"* {s}"
                    else:
                        cls, lbl = "",          s

                    rcols = st.columns([1.5] + [1] * len(all_syms_nfa))
                    with rcols[0]:
                        st.markdown(f"<div class='state-label {cls}'>{lbl}</div>", unsafe_allow_html=True)
                    for i, sym in enumerate(all_syms_nfa):
                        with rcols[i + 1]:
                            st.text_input("x", key=f"nsim_t_{s}_{sym}", placeholder="\u2205", label_visibility="collapsed")

            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
            nb1, nb2 = st.columns([4, 1])
            with nb1:
                deploy_nfa = st.button("Deploy NFA", use_container_width=True, type="primary", disabled=not nsim_ready)
            with nb2:
                if st.button("Reset", use_container_width=True, type="secondary", key="nsim_reset"):
                    for k in list(st.session_state.keys()):
                        if k.startswith("nsim"):
                            del st.session_state[k]
                    st.rerun()

            st.markdown("""
            <div class='info-note'>
              NFA supports epsilon transitions and non-determinism:
              one state can have multiple or zero transitions per symbol.
            </div>""", unsafe_allow_html=True)

        with right:
            st.markdown("<div class='section-title'>NFA Visualization</div>", unsafe_allow_html=True)

            if deploy_nfa and nsim_ready:
                transitions_built = {}
                for s in nsim_states_list:
                    for sym in all_syms_nfa:
                        val = st.session_state.get(f"nsim_t_{s}_{sym}", "").replace(",", " ").strip()
                        if val and val != "-" and val != "\u2205":
                            targets = set(val.split())
                            valid_targets = {t for t in targets if t in nsim_states_list}
                            if valid_targets:
                                transitions_built[(s, sym)] = valid_targets

                nfa_obj = NFAModel(
                    states=set(nsim_states_list),
                    alphabet=set(nsim_alpha_list),
                    start_state=nsim_start,
                    accept_states={t for t in nsim_accept_set if t in nsim_states_list},
                    transitions=transitions_built,
                )
                st.session_state["nsim_nfa"]   = nfa_obj
                st.session_state["nsim_ready"] = True

            graph_ph  = st.empty()
            status_ph = st.empty()

            if st.session_state.get("nsim_ready"):
                nfa_d = st.session_state["nsim_nfa"]
                graph_ph.graphviz_chart(generate_nfa_graph(nfa_d), use_container_width=True)

                content  = render_state_badges(nfa_d.states, nfa_d.start_state, nfa_d.accept_states)
                content += render_nfa_table(nfa_d)
                st.markdown(f"<div class='display-area'>{content}</div>", unsafe_allow_html=True)

                nfa_r = st.session_state["nsim_nfa"]
                st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)
                tc1, tc2 = st.columns([3, 1.2])
                with tc1:
                    test_nfa_str = st.text_input(
                        "tnfa", placeholder="Enter string to test...",
                        key="nsim_test_str", label_visibility="collapsed"
                    )
                with tc2:
                    run_nfa = st.button("Run", type="primary", use_container_width=True, key="nsim_run")

                if run_nfa:
                    label = f'"{test_nfa_str}"' if test_nfa_str else "empty string"
                    try:
                        accepted, log = animate_nfa(nfa_r, test_nfa_str, graph_ph, status_ph)
                        if accepted:
                            st.markdown(f"<div class='result-accept'><b>Accepted</b> &mdash; {label}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='result-reject'><b>Rejected</b> &mdash; {label}</div>", unsafe_allow_html=True)
                        st.markdown("<div class='field-label' style='margin-top:0.8rem'>Simulation Log</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='log-box'>{log.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    except ValueError as e:
                        st.markdown(f"<div class='result-reject'><b>Error:</b> {e}</div>", unsafe_allow_html=True)

            else:
                graph_ph.markdown("<div class='display-area'><div class='idle-text'>Define the NFA and click Deploy.</div></div>", unsafe_allow_html=True)

    # ── 4. DFA MINIMIZER ──────────────────────────────────────────────────────
    elif menu == "DFA Minimizer":
        left, right = st.columns([1, 1.8], gap="large")

        with left:
            states, alphabet, ready = dfa_config_form("min_")
            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

            mb1, mb2 = st.columns([4, 1])
            with mb1:
                do_min = st.button("Minimize DFA", use_container_width=True, type="primary", disabled=not ready)
            with mb2:
                if st.button("Reset", use_container_width=True, type="secondary", key="min_reset"):
                    for k in list(st.session_state.keys()):
                        if k.startswith("min_"):
                            del st.session_state[k]
                    st.rerun()

            st.markdown("""
            <div class='info-note'>
              Minimizes the DFA using the Table-Filling algorithm (Myhill-Nerode theorem).
              Equivalent states are merged into one.
            </div>""", unsafe_allow_html=True)

        with right:
            st.markdown("<div class='section-title'>Minimized DFA</div>", unsafe_allow_html=True)

            if do_min and ready:
                dfa_orig = build_dfa("min_", states, alphabet)
                try:
                    dfa_min, log = capture(minimize_dfa, copy.deepcopy(dfa_orig))
                    st.session_state["min_orig"]   = dfa_orig
                    st.session_state["min_result"] = dfa_min
                    st.session_state["min_log"]    = log
                    st.session_state["min_done"]   = True
                    st.session_state.pop("min_error", None)
                except Exception as e:
                    st.session_state["min_error"] = str(e)
                    st.session_state["min_done"]  = False

            if st.session_state.get("min_done"):
                dfa_orig = st.session_state["min_orig"]
                dfa_min  = st.session_state["min_result"]
                log      = st.session_state["min_log"]

                st.graphviz_chart(generate_dfa_graph(dfa_min), use_container_width=True)

                content  = render_state_badges(dfa_min.states, dfa_min.start_state, dfa_min.accept_states)
                content += render_dfa_table(dfa_min)
                st.markdown(f"<div class='display-area'>{content}</div>", unsafe_allow_html=True)

                reduction = len(dfa_orig.states) - len(dfa_min.states)
                pct       = int(reduction / max(len(dfa_orig.states), 1) * 100)

                s1, s2, s3 = st.columns(3)
                with s1:
                    st.markdown(f"""
                    <div class='stat-card'>
                      <div class='stat-label'>Original States</div>
                      <div class='stat-value'>{len(dfa_orig.states)}</div>
                    </div>""", unsafe_allow_html=True)
                with s2:
                    st.markdown(f"""
                    <div class='stat-card'>
                      <div class='stat-label'>Minimized States</div>
                      <div class='stat-value' style='color:var(--wine-hover)'>{len(dfa_min.states)}</div>
                    </div>""", unsafe_allow_html=True)
                with s3:
                    st.markdown(f"""
                    <div class='stat-card'>
                      <div class='stat-label'>State Reduction</div>
                      <div class='stat-value' style='color:var(--green-text)'>{pct}%</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("<div class='field-label' style='margin-top:0.8rem'>Process Log</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='log-box'>{log.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

            elif st.session_state.get("min_error"):
                st.markdown(f"<div class='result-reject'><b>Error:</b> {st.session_state['min_error']}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='display-area'><div class='idle-text'>Configure a DFA and click Minimize.</div></div>", unsafe_allow_html=True)

    # ── 5. DFA EQUIVALENCE ────────────────────────────────────────────────────
    elif menu == "DFA Equivalence":
        st.markdown("<div class='section-title'>DFA Equivalence Checker</div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='color:var(--gray);font-size:0.8rem;margin-bottom:1.2rem'>"
            "Enter two DFAs to check whether they accept the same language using product construction."
            "</div>",
            unsafe_allow_html=True
        )

        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            st.markdown("<div class='dfa-tag dfa-tag-1'>DFA 1</div>", unsafe_allow_html=True)
            states_a, alpha_a, ready_a = dfa_config_form("eq1_")
        with col_b:
            st.markdown("<div class='dfa-tag dfa-tag-2'>DFA 2</div>", unsafe_allow_html=True)
            states_b, alpha_b, ready_b = dfa_config_form("eq2_")

        st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)
        _, ec_mid, __ = st.columns([2, 2, 2])
        with ec_mid:
            do_eq = st.button(
                "Check Equivalence", use_container_width=True,
                type="primary", disabled=not (ready_a and ready_b)
            )

        if do_eq and ready_a and ready_b:
            dfa1 = build_dfa("eq1_", states_a, alpha_a)
            dfa2 = build_dfa("eq2_", states_b, alpha_b)
            try:
                result, log = capture(check_equivalence, dfa1, dfa2)
                st.session_state["eq_result"] = result
                st.session_state["eq_log"]    = log
                st.session_state["eq_done"]   = True
                st.session_state.pop("eq_error", None)
            except Exception as e:
                st.session_state["eq_error"] = str(e)
                st.session_state["eq_done"]  = False

        st.markdown("<hr>", unsafe_allow_html=True)

        if st.session_state.get("eq_done"):
            result = st.session_state["eq_result"]
            log    = st.session_state["eq_log"]
            _, mid, __ = st.columns([1, 2, 1])
            with mid:
                if result:
                    st.markdown("""
                    <div class='verdict-yes'>
                      <div class='verdict-label'>Verdict</div>
                      <div class='verdict-main'>EQUIVALENT</div>
                      <div class='verdict-sub'>Both DFAs accept exactly the same language.</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class='verdict-no'>
                      <div class='verdict-label'>Verdict</div>
                      <div class='verdict-main'>NOT EQUIVALENT</div>
                      <div class='verdict-sub'>There exists a string accepted by one DFA but not the other.</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div class='field-label' style='margin-top:1rem'>Analysis Log</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='log-box'>{log.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

        elif st.session_state.get("eq_error"):
            st.markdown(f"<div class='result-reject'><b>Error:</b> {st.session_state['eq_error']}</div>", unsafe_allow_html=True)
        else:
            _, mid, __ = st.columns([1, 2, 1])
            with mid:
                st.markdown(
                    "<div class='idle-text' style='padding:2rem 0'>Configure both DFAs above to check equivalence.</div>",
                    unsafe_allow_html=True
                )