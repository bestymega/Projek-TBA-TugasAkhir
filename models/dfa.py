class DFA:
    def __init__(self):
        self.states = set()
        self.alphabet = set()
        self.transitions = {}  
        self.start_state = None
        self.accept_states = set()

    def add_transition(self, from_state, symbol, to_state):
        self.states.add(from_state)
        self.states.add(to_state)
        self.alphabet.add(symbol)
        self.transitions[(from_state, symbol)] = to_state

    def set_start(self, state):
        self.states.add(state)
        self.start_state = state

    def add_accept(self, state):
        self.states.add(state)
        self.accept_states.add(state)

    def get_next_state(self, state, symbol):
        return self.transitions.get((state, symbol), None)

    def display(self):
        print("\n=== DFA ===")
        print(f"States       : {sorted(self.states)}")
        print(f"Alphabet     : {sorted(self.alphabet)}")
        print(f"Start State  : {self.start_state}")
        print(f"Accept States: {sorted(self.accept_states)}")
        print("Transitions  :")
        for (s, sym), ns in sorted(self.transitions.items()):
            print(f"  δ({s}, {sym}) → {ns}")