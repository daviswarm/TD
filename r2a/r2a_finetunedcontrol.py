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
import numpy as np

# Classe da máquina de estados finitos (FSM)
class FSM():

    def __init__(self, qi_0, q_max, q_min, m, n):
        self.min_rate = qi_0 # Valor mínimo da taxa de transmissão
        self.current_state = 'lc' # Estado inicial
        self.prev_state = 'lc' # Estado anterior
        self.prev_lc = 0 # Valor lc anterior
        self.prev_q = 0 # Valor q(t-1)
        self.q_max = q_max # buffer máximo
        self.q_min = q_min # buffer mínimo
        self.current_l = 0 # Valor l(k) 
        self.current_q = 0 # Valor q(t)
        self.m_chks = 0 # Contador de m
        self.m_max = m # Máximo de m
        self.n_chks = 0 # Contador de n
        self.n_max = n # Máximo de n

    # Define o dicionário com os estados
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
                self.n_chks = 0
                return 'l+'
            
            elif (self.current_l > self.prev_lc and self.m_chks < self.m_max):
                self.m_chks += 1
                return 'lc'
            
            elif (self.current_l < self.prev_lc and self.n_chks >= self.n_max):
                self.n_chks = 0
                self.m_chks = 0
                return 'l-'
            
            elif (self.current_l < self.prev_lc and self.n_chks < self.n_max):
                self.n_chks += 1
                return 'lc'
            
            else:
                return 'lc'

    # Atualiza o estado e retorna o próximo lc
    def set_state(self):
        self.prev_state = self.current_state
        self.current_state = self.get_conditions()
        self.prev_lc = self.states[self.current_state]

        return self.states[self.current_state]

    # Calcula o tempo de pausa no estado IDLE
    def get_IDLE_time(self, l, D_x, x):
        delta_I = self.prev_q + x - (l*x)/D_x - self.q_max
        return delta_I

class R2A_FineTunedControl(IR2A):

    def __init__(self, id):
        IR2A.__init__(self, id)
        self.parsed_mpd = ''
        
        # Sistema de controle
        self.qi = [] # lista de qualidade
        self.q0 = 30 # refernência do buffer
        self.qt = 0 # buffer
        self.D = 1 # taxa de download
        self.x = 1 # tamanho do pedaço de vídeo
        self.de = 1 # taxa de extração
        self.S = 0 # tamanho do pedaço de vídeo
        self.te = 0 # tempo final do download
        self.ts = 0 # tempo inicial do download
        self.lk = 0 # qualidade l(k)
        self.l0 = 0 # qualidade l(0)
        self.kp = 0.01 # ganho proporcional

        # Máquina de estados
        self.q_max = self.q0 + 20 # limite superior
        self.q_min = self.q0 - 20 # limite inferior
        self.m = 10 # m
        self.n = 3 # n

        self.t0 = time.perf_counter() # tempo inicial
        self.states = {'lc': 0, 'l0': 0, 'l+': 0, 'l-': 0, 'IDLE': 0} # estados

    def handle_xml_request(self, msg):
        self.ts = time.perf_counter()
        self.send_down(msg)

    def handle_xml_response(self, msg):
        # Captura a lista de qualidades disponíveis
        self.parsed_mpd = parse_mpd(msg.get_payload())
        self.qi = self.parsed_mpd.get_qi()
        self.statemachine = FSM(self.qi[0], self.q_max, self.q_min, self.m, self.n)
        
        # Calcula o valor do lk
        self.te = time.perf_counter() - self.ts
        self.S = msg.get_bit_length()
        self.D = self.S/(self.te)
        self.l0 = self.D/self.de
        G = -self.de*self.kp/self.x
        self.lk = (np.exp(G*(time.perf_counter()-self.t0))/self.x + 1)*self.l0

        self.send_up(msg)

    def handle_segment_size_request(self, msg):
        # Passa os valores de lk e q
        self.statemachine.set_params(self.lk, self.qt)
        l = self.statemachine.set_state()

        # Verifica se está no estado IDLE e dá uma pausa
        if (self.statemachine.current_state == 'IDLE'):
            interval = self.statemachine.get_IDLE_time(self.lk, self.D, self.x)
            time.sleep(interval)

        # Seleciona o maior valor que satisfaz o l definido pelo FSM
        selected_qi = self.qi[0]
        for i in self.qi:
            if l > i:
                selected_qi = i
        
        # Incrementa o contador do estado
        self.states[self.statemachine.current_state] += 1

        msg.add_quality_id(selected_qi) 
        self.ts = time.perf_counter()
        self.send_down(msg)

    def handle_segment_size_response(self, msg):
        # Calcula a qualidade l(k) e o tempo de buffer
        self.te = time.perf_counter() - self.ts
        self.S = msg.get_bit_length()
        self.D = self.S/(self.te)
        self.qt = self.whiteboard.get_amount_video_to_play()
        self.l0 = self.D/self.de
        G = -self.de*self.kp/self.x
        self.lk = (np.exp(G*(time.perf_counter()-self.t0))/self.x + 1)*self.l0

        self.statemachine.prev_q = self.qt

        self.send_up(msg)

    def initialize(self):
        pass

    def finalization(self):
        states_vector = [self.states['lc'], self.states['l0'], self.states['l+'], self.states['l-'], self.states['IDLE']]
        qi = self.whiteboard.get_playback_qi()
        buffer = self.whiteboard.get_playback_buffer_size()
        pauses = self.whiteboard.get_playback_pauses()
        history = self.whiteboard.get_playback_history()

        # Salva os dados
        np.save('results/qi.npy', qi)
        np.save('results/buffer.npy', buffer)
        np.save('results/pauses.npy', pauses)
        np.save('results/history.npy', history)
        np.save('results/states.npy', states_vector)
