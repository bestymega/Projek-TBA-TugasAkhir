from models.dfa import DFA


def simulate_dfa(dfa: DFA, input_string: str) -> bool:
    """
    Simulasi DFA untuk input string.
    Return True jika diterima, False jika ditolak.
    """
    current_state = dfa.start_state

    print(f"\n[Simulasi] Input: '{input_string}'")
    print(f"  Start → {current_state}")

    for symbol in input_string:
        if symbol not in dfa.alphabet:
            print(f"  ERROR: simbol '{symbol}' tidak ada di alphabet!")
            return False

        next_state = dfa.get_next_state(current_state, symbol)
        if next_state is None:
            print(f"  δ({current_state}, {symbol}) → DEAD STATE")
            print("  Hasil: DITOLAK ✗")
            return False

        print(f"  δ({current_state}, {symbol}) → {next_state}")
        current_state = next_state

    accepted = current_state in dfa.accept_states
    status = "DITERIMA ✓" if accepted else "DITOLAK ✗"
    print(f"  State akhir: {current_state} → {status}")
    return accepted


def input_dfa() -> DFA:
    """Input DFA secara interaktif dari user."""
    dfa = DFA()

    print("\n=== Input DFA ===")

    states_input = input("Masukkan semua states (pisah spasi, contoh: q0 q1 q2): ").split()
    for s in states_input:
        dfa.states.add(s)

    alphabet_input = input("Masukkan alphabet (pisah spasi, contoh: 0 1): ").split()
    for a in alphabet_input:
        dfa.alphabet.add(a)

    start = input("Masukkan start state: ").strip()
    dfa.set_start(start)

    accepts = input("Masukkan accept states (pisah spasi): ").split()
    for a in accepts:
        dfa.add_accept(a)

    print(f"Masukkan transisi ({len(states_input) * len(alphabet_input)} transisi):")
    print("Format: dari_state simbol ke_state (contoh: q0 0 q1)")
    print("Ketik 'selesai' untuk berhenti\n")

    while True:
        line = input("  Transisi: ").strip()
        if line.lower() == "selesai":
            break
        parts = line.split()
        if len(parts) != 3:
            print("  Format salah! Gunakan: dari_state simbol ke_state")
            continue
        from_s, sym, to_s = parts
        if from_s not in dfa.states:
            print(f"  State '{from_s}' tidak terdaftar.")
            continue
        if to_s not in dfa.states:
            print(f"  State '{to_s}' tidak terdaftar.")
            continue
        if sym not in dfa.alphabet:
            print(f"  Simbol '{sym}' tidak ada di alphabet.")
            continue
        dfa.add_transition(from_s, sym, to_s)

    return dfa