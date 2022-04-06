# Classe da máquina de estados finitos (FSM)
class FSM():

    def __init__(self, qi_0, q_max, q_min, m, n):
        self.min_rate = qi_0
        self.current_state = 'lc'
        self.prev_state = 'lc'
        self.prev_lc = 0
        self.q_max = q_max
        self.q_min = q_min
        self.current_l = 0
        self.current_q = 0
        self.m_chks = 0
        self.m_max = m
        self.n_chks = 0
        self.n_max = n

    # Define a lista de estados
    def set_params(self, l, q):
        self.current_l = l
        self.current_q = q
        self.states = {'lc': self.prev_lc, 'l0': self.min_rate, 'l+': self.current_l, 'l-': self.current_l, 'IDLE': self.current_l}

    # Verifica as codições atuais
    def get_conditions(self):
        # Se q(t) < q_min --> estado l0
        if (self.current_q < self.q_min):
            return 'l0'

        # Se não, se q(t) > q_max --> estado IDLE
        elif (self.current_q > self.q_max):
            return 'IDLE'
        
        # Se não, se q_min <= q(t) <= q_max --> estado l+, l- ou lc
        elif (self.current_q >= self.q_min and self.current_q <= self.q_max):
            if (self.current_l > self.prev_lc and self.m_chks >= self.m_max):
                self.m_chks = 0
                return 'l+'
            elif (self.current_l > self.prev_lc and self.m_chks < self.m_max):
                self.m_chks += 1
                return 'lc'
            elif (self.current_l < self.prev_lc and self.n_chks >= self.n_max):
                self.n_chks = 0
                return 'l-'
            elif (self.current_l < self.prev_lc and self.n_chks < self.n_max):
                self.n_chks += 1
                return 'lc'
            else:
                return 'lc'

    # Atualiza o estado e retorna o próximo lc
    def set_state(self, forced_state=''):
        self.prev_state = self.current_state
        if forced_state == '':
            self.current_state = self.get_conditions()
        else:
            self.current_state = forced_state
        self.prev_lc = self.states[self.current_state]

        if self.current_state != 'IDLE':
            return self.states[self.current_state]
        else:
            # Se o estado for IDLE, retorna 0 para indicar a pausa no download
            return 0

    # Calcula o tempo de pausa no estado IDLE
    def get_IDLE_time(self, prev_q, x, ln, D_x):
        pass # delta_I = prev_q + x - (ln*x)/D_x - self.q_max