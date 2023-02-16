from operator import length_hint
import unittest

from qiskit import *
from qiskit.circuit import *
from qiskit import Aer
from qiskit.providers.aer.library import *
from qiskit.quantum_info import Statevector
from qiskit.quantum_info import Operator

from qiskit import execute

import numpy as np
import math

import driver, oracle, grover, counter

def measure_qubits(circ, indices):
# adds classical bits to circuit which is result
# of measuring select qubits
    circ_m = QuantumCircuit(circ.num_qubits, circ.num_clbits)

    num_qubits = len(indices)
    cr = ClassicalRegister(num_qubits)
    circ.add_register(cr)
    circ.measure(indices,range(num_qubits))

    return circ

def test_circuit(dut, input_val, measure_indices, num_shots):
# for a given device-under-test (DUT), initialize circuit with provided input,
# measure each of the specified qubits, and simulate num_shots runs, returning
# results
    circ = QuantumCircuit(dut.num_qubits, dut.num_clbits)
    initial_state = Statevector.from_int(input_val,2**circ.num_qubits)
    circ.set_statevector(initial_state)
    circ.compose(dut, inplace=True)
    measure_qubits(circ, measure_indices)

    sim = Aer.get_backend('aer_simulator')
    result = execute(circ, sim, shots=num_shots).result()

    return result.get_counts(circ)

class PublicTests(unittest.TestCase):

    def test_simple_oracle(self):
        # (var1 or var2) and (~var1 or ~var2)
        # (solutions should be 01 and 10)
        input = [[1,2],[-1,-2]]
        num_vars = 2

        # create oracle
        circ = oracle.get_bitflip_oracle(input, num_vars)

        num_shots = 10

        # input 0b00 and verify output is 0
        counts = test_circuit(circ.copy(), 0b00, {num_vars}, num_shots)
        self.assertEqual(counts, {'0':num_shots})

         # input 0b01 and verify output is 1
        counts = test_circuit(circ.copy(), 0b01, {num_vars}, num_shots)
        self.assertEqual(counts, {'1':num_shots})

    def test_big_oracle(self):
        input = [[1, -2, 3], [2, 3, 4], [-1, -3, 4], [-1, -4]]
        num_vars = 4

        circ = oracle.get_bitflip_oracle(input, num_vars)

        num_shots = 10

        # input 0b00 and verify output is 0
        counts = test_circuit(circ.copy(), 0b1100, {num_vars}, num_shots)
        self.assertEqual(counts, {'1':num_shots})

        counts = test_circuit(circ.copy(), 0b1111, {num_vars}, num_shots)
        self.assertEqual(counts, {'0':num_shots})

        counts = test_circuit(circ.copy(), 0b0, {num_vars}, num_shots)
        self.assertEqual(counts, {'0':num_shots})

        counts = test_circuit(circ.copy(), 0b1001, {num_vars}, num_shots)
        self.assertEqual(counts, {'0':num_shots})

         # input 0b01 and verify output is 1
        counts = test_circuit(circ.copy(), 0b011, {num_vars}, num_shots)
        self.assertEqual(counts, {'1':num_shots})
    
    def test_phase(self):
        input = [[1, -2, 3], [2, 3, 4], [-1, -3, 4], [-1, -4]]
        num_vars = 4

        qc = oracle.get_bitflip_oracle(input, num_vars)
        circ = oracle.bf_to_phase_oracle(qc, num_vars)
        num_shots = 10

        qc = QuantumCircuit(circ.num_qubits, circ.num_clbits)
        qc.append(circ, range(qc.num_qubits))

        state = Statevector.from_int(0b011, 2**qc.num_qubits)
        pls = state.evolve(qc)
        self.assertTrue(np.allclose(pls, -1*state))

        state = Statevector.from_int(0b0, 2**qc.num_qubits)
        pls = state.evolve(qc)
        self.assertTrue(np.allclose(pls, state))

        state = Statevector.from_int(0b1100, 2**qc.num_qubits)
        pls = state.evolve(qc)
        self.assertTrue(np.allclose(pls, -1*state))

        state = Statevector.from_int(0b1111, 2**qc.num_qubits)
        pls = state.evolve(qc)
        self.assertTrue(np.allclose(pls, state))

    def test_edge(self):
        input = [[1], [-1], [2], [-2]]
        num_vars = 2

        circ = oracle.get_bitflip_oracle(input, num_vars)

        num_shots = 10

        # input 0b00 and verify output is 0
        counts = test_circuit(circ.copy(), 0b11, {num_vars}, num_shots)
        self.assertEqual(counts, {'0':num_shots})

        counts = test_circuit(circ.copy(), 0b10, {num_vars}, num_shots)
        self.assertEqual(counts, {'0':num_shots})

        counts = test_circuit(circ.copy(), 0b0, {num_vars}, num_shots)
        self.assertEqual(counts, {'0':num_shots})

        counts = test_circuit(circ.copy(), 0b01, {num_vars}, num_shots)
        self.assertEqual(counts, {'0':num_shots})

        

if __name__ == "__main__":
	unittest.main()