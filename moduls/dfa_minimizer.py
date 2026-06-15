from models.dfa import DFA
from itertools import combinations


def minimize_dfa(dfa: DFA) -> DFA:
    """
    Minimasi DFA menggunakan algoritma Table-Filling (Myhill-Nerode).
    """
    print("\n=== Minimasi DFA (Table-Filling) ===")

    states = sorted(dfa.states)
    alphabet = sorted(dfa.alphabet)

    dead_state = "__dead__"
    has_dead = False
    for s in states:
        for sym in alphabet:
            if dfa.get_next_state(s, sym) is None:
                has_dead = True
                dfa.transitions[(s, sym)] = dead_state
    if has_dead:
        dfa.states.add(dead_state)
        for sym in alphabet:
            dfa.transitions[(dead_state, sym)] = dead_state
        states = sorted(dfa.states)
        print(f"  Dead state '{dead_state}' ditambahkan.")

    distinguishable = set()

    pairs = list(combinations(states, 2))

    def mark(p, q):
        pair = (min(p, q), max(p, q))
        if pair not in distinguishable:
            distinguishable.add(pair)
            return True
        return False

    for p, q in pairs:
        p_accept = p in dfa.accept_states
        q_accept = q in dfa.accept_states
        if p_accept != q_accept:
            mark(p, q)

    print(f"  Pasangan awal (accept vs non-accept): {len(distinguishable)}")

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
                np = dfa.transitions.get((p, sym))
                nq = dfa.transitions.get((q, sym))
                if np is None or nq is None:
                    continue
                if np == nq:
                    continue
                check = (min(np, nq), max(np, nq))
                if check in distinguishable:
                    if mark(p, q):
                        changed = True
                    break

    print(f"  Iterasi selesai dalam {iteration} putaran.")
    print(f"  Total pasangan dibedakan: {len(distinguishable)}")

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

    min_dfa = DFA()

    groups = {}
    for s in states:
        rep = find(s)
        if rep not in groups:
            groups[rep] = []
        groups[rep].append(s)

    rep_to_name = {}
    idx = 0
 
    start_rep = find(dfa.start_state)
    rep_to_name[start_rep] = f"q{idx}"
    idx += 1
    for rep in sorted(groups.keys()):
        if rep != start_rep:
            rep_to_name[rep] = f"q{idx}"
            idx += 1

    print("\n  Pengelompokan state:")
    for rep, members in sorted(groups.items()):
        name = rep_to_name[rep]
        print(f"    {name} ← {sorted(members)}")

    min_dfa.set_start(rep_to_name[start_rep])

    for rep, members in groups.items():
        for m in members:
            if m in dfa.accept_states:
                min_dfa.add_accept(rep_to_name[rep])
                break

    for rep, members in groups.items():
        s = members[0]  
        if s == dead_state:
            continue
        for sym in alphabet:
            ns = dfa.transitions.get((s, sym))
            if ns is None:
                continue
            ns_rep = find(ns)
            if ns_rep == find(dead_state) if has_dead else False:
                continue
            from_name = rep_to_name[rep]
            to_name = rep_to_name[ns_rep]
            min_dfa.add_transition(from_name, sym, to_name)

    if has_dead and dead_state in dfa.states:
        dfa.states.discard(dead_state)
        for sym in alphabet:
            dfa.transitions.pop((dead_state, sym), None)
        for s in list(dfa.states):
            for sym in alphabet:
                if dfa.transitions.get((s, sym)) == dead_state:
                    dfa.transitions.pop((s, sym), None)

    return min_dfa