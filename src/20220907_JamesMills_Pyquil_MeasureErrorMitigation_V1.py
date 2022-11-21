# https://qiskit.org/textbook/ch-quantum-hardware/measurement-error-mitigation.html
# Useful additional packages
#import matplotlib.pyplot as plt

#matplotlib inline
import numpy as np
from math import pi
from numpy.linalg import inv
import itertools
from datetime import datetime
from random import randrange
import os
import networkx as nx

from pyquil import Program
from pyquil.quil import Pragma
from pyquil.gates import *
from pyquil import get_qc
from pyquil.quantum_processor import NxQuantumProcessor

#qc = get_qc('6q-qvm')  # 'n' is number of qubits for quantum vector machine




qubit = [14, 16]#, 2, 3]  # qubits are numbered by octagon
#edge = [(33, 34)]#, (1, 2), (2, 3), (3, 4)] # second octagon

#topo = nx.from_edgelist(edge)
#device = NxQuantumProcessor(topo)
#qc = get_qc("Aspen-11")
qc = get_qc('32q-qvm')


#NUM_SHOTS = 1024
#from pyquil.api import WavefunctionSimulator
#backend = WavefunctionSimulator().wavefunction(program)
num_qubits = 2
depth = 1

print("num qubits = ",num_qubits)
print("depth = ",depth)
signatures = []

def RQC_Unit(num_qubits, depth, params): # could change params to basis
    p = Program()
    ro = p.declare("ro", "BIT", num_qubits)
    # for i in range(num_qubits):
    #     target_circuit.h([i])
    for dep in range(depth): # could prob delete and run still
        for i in range(num_qubits):
            if params[dep*num_qubits+i]!=0: # then remove dep
                p+=X(14+i*2) # could change X to RX
        # for k in range(num_qubits):
        #     target_circuit.ry(params[dep*num_qubits*2+k+num_qubits], q_reg[k])
    p += MEASURE(14, ro[0])
    p += MEASURE(16, ro[1])#
    p.wrap_in_numshots_loop(10000)
    print(p)
    return p

def build_circuit(params):
    # least_busy(small_devices)
    # backend = least_busy(small_devices)
    the_circuit = RQC_Unit(num_qubits, depth, params)
    #qc.barrier()
    #qc.measure(q[index_meas], c[int(index_meas)])
    #print(the_circuit.draw())
    # result = execute(qc, backend, shots=NUM_SHOTS).result()
    # data = result.get_counts(qc)
    return the_circuit

np.set_printoptions(precision=18)
num_param = num_qubits*depth
#num_param = 2*num_qubits*depth
#params = np.random.rand(num_param)
all_strings = ["".join(seq) for seq in itertools.product("01", repeat=num_qubits)]
print("all_strings",all_strings)
matr = np.zeros(2**num_qubits)
count_str = 0
for strin in all_strings:
    if strin=='00':
        params = np.array([0, 0])
    if strin=='01':
        params = np.array([0, 3.141592653589793])
    if strin=='10':
        params = np.array([3.141592653589793, 0])
    if strin=='11':
        params = np.array([3.141592653589793, 3.141592653589793])
    # print("string=",strin)
    # strin = strin[::-1]
    # params = np.zeros(num_param)
    # index_str = 0
    # for i in strin:
    #     print(i)
    #     if i=='1':
    #         for counterrot in range(depth):
    #             ang_position = counterrot*num_qubits
    #             params[index_str+ang_position] = np.pi
    #             #params[index_str] = np.pi
    #     index_str+=1
    # #params[0] = np.pi
    print("params",params)
    target_circuit = build_circuit(params)
    #print(target_circuit.draw())

    # position is += num_qubits for num loops = depth

    shots_number = 1000
    #for the_qubit in range(num_qubits):
    executable = qc.compile(target_circuit)
    bitstrings = qc.run(executable).readout_data.get("ro")

    len(bitstrings) == shots_number
    arr = [0,0,0,0]
    for a in bitstrings:
        if np.array_equal(a,np.array([0, 0]))==True:
            arr[0]+=1
        if np.array_equal(a,np.array([0, 1]))==True:
            arr[1]+=1
        if np.array_equal(a,np.array([1, 0]))==True:
            arr[2]+=1
        if np.array_equal(a,np.array([1, 1]))==True:
            arr[3]+=1
    #data = arr/10000
    data = [x / 10000 for x in arr]
    print(data)

    # job = execute(target_circuit,
    #               backend,
    #               noise_model=noise_model,
    #               #basis_gates=basis_gates,
    #               shots = shots_number #,
    #               #backend_options={'max_parallel_experiments': 0}
    #               )
    # result = job.result()
    # #print((result.get_counts()).keys())
    # data = result.get_counts()
    # print(data)
    # for key in data:
        #print(type(key))
        #output_target = np.array([key])
        # print(key)

    
    #################################################################################
    # What is the point of this block? It does not seem to be used elsewhere
    #################################################################################
    # loop through all possible strings from 00...0 to 11...1
    all_strings = ["".join(seq) for seq in itertools.product("01", repeat=num_qubits)]
    print(all_strings)
    output_list = []
    for stri in all_strings:
        if stri in data:
            output_list.append(data[stri]/shots_number)
            #print(stri)
            #print(data[stri])
        else:
            #print("none of this one")
            output_list.append(0)
    print(output_list)
    #################################################################################
    # end 
    #################################################################################


    if count_str == 0:
        matr = data
        print("start stackk")
    else:
        #output_list = np.array(output_list)
        matr = np.row_stack((matr, data))
        print("stackk")
        #print("matr=",matr)
    count_str+=1
print("matr=",matr)
inv_matr = inv(matr)
print("inv_matr=",inv_matr)
inv_matr = inv_matr.clip(min=0)
print("no negatives",inv_matr)
# towrite3 = "matrix = " + inv_matr + os.linesep
# outFileID1.write(towrite3)
# outFileID1.flush()


# How do we know what qubits are starting in superposition
