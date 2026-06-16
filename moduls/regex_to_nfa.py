"""
moduls/regex_to_nfa.py - Konversi Regular Expression → NFA (Thompson Construction).

Modul ini menggabungkan dua tahap utama:
  1. PARSING  : Regex infix → Postfix (Shunting-Yard Algorithm)
  2. BUILDING : Postfix → NFA (Thompson Construction)

Cara penggunaan (dari modul lain):
    from moduls.regex_to_nfa import regex_to_nfa

    nfa = regex_to_nfa("(a|b)*abb")
    print(nfa.states)
    print(nfa.start_state)
    print(nfa.accept_states)
    print(nfa.transitions)

Regex yang didukung:
    - Literal     : a-z
    - Union       : |
    - Concatenation: implisit (otomatis ditangani)
    - Kleene Star : *
    - Parentheses : ()
"""

from models.nfa import NFA

# ══════════════════════════════════════════════════════
#  BAGIAN 1 — PARSER
#  Mengonversi regex infix biasa ke notasi postfix
# ══════════════════════════════════════════════════════

CONCAT_OP = '·'   # Operator konkatenasi eksplisit (internal)

PRECEDENCE = {
    '*':      3,   # Kleene Star (paling kuat)
    CONCAT_OP: 2,  # Concatenation
    '|':      1,   # Union (paling lemah)
}


def is_literal(char: str) -> bool:
    """Mengembalikan True jika char adalah sebuah literal (bukan operator regex)."""
    return char not in ('|', '*', '(', ')', CONCAT_OP)


def add_concat_operator(regex: str) -> str:
    """
    Menyisipkan operator konkatenasi eksplisit '·' pada posisi yang tepat.

    Konkatenasi implisit terjadi ketika:
      - Sisi kiri  : literal, ')', atau '*'
      - Sisi kanan : literal atau '('

    Contoh:
      "ab"        → "a·b"
      "(a|b)*abb" → "(a|b)*·a·b·b"

    Args:
        regex : string regex dalam notasi infix biasa

    Returns:
        String regex dengan operator '·' disisipkan.
    """
    result = []
    for i, char in enumerate(regex):
        result.append(char)
        if i + 1 < len(regex):
            left = char
            right = regex[i + 1]
            left_ok = is_literal(left) or left in (')', '*')
            right_ok = is_literal(right) or right == '('
            if left_ok and right_ok:
                result.append(CONCAT_OP)
    return ''.join(result)


def infix_to_postfix(regex: str) -> str:
    """
    Mengonversi regex infix (dengan '·' eksplisit) ke notasi postfix
    menggunakan Shunting-Yard Algorithm.

    Urutan presedensi: * > · > |
    Semua operator bersifat left-associative.

    Contoh:
      "a·b|c"  → "ab·c|"
      "(a|b)*" → "ab|*"

    Args:
        regex : string regex infix dengan '·' eksplisit

    Returns:
        String regex dalam notasi postfix.

    Raises:
        ValueError: jika parentheses tidak seimbang.
    """
    output = []
    stack = []

    for token in regex:
        if is_literal(token):
            output.append(token)

        elif token == '(':
            stack.append(token)

        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Parentheses tidak seimbang: '(' tidak ditemukan.")
            stack.pop()  # buang '('

        elif token in PRECEDENCE:
            while (
                stack
                and stack[-1] != '('
                and stack[-1] in PRECEDENCE
                and PRECEDENCE.get(stack[-1], 0) >= PRECEDENCE.get(token, 0)
            ):
                output.append(stack.pop())
            stack.append(token)

        else:
            raise ValueError(f"Token tidak dikenal: '{token}'")

    while stack:
        top = stack.pop()
        if top == '(':
            raise ValueError("Parentheses tidak seimbang: ')' tidak ditemukan.")
        output.append(top)

    return ''.join(output)


def parse_regex(regex: str) -> str:
    """
    Fungsi utama parsing: regex biasa → postfix.

    Tahapan:
      1. Sisipkan operator konkatenasi eksplisit dengan add_concat_operator()
      2. Konversi infix → postfix dengan infix_to_postfix()

    Args:
        regex : string regex dari pengguna

    Returns:
        String postfix siap diproses Thompson Construction.
    """
    if not regex:
        raise ValueError("Regex tidak boleh kosong.")
    with_concat = add_concat_operator(regex)
    return infix_to_postfix(with_concat)


# ══════════════════════════════════════════════════════
#  BAGIAN 2 — THOMPSON CONSTRUCTION
#  Membangun NFA dari ekspresi postfix
# ══════════════════════════════════════════════════════

_state_counter = 0


def _new_state() -> int:
    """Membuat ID state baru yang unik secara global."""
    global _state_counter
    state = _state_counter
    _state_counter += 1
    return state


def _reset_counter():
    """Mereset counter state ke 0 untuk setiap regex baru."""
    global _state_counter
    _state_counter = 0


def _nfa_literal(symbol: str) -> NFA:
    """
    Primitif Thompson: NFA untuk satu simbol literal.

    Konstruksi:
        q0 ──[symbol]──► q1 (accept)
    """
    q0 = _new_state()
    q1 = _new_state()
    return NFA(
        states={q0, q1},
        alphabet={symbol},
        start_state=q0,
        accept_states={q1},
        transitions={(q0, symbol): {q1}}
    )


def _nfa_union(nfa1: NFA, nfa2: NFA) -> NFA:
    """
    Primitif Thompson: NFA untuk union (nfa1 | nfa2).

    Konstruksi:
                    ┌──ε──► [nfa1] ──ε──┐
        q_start ───┤                    ├──► q_accept
                    └──ε──► [nfa2] ──ε──┘
    """
    q_start  = _new_state()
    q_accept = _new_state()
    eps = NFA.EPSILON

    transitions = {}
    transitions.update(nfa1.transitions)
    transitions.update(nfa2.transitions)
    transitions[(q_start, eps)] = {nfa1.start_state, nfa2.start_state}

    for s in nfa1.accept_states:
        transitions.setdefault((s, eps), set()).add(q_accept)
    for s in nfa2.accept_states:
        transitions.setdefault((s, eps), set()).add(q_accept)

    return NFA(
        states={q_start, q_accept} | nfa1.states | nfa2.states,
        alphabet=nfa1.alphabet | nfa2.alphabet,
        start_state=q_start,
        accept_states={q_accept},
        transitions=transitions
    )


def _nfa_concat(nfa1: NFA, nfa2: NFA) -> NFA:
    """
    Primitif Thompson: NFA untuk konkatenasi (nfa1 · nfa2).

    Konstruksi:
        [nfa1] ──ε──► [nfa2]
    """
    eps = NFA.EPSILON
    transitions = {}
    transitions.update(nfa1.transitions)
    transitions.update(nfa2.transitions)

    for s in nfa1.accept_states:
        transitions.setdefault((s, eps), set()).add(nfa2.start_state)

    return NFA(
        states=nfa1.states | nfa2.states,
        alphabet=nfa1.alphabet | nfa2.alphabet,
        start_state=nfa1.start_state,
        accept_states=nfa2.accept_states,
        transitions=transitions
    )


def _nfa_kleene_star(nfa: NFA) -> NFA:
    """
    Primitif Thompson: NFA untuk Kleene Star (nfa*).

    Konstruksi:
        q_start ──ε──► [nfa] ──ε──► q_accept
            │    ε (zero)  ↑ ε (loop)    ↑
            └─────────────────────────────┘
    """
    q_start  = _new_state()
    q_accept = _new_state()
    eps = NFA.EPSILON

    transitions = {}
    transitions.update(nfa.transitions)
    transitions[(q_start, eps)] = {nfa.start_state, q_accept}

    for s in nfa.accept_states:
        transitions.setdefault((s, eps), set()).update({nfa.start_state, q_accept})

    return NFA(
        states={q_start, q_accept} | nfa.states,
        alphabet=nfa.alphabet,
        start_state=q_start,
        accept_states={q_accept},
        transitions=transitions
    )


# ══════════════════════════════════════════════════════
#  FUNGSI UTAMA — PUBLIC API
# ══════════════════════════════════════════════════════

def regex_to_nfa(regex: str) -> NFA:
    """
    Mengonversi regular expression ke NFA menggunakan Thompson Construction.

    Ini adalah fungsi utama yang dipanggil oleh modul lain (NFA Simulator, main.py, dll).

    Alur:
      1. Parse regex → postfix notation
      2. Evaluasi postfix dengan stack:
           literal → NFA primitif
           '|'     → union dua NFA teratas
           '·'     → konkatenasi dua NFA teratas
           '*'     → Kleene star NFA teratas

    Args:
        regex : string regular expression, misal "(a|b)*abb"

    Returns:
        Object NFA siap digunakan oleh NFA Simulator.

    Raises:
        ValueError: jika regex tidak valid.

    Contoh:
        >>> nfa = regex_to_nfa("(a|b)*abb")
        >>> print(nfa.states)
        >>> print(nfa.start_state)
        >>> print(nfa.accept_states)
        >>> print(nfa.transitions)
    """
    _reset_counter()
    postfix = parse_regex(regex)

    stack: list = []

    for token in postfix:
        if is_literal(token):
            stack.append(_nfa_literal(token))

        elif token == '|':
            if len(stack) < 2:
                raise ValueError("Regex tidak valid: '|' kekurangan operand.")
            nfa2, nfa1 = stack.pop(), stack.pop()
            stack.append(_nfa_union(nfa1, nfa2))

        elif token == CONCAT_OP:
            if len(stack) < 2:
                raise ValueError("Regex tidak valid: '·' kekurangan operand.")
            nfa2, nfa1 = stack.pop(), stack.pop()
            stack.append(_nfa_concat(nfa1, nfa2))

        elif token == '*':
            if len(stack) < 1:
                raise ValueError("Regex tidak valid: '*' kekurangan operand.")
            stack.append(_nfa_kleene_star(stack.pop()))

        else:
            raise ValueError(f"Token tidak dikenal: '{token}'")

    if len(stack) != 1:
        raise ValueError(f"Regex tidak valid: stack berisi {len(stack)} NFA.")

    return stack[0]