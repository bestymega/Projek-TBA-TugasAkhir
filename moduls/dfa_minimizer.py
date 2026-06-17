from models.dfa import DFA
from itertools import combinations


def minimize_dfa(dfa: DFA) -> DFA:
    """
    Minimasi DFA menggunakan algoritma Table-Filling (Myhill-Nerode).
    """
    print("Minimasi DFA (Table-Filling)")

    alphabet = sorted(dfa.alphabet)
    dead_state = "__dead__"
    has_dead = False

    # ── 1. Tambah dead state jika ada transisi yang hilang ──────────────────
    for s in list(dfa.states):
        for sym in alphabet:
            if dfa.transitions.get((s, sym)) is None:
                has_dead = True
                dfa.transitions[(s, sym)] = dead_state

    if has_dead:
        dfa.states.add(dead_state)
        for sym in alphabet:
            dfa.transitions[(dead_state, sym)] = dead_state
        print(f"  Dead state '{dead_state}' ditambahkan.")

    states = sorted(dfa.states)

    # ── 2. Inisialisasi tabel — tandai pasangan (accept, non-accept) ────────
    distinguishable = set()
    pairs = list(combinations(states, 2))

    def mark(p, q):
        pair = (min(p, q), max(p, q))
        if pair not in distinguishable:
            distinguishable.add(pair)
            return True
        return False

    for p, q in pairs:
        if (p in dfa.accept_states) != (q in dfa.accept_states):
            mark(p, q)

    print(f"  Pasangan awal (accept vs non-accept): {len(distinguishable)}")

    # ── 3. Propagasi — tandai pasangan yang mengarah ke pasangan berbeda ────
    changed = True
    iteration = 0
    while changed:
        changed = False
        iteration += 1
        for p, q in pairs:
            pair = (min(p, q), max(p, q))
            if pair in distinguishable:
                continue
            for sym in alphabet:
                np_ = dfa.transitions.get((p, sym))
                nq_ = dfa.transitions.get((q, sym))
                if np_ is None or nq_ is None or np_ == nq_:
                    continue
                check = (min(np_, nq_), max(np_, nq_))
                if check in distinguishable:
                    if mark(p, q):
                        changed = True
                    break

    print(f"  Iterasi selesai dalam {iteration} putaran.")
    print(f"  Total pasangan dibedakan: {len(distinguishable)}")

    # ── 4. Union-Find — gabungkan state yang tidak dapat dibedakan ───────────
    parent = {s: s for s in states}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    for p, q in pairs:
        pair = (min(p, q), max(p, q))
        if pair not in distinguishable:
            union(p, q)

    # ── 5. Kelompokkan state berdasarkan representative ──────────────────────
    groups: dict[str, list[str]] = {}
    for s in states:
        rep = find(s)
        groups.setdefault(rep, []).append(s)

    # ── 6. Beri nama state baru; start state selalu q0 ──────────────────────
    rep_to_name: dict[str, str] = {}
    idx = 0
    start_rep = find(dfa.start_state)
    rep_to_name[start_rep] = f"q{idx}"
    idx += 1
    for rep in sorted(groups.keys()):
        if rep not in rep_to_name:
            rep_to_name[rep] = f"q{idx}"
            idx += 1

    print("\n  Pengelompokan state:")
    for rep, members in sorted(groups.items()):
        name = rep_to_name[rep]
        print(f"    {name} ← {sorted(members)}")

    # ── 7. Bangun min_dfa ────────────────────────────────────────────────────
    min_dfa = DFA()
    min_dfa.set_start(rep_to_name[start_rep])

    for rep, members in groups.items():
        # Skip grup yang seluruhnya dead state
        if all(m == dead_state for m in members):
            continue
        # Accept jika ada member yang accept (dead state tidak bisa accept)
        for m in members:
            if m != dead_state and m in dfa.accept_states:
                min_dfa.add_accept(rep_to_name[rep])
                break

    dead_rep = find(dead_state) if has_dead else None

    for rep, members in groups.items():
        # Skip grup dead state — tidak perlu transisi dari sana
        if dead_rep is not None and find(rep) == find(dead_rep):
            continue

        # Ambil representative non-dead dari grup ini
        src = next((m for m in members if m != dead_state), None)
        if src is None:
            continue

        from_name = rep_to_name[rep]

        for sym in alphabet:
            ns = dfa.transitions.get((src, sym))
            if ns is None:
                continue
            ns_rep = find(ns)
            # Jangan tambah transisi ke dead state
            if dead_rep is not None and find(ns_rep) == find(dead_rep):
                continue
            to_name = rep_to_name[ns_rep]
            min_dfa.add_transition(from_name, sym, to_name)

    # ── 8. Kembalikan dfa asli ke kondisi sebelum dead state ditambahkan ────
    if has_dead:
        dfa.states.discard(dead_state)
        for sym in alphabet:
            dfa.transitions.pop((dead_state, sym), None)
        for s in list(dfa.states):
            for sym in alphabet:
                if dfa.transitions.get((s, sym)) == dead_state:
                    dfa.transitions.pop((s, sym), None)

    return min_dfa