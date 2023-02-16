import oracle
from qiskit import *
from typing import List

def diffuser(num_vars: int) -> QuantumCircuit:
    """Returns QuantumCircuit that rotates the state around |s>
    Args:
        num_vars: How many variables are input into the diffuser"""
    n = num_vars
    qc = QuantumCircuit(n)

    if not n == 1: 
        for qubit in range(n):
            qc.h(qubit)
        # Apply transformation |00..0> -> |11..1> (X-gates)
        for qubit in range(n):
            qc.x(qubit)
        # Do multi-controlled-Z gate
        qc.h(n-1)
        qc.mct(list(range(n-1)), n-1)  # multi-controlled-toffoli
        qc.h(n-1)
        # Apply transformation |11..1> -> |00..0>
        for qubit in range(n):
            qc.x(qubit)
        # Apply transformation |00..0> -> |s>
        for qubit in range(n):
            qc.h(qubit)
    else: 
        qc.h(0)
        qc.x(0)
        qc.z(0)
        qc.x(0)
        qc.h(0)
    qc.z(0)
    qc.x(0)
    qc.z(0)
    qc.x(0)

    return qc

def grover_iteration(cnf: List[List[int]], num_vars: int) -> QuantumCircuit:
    """Returns a QuantumCircuit implementing a single Grover iteration
    (i.e. phase oracle of provided cnf + diffuser)
    Args:
        cnf: List of clauses of literals
        num_vars: How many variables are taken as input to the oracle"""
    bf_oracle = oracle.get_bitflip_oracle(cnf, num_vars)
    phase_oracle = oracle.bf_to_phase_oracle(bf_oracle, num_vars)
    qc = QuantumCircuit(phase_oracle.num_qubits)

    qc.append(phase_oracle, range(phase_oracle.num_qubits))
    qc.append(diffuser(num_vars).to_gate(), range(num_vars))

    return qc

def grover(cnf: List[List[int]], num_vars: int, num_iters: int) -> QuantumCircuit:
    """Returns a QuantumCircuit implementing a full Grover implementation
    with specified number of iterations
    Args:
        cnf: List of clauses of literals
        num_vars: How many variables are taken as input to the oracle
        num_iters: How many Grover iterations should be included"""
    qc = QuantumCircuit(num_vars + len(cnf) + 1)

    qc.h(range(num_vars))

    for i in range(num_iters): 
        qc.append(grover_iteration(cnf, num_vars).to_gate(), range(qc.num_qubits))

    return qc