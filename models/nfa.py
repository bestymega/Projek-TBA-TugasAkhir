"""
models/nfa.py - Definisi struktur data NFA (Nondeterministic Finite Automaton).

Modul ini menyediakan class NFA yang digunakan bersama oleh:
  - moduls/regex_to_nfa.py  (Thompson Construction)
  - moduls/nfa_simulator.py (NFA Simulator)
"""

from typing import Dict, Set, Tuple


class NFA:
    """
    Representasi NFA (Nondeterministic Finite Automaton).

    Atribut:
        states       : himpunan semua state (set of int)
        alphabet     : himpunan simbol input (set of str), tidak termasuk 'ε'
        start_state  : state awal (int)
        accept_states: himpunan state akhir (set of int)
        transitions  : dict {(state, symbol): set_of_states}
                       Gunakan NFA.EPSILON ('ε') untuk epsilon-transition.

    Contoh penggunaan (Anggota 3 - NFA Simulator):
        from models.nfa import NFA
        from moduls.regex_to_nfa import regex_to_nfa

        nfa = regex_to_nfa("(a|b)*abb")
        print(nfa.start_state)
        print(nfa.accept_states)
        next_states = nfa.get_transitions(state, symbol)
    """

    EPSILON = 'ε'

    def __init__(
        self,
        states: Set,
        alphabet: Set[str],
        start_state,
        accept_states: Set,
        transitions: Dict[Tuple, Set]
    ):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.transitions: Dict[Tuple, Set] = {
            key: set(val) for key, val in transitions.items()
        }

    def get_transitions(self, state, symbol: str) -> Set:
        """
        Mengembalikan himpunan state tujuan dari (state, symbol).

        Args:
            state  : state asal
            symbol : simbol input, atau NFA.EPSILON untuk ε-transition

        Returns:
            Set of states yang dapat dicapai, atau set kosong jika tidak ada.
        """
        return self.transitions.get((state, symbol), set())

    def display(self):
        """Menampilkan informasi lengkap NFA ke konsol."""
        print("\nNFA (Thompson Construction)")
        print(f"\n{'States':<20}: {sorted(self.states)}")
        print(f"{'Alphabet':<20}: {sorted(self.alphabet)}")
        print(f"{'Start State':<20}: {self.start_state}")
        print(f"{'Accept States':<20}: {sorted(self.accept_states)}")
        print(f"\nTransition Function:")
        print(f"  {'(State, Symbol)':<25} -> Next States")
        print(f"  {'-'*40}")
        for (state, symbol), next_states in sorted(
            self.transitions.items(), key=lambda x: (x[0][0], x[0][1])
        ):
            sym = symbol if symbol != self.EPSILON else 'ε'
            print(f"  ({state:>3}, {sym:<10})  ->  {sorted(next_states)}")
        print("=" * 55)

    def __repr__(self):
        return (
            f"NFA(states={sorted(self.states)}, "
            f"alphabet={sorted(self.alphabet)}, "
            f"start={self.start_state}, "
            f"accept={sorted(self.accept_states)}, "
            f"transitions={len(self.transitions)} rules)"
        )