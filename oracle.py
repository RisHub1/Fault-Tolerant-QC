from qiskit import QuantumCircuit

from qiskit.circuit import QuantumRegister, ClassicalRegister, AncillaRegister
from qiskit.circuit.library.standard_gates import SXGate, MCXGate

from typing import List
import numpy as np

# RESTRICTIONS ON CNF (you do not need to verify these):
# every variable appears at least once in CNF
# no variable appears twice in one term
# variable IDs always appear in ascending order (ignoring minus signs)
# names appear in the same relative order for each term
# (see spec for examples of invalid CNFs)


def bf_to_phase_oracle(bf_oracle: QuantumCircuit, num_vars: int) -> QuantumCircuit:
    """Returns a QuantumCircuit that flips the phase if f(x)=1
    Args:
        bf_oracle: Bitflip oracle to be converted to a phase oracle
        num_vars: How many variables are taken as input to the oracle"""
    qc = QuantumCircuit(bf_oracle.num_qubits)
    qc.x(num_vars)
    qc.h(num_vars)
    qc.append(bf_oracle, range(bf_oracle.num_qubits))
    qc.h(num_vars)
    qc.x(num_vars)
    return qc.to_gate()

def get_bitflip_oracle(cnf: List[List[int]], num_vars: int) -> QuantumCircuit:
    """Returns a QuantumCircuit that flips qubit[num_var] if f(x) = 1
    Args:
        cnf: Array of clauses of literals
        num_vars: How many variables are taken as input to the oracle"""
    l = len(cnf) 
    inputs = QuantumRegister(num_vars, "inputs")
    output = QuantumRegister(1, "output")
    ancilla = AncillaRegister(l, "ancilla")
    qc = QuantumCircuit(inputs, output, ancilla)
    
    abit = num_vars + 1
    for list in cnf: 
        state = 0b0
        ls = []
        ind = 0
        for i in list: 
            if i > 0: 
                ls.append(i - 1)
                state += 1 << ind
            else: 
                ls.append(i * -1 - 1)
            ind += 1
        for i in ls: 
            qc.x(i) 
        gate = MCXGate(len(ls), ctrl_state=state)
        ls.append(abit)
        qc.append(gate, ls)
        qc.x(num_vars) 
        for i in ls: 
            qc.x(i)
        abit += 1

    gate = MCXGate(l)
    ls = np.arange(num_vars + 1, num_vars + 1 + l).tolist()
    ls.append(num_vars)
    qc.append(gate, ls)

    abit = num_vars + 1
    for list in cnf: 
        state = 0b0
        ls = []
        ind = 0
        for i in list: 
            if i > 0: 
                ls.append(i - 1)
                state += 1 << ind
            else: 
                ls.append(i * -1 - 1)
            ind += 1
        for i in ls: 
            qc.x(i) 
        gate = MCXGate(len(ls), ctrl_state=state)
        ls.append(abit)
        qc.append(gate, ls)
        qc.x(num_vars) 
        for i in ls: 
            qc.x(i)
        abit += 1
    return qc.to_gate()

    
