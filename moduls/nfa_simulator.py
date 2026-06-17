"""
moduls/nfa_simulator.py - Simulasi NFA (Nondeterministic Finite Automaton).

Modul ini mensimulasikan NFA yang dihasilkan oleh moduls/regex_to_nfa.py
menggunakan algoritma subset construction berbasis epsilon-closure.

Cara penggunaan:
    from moduls.nfa_simulator import NFASimulator
    from moduls.regex_to_nfa import regex_to_nfa

    nfa = regex_to_nfa("(a|b)*abb")
    simulator = NFASimulator()
    result = simulator.simulate(nfa, "abb", verbose=True)
    print(result)  # True
"""

from models.nfa import NFA


class NFASimulator:
    """
    Simulator untuk NFA (Nondeterministic Finite Automaton).

    Mensimulasikan jalannya NFA terhadap sebuah string input menggunakan
    algoritma epsilon-closure dan move secara bertahap.

    Atribut:
        current_states : himpunan state aktif saat ini (set)
        input_string   : string input yang sedang/telah disimulasikan (str)

    Contoh penggunaan:
        from moduls.regex_to_nfa import regex_to_nfa

        nfa = regex_to_nfa("(a|b)*abb")
        simulator = NFASimulator()

        result = simulator.simulate(nfa, "abb", verbose=True)
        # True

        result = simulator.test_string(nfa, "abab")
        # False
    """

    def __init__(self):
        """
        Menginisialisasi NFASimulator dengan state kosong dan string kosong.
        """
        self.current_states: set = set()
        self.input_string: str = ""

    def epsilon_closure(self, nfa: NFA, states: set) -> set:
        """
        Menghitung epsilon-closure dari sekumpulan state.

        Mengembalikan semua state yang dapat dicapai dari sekumpulan state
        hanya melalui epsilon-transition (tanpa membaca simbol input).

        Algoritma menggunakan DFS berbasis stack.

        Args:
            nfa    : objek NFA yang digunakan
            states : himpunan state awal

        Returns:
            Himpunan semua state yang dapat dicapai melalui ε-transition.

        Contoh:
            Jika (0, ε) -> {1, 2} dan (1, ε) -> {3}, maka:
            epsilon_closure({0}) menghasilkan {0, 1, 2, 3}
        """
        closure: set = states.copy()
        stack: list = list(states)

        while stack:
            state = stack.pop()
            for next_state in nfa.get_transitions(state, NFA.EPSILON):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

        return closure

    def move(self, nfa: NFA, states: set, symbol: str) -> set:
        """
        Menghitung himpunan state tujuan dari sekumpulan state dengan simbol tertentu.

        Mengumpulkan semua state yang dapat dicapai dari setiap state dalam
        himpunan menggunakan simbol input yang diberikan.

        Args:
            nfa    : objek NFA yang digunakan
            states : himpunan state asal
            symbol : simbol input yang dibaca

        Returns:
            Himpunan semua state tujuan.

        Contoh:
            Jika (1, 'a') -> {2} dan (3, 'a') -> {4}, maka:
            move({1, 3}, 'a') menghasilkan {2, 4}
        """
        result: set = set()
        for state in states:
            result.update(nfa.get_transitions(state, symbol))
        return result

    def simulate(self, nfa: NFA, input_string: str, verbose: bool = False) -> bool:
        """
        Mensimulasikan NFA terhadap sebuah string input.

        Memproses setiap simbol pada input_string secara berurutan dengan
        menghitung move() lalu epsilon_closure() pada setiap langkah.
        Diterima jika state akhir beririsan dengan accept_states.

        Args:
            nfa          : objek NFA yang akan disimulasikan
            input_string : string input yang akan diuji
            verbose      : jika True, tampilkan langkah-langkah simulasi

        Returns:
            True jika string diterima oleh NFA, False jika tidak.

        Raises:
            ValueError: jika terdapat simbol pada input_string yang tidak
                        ada dalam alphabet NFA.
        """
        self.input_string = input_string
        self.current_states = self.epsilon_closure(nfa, {nfa.start_state})

        if verbose:
            print(f"Input String : {input_string}")
            print(f"Initial ε-closure: {sorted(self.current_states)}")

        for symbol in input_string:
            if symbol not in nfa.alphabet:
                raise ValueError(
                    f"Simbol '{symbol}' tidak terdapat pada alphabet NFA."
                )

            next_states = self.move(nfa, self.current_states, symbol)
            self.current_states = self.epsilon_closure(nfa, next_states)

            if verbose:
                print(f"\nRead symbol : '{symbol}'")
                print(f"Move: {sorted(next_states)}")
                print(f"ε-closure: {sorted(self.current_states)}")

        accepted: bool = bool(self.current_states & nfa.accept_states)

        if verbose:
            print(f"\nFinal States : {sorted(self.current_states)}")
            print(f"Accept States : {sorted(nfa.accept_states)}")
            result_str = "ACCEPTED" if accepted else "REJECTED"
            print(f"RESULT : {result_str}")

        return accepted

    def reset(self):
        """
        Mereset simulator ke kondisi awal.

        Mengosongkan current_states dan input_string sehingga simulator
        siap digunakan kembali untuk string lain.
        """
        self.current_states = set()
        self.input_string = ""

    def test_string(self, nfa: NFA, input_string: str) -> bool:
        """
        Menguji apakah string diterima oleh NFA (tanpa verbose).

        Wrapper sederhana dari simulate() dengan verbose=False.

        Args:
            nfa          : objek NFA yang akan digunakan
            input_string : string input yang akan diuji

        Returns:
            True jika string diterima, False jika tidak.
        """
        return self.simulate(nfa, input_string)


# ══════════════════════════════════════════════════════
#  CONTOH PENGGUNAAN
# ══════════════════════════════════════════════════════

if __name__ == "__main__":
    from moduls.regex_to_nfa import regex_to_nfa

    print("=" * 50)
    print("         NFA SIMULATOR — User Input Mode")
    print("=" * 50)

    # Input regex
    while True:
        regex = input("\nMasukkan regex (contoh: (a|b)*abb): ").strip()
        if regex:
            break
        print("  [!] Regex tidak boleh kosong.")

    try:
        nfa = regex_to_nfa(regex)
        print(f'\n  NFA berhasil dibuat untuk regex: "{regex}"')
    except ValueError as e:
        print(f"  [ERROR] Regex tidak valid: {e}")
        exit(1)

    # Input verbose mode
    verbose_input = input("\nTampilkan langkah-langkah simulasi? (y/n): ").strip().lower()
    verbose = verbose_input == 'y'

    simulator = NFASimulator()

    # Loop pengujian string
    print("\n  Ketik 'exit' untuk keluar, Enter kosong = string kosong (\"\").")
    while True:
        raw = input("\nMasukkan string input: ")
        if raw.strip().lower() == 'exit':
            print("\n  Keluar dari simulator. Sampai jumpa!")
            break

        input_string = raw  # biarkan spasi/kosong apa adanya
        simulator.reset()

        try:
            result = simulator.simulate(nfa, input_string, verbose=verbose)
            if not verbose:
                status = "ACCEPTED" if result else "REJECTED"
                print(f"  Hasil: {status}")
        except ValueError as e:
            print(f"  [ERROR] {e}")