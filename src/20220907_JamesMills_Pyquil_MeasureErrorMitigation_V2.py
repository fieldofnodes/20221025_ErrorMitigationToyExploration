########################################################################################
# Author  : Jonathan Miller
# Date    : 20220908
# Aim     : Code an error correction algorithm
########################################################################################

# Load non pyquil packages
import numpy as np 
np.set_printoptions(precision=18)
from math import pi
from numpy.linalg import inv
import itertools
from datetime import datetime
from random import randrange
import os
import networkx as nx
import matplotlib.pyplot as plt

# end


# Load pyquil associated packages
from pyquil import Program
from pyquil.quil import Pragma
from pyquil.gates import *
from pyquil import get_qc
from pyquil.quantum_processor import NxQuantumProcessor
# end

##########################################################################################
# Load functions/methods
##########################################################################################


def RQC_Unit(num_qubits, depth, params, shots,qubit_select):
    """
    `RQC_Unit` can be used with a 2 qubit system
    Set up circuit with an `X` gate. For non-zero enries of the params value, apply `X` gate. Measure each qubit and run `shots` times.

    :num_qubits: an integer, give number of qubits to apply in the circuit
    :depth: an integer, how deep is the circuit
    :params: an array, apply X gate on qubit
    :shots: how many times to run experiement
    :qubit_select: what qubits to select
    """
    p = Program()
    ro = p.declare("ro", "BIT", num_qubits)
    for dep in range(depth):
        for i in range(num_qubits):
            if params[dep*num_qubits+i]!=0: 
                p+=X(qubit_select[0]+i*2) 
        
    p += MEASURE(qubit_select[0], ro[0])
    p += MEASURE(qubit_select[1], ro[1])#
    p.wrap_in_numshots_loop(shots)
    return p

def normalise_elements(qubit_count,shots):
    """
    Normalises the number `qubit_state` related to a specific qubit state our of the number of `shots`

    :qubit_state: an integer, given a state, the number of times the circuit measured in said state.
    :shots: an integer, the total number of shots 
    """
    return qubit_count / shots


normalise_elements_anon = lambda qubit_count : normalise_elements(qubit_count,shots)
""" Takes `normalise_elements` function and produces a one-input function, the number of qubits in a state, `qubit_state`."""


def run_circuit(num_qubits, depth, params, shots,qubit_select):
    """
    Run circuit and execute `shots` times

    :num_qubits: an integer, give number of qubits to apply in the circuit
    :depth: an integer, how deep is the circuit
    :params: an array, apply X gate on qubit
    :shots: how many times to run experiement
    :qubit_select: what qubits to select    
    """
    target_circuit = RQC_Unit(num_qubits, depth, params, shots,qubit_select)
    executable = qc.compile(target_circuit)

    return qc.run(executable).readout_data.get("ro")


def count_single_state(bitstrings,possible_qubit):
    """
    Count number of qubits states
    
    :bitstrings: a array of lists on binary such that each element is a result of a shot of a quantum circuit
    :possible_qubit: a list of binary such that th qubit state is said vector
    """
    return [np.array_equal(b,np.array(possible_qubit)) for b in bitstrings].count(True)


count_states = lambda possible_arrays : count_single_state(bitstrings,possible_arrays)
"""
Anonymous function of one argument to apply the map function
"""

##########################################################################################
# End
##########################################################################################

# Get a qvm simulator
qc = get_qc('32q-qvm',noisy=True) # Why 32?

# Stipulate which qubits to use
qubit_select = [14, 16] # Why these ?

# Define the number of qubits
num_qubits = 2

# Define the depth
depth = 1

# Define qubit labels and gate inputs
qubit_dict  = {
    '00': np.array([0, 0]) , 
    '01' : np.array([0, np.pi]), 
    '10' : np.array([np.pi, 0]), 
    '11' : np.array([np.pi, np.pi])}

# Define pattern to match for circuit results
possible_arrays = [[0,0],[0,1],[1,0],[1,1]]

# Define an empty list
complete_quantum_states = []

# Define number of shots 
shots = 1_000

for key in qubit_dict:
    params = qubit_dict[key]
    bitstrings = run_circuit(num_qubits, depth, params, shots,qubit_select)
    state_counts = list(map(count_states,possible_arrays))
    normalise_state_counts = list(map(normalise_elements_anon,state_counts))
    complete_quantum_states.append(normalise_state_counts)
    



np.array(complete_quantum_states)
inverse_complete_quantum_states_no_negatives = inv(complete_quantum_states).clip(min=0) 
inverse_complete_quantum_states_no_negatives
