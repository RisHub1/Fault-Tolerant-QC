from qiskit import *
import numpy as np
from typing import List

import grover

def qft(n: int) -> QuantumCircuit:
    """Returns a QuantumCircuit implementing the Quantum Fourier Transform
    for n bits
    Args:
        n: Width of the quantum circuit"""
    qc = QuantumCircuit(n)

    # for every qubit
    for i in reversed(range(n)):
        # apply appropriate controlled-phase gates
        qc.h(i)
        for j in range(i):
            qc.cp(np.pi/2**(i-j), j, i)
            
    # swap pair of qubits
    for i in range(n//2):
        qc.swap(i, n-i-1)
    return qc


def quantum_counter(cnf: List[List[int]], num_vars: int, precision: int) -> QuantumCircuit:
    """Returns quantum circuit implementing quantum counter algorithm,
    which estimates the number of solutions to a given CNF function
    Args:
        cnf: List of clauses of literals
        num_vars: number of distinct variables in CNF
        precision: how many bits should be used to encode result"""
    n = num_vars
    t = precision
    qft_dagger = qft(t).to_gate().inverse()
    cgrov = grover.grover_iteration(cnf, n).to_gate().control()
    qc = QuantumCircuit(n + t + len(cnf) + 1)

    for qubit in range(t + n):
        qc.h(qubit)

    # Begin controlled Grover iterations
    iterations = 1
    for qubit in range(t):
        for i in range(iterations): 
            qc.append(cgrov, [qubit] + [*range(t, n + t + len(cnf) + 1)])
        iterations *= 2
        
    # Do inverse QFT on counting qubits
    qc.append(qft_dagger, range(t))

    return qc


