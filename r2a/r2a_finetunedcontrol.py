# -*- coding: utf-8 -*-
# @autores: Davi Salomão Soares Corrêa (davi.salomao@aluno.unb.br) 
#           Francisco Henrique da Silva Costa (francisco.henrique@aluno.unb.br)
#           Matheus Teixeira de Sousa (teixeira.sousa@aluno.unb.br)
#
# @disciplina: Transmissão de dados - Turma A - Grupo 1
#
# Esse código implementa o algortimo adaptativo para streaming proposto em "A Fine-Tuned
# Control-Theoretic Approach for Dynamic Adaptive Streaming Over HTTP" que será aplicado
# no framework pyDash disponível em https://github.com/mfcaetano/pydash

from player.parser import *
from base.whiteboard import *
from r2a.ir2a import IR2A
import time


class R2A_FineTunedControl(IR2A):
    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        # Control System
        self.qi = [] # list of qualities
        self.q0 = 30 # buffer time reference (constant) [s]
        self.qt = 0 # buffer time [s]
        self.D = 1 # average download rate [kbps]
        self.x = 1 # chunk duration [s]
        self.de = 1 # decoder extraction
        self.S = 0 # chunk size [kb]
        self.te = 0 # chunk download end [s]
        self.ts = 0 # chunk download start [s]
        self.lk = 0 # chunk bitrate / quality level [kbps]
        self.l0 = 0 # lowest quality level [kbps]
        # State Machine
        self.q_max = self.q0 + 20 # maximum security limit [s]
        self.q_min = self.q0 - 20 # minimum security limit [s]
        self.m = 3 # m chunk(s) to evaluate l+
        self.n = 1 # n chunk(s) to evaluate l-
        self.quality = 10 # adaptive quality
        self.statemachine = FSM(self.q0, self.q_max, self.q_min, self.m, self.n)
    
    def handle_xml_request(self, msg):
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # Capture the list with available qualities
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # FSM receives the selected video level l(k) and buffer time q(t) from the control system
        self.statemachine.set_params(self.lk,self.qt)
        self.statemachine.set_state()
        print( "\n\n",self.statemachine.current_state,"\n")
        # FSM evaluates lc states according to safety limits
        if(self.statemachine.current_state!='lc'):
            if(self.statemachine.current_state=='l-'):
                if(self.quality!=0):
                    self.quality-=2
            elif(self.statemachine.current_state=='l+' or self.statemachine.current_state=='IDLE'):
                if(self.quality<len(self.qi)-3):       
                    self.quality+=2
            elif(self.statemachine.current_state=='l0'):
                self.quality=0   
        msg.add_quality_id(self.qi[self.quality]) 
        self.ts = time.perf_counter()
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # Selection of quality level l(k) and buffer time q(t) in the control system
        self.te = time.perf_counter() - self.ts
        self.S = msg.get_bit_length()
        self.D = self.S/(self.te*1000*8)
        self.qt = self.whiteboard.get_amount_video_to_play()
        self.l0 = self.D/self.de
        self.lk = (((self.qt-self.q0)/self.x) + 1)*self.l0
        self.send_up(msg)
    def initialize(self):
        pass

    def finalization(self):
        pass

# Finite state machine class (FSM)
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

    # List of states
    def set_params(self, l, q):
        self.current_l = l
        self.current_q = q
        self.states = {'lc': self.prev_lc, 'l0': self.min_rate, 'l+': self.current_l, 'l-': self.current_l, 'IDLE': self.current_l}

    # Current conditions
    def get_conditions(self):
        # q(t) < q_min --> l0 state
        if (self.current_q < self.q_min):
            return 'l0'

        # q(t) > q_max --> IDLE state
        elif (self.current_q > self.q_max):
            return 'IDLE'
        
        # q_min <= q(t) <= q_max --> l+, l- or lc
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

    # Update state and return next lc
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
            # IDLE state --> pause in download
            return 0

    # Calculates pause time in IDLE state
    def get_IDLE_time(self, prev_q, x, ln, D_x):
        pass # delta_I = prev_q + x - (ln*x)/D_x - self.q_max