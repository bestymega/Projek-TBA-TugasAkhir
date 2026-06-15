from models.dfa import DFA
from collections import deque


def check_equivalence(dfa1: DFA, dfa2: DFA) -> bool:
    """
    Cek apakah dua DFA equivalen menggunakan algoritma product construction.
    Dua DFA equivalen jika untuk semua string input, keduanya menghasilkan
    output yang sama (diterima/ditolak).
    """
    print("\n=== Pengecekan Equivalensi DFA ===")

    # Alphabet harus sama
    if dfa1.alphabet != dfa2.alphabet:
        print(f"  Alphabet berbeda!")
        print(f"  DFA 1: {sorted(dfa1.alphabet)}")
        print(f"  DFA 2: {sorted(dfa2.alphabet)}")
        print("  Hasil: TIDAK EQUIVALEN ✗")
        return False

    alphabet = sorted(dfa1.alphabet)

    # BFS pada product automaton
    start = (dfa1.start_state, dfa2.start_state)
    visited = set()
    queue = deque([start])
    visited.add(start)

    print(f"  Alphabet    : {alphabet}")
    print(f"  Start pair  : {start}")
    print("\n  Eksplorasi product automaton:")

    while queue:
        s1, s2 = queue.popleft()

        in1 = s1 in dfa1.accept_states
        in2 = s2 in dfa2.accept_states

        status = ""
        if in1 and not in2:
            status = f"✗ DFA1 accept, DFA2 reject di ({s1}, {s2})"
        elif not in1 and in2:
            status = f"✗ DFA1 reject, DFA2 accept di ({s1}, {s2})"

        if status:
            print(f"    State pair ({s1}, {s2}) → {status}")
            print("\n  Hasil: TIDAK EQUIVALEN ✗")
            return False

        for sym in alphabet:
            ns1 = dfa1.get_next_state(s1, sym)
            ns2 = dfa2.get_next_state(s2, sym)

            # Jika salah satu tidak punya transisi, anggap dead state
            if ns1 is None and ns2 is None:
                continue

            # Salah satu dead tapi lainnya tidak
            if ns1 is None:
                ns1 = "_dead1_"
            if ns2 is None:
                ns2 = "_dead2_"

            next_pair = (ns1, ns2)
            if next_pair not in visited:
                visited.add(next_pair)
                queue.append(next_pair)
                print(f"    ({s1},{s2}) --{sym}--> ({ns1},{ns2})")

    print(f"\n  Total state pairs dieksplorasi: {len(visited)}")
    print("\n  Hasil: EQUIVALEN ✓")
    return True


def input_dfa_simple(label: str) -> DFA:
    """Input DFA sederhana (dipakai untuk equivalence checker)."""
    from moduls.dfa_simulator import input_dfa
    print(f"\n--- Input {label} ---")
    return input_dfa()