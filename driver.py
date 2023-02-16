from operator import length_hint
import unittest

from qiskit import *
from qiskit.circuit import *
from qiskit import Aer
from qiskit.providers.aer.library import *
from qiskit.quantum_info import Statevector

from qiskit import execute

import numpy as np
import math

import sys
import csv

import counter, grover, oracle

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

def calc_solutions(value, num_vars, precision): 
    theta = 2 * np.pi * (value / (2**precision))
    m = (2**num_vars) * (np.sin(theta/2)**2)
    return m

def satisfy(result, cnf, pot): 
    # print(cnf)
    for clause in cnf: 
        sat = False 
        for i in clause:
            if i < 0 and int(pot[(-1*i)]) == 0: 
                sat = True 
            elif i > 0 and int(pot[i]) == 1:
                sat = True 
        if not sat: 
            return False
    return True 

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: ./%s [csv_file]" % sys.argv[0])
    print()
    cnf = []
    dict = {}
    with open(sys.argv[1]) as f: 
        lines = f.readlines()
        count = 1
        for line in lines: 
            clause = []
            els = line.strip().split(',')
            for el in els: 
                mult = False
                if el[0] == '~': 
                    el = el.replace('~', '')
                    mult = True 
                if not (el in dict): 
                    dict[el] = count
                    count += 1
                if mult: 
                    clause.append(dict[el] * -1)
                else: 
                    clause.append(dict[el])
            cnf.append(clause)

    num_vars = len(dict)

    print("COUNT - Counting solutions for {0} variables..." .format(num_vars))

    precision = 5 
    qc = counter.quantum_counter(cnf, num_vars, precision)
    circ = qc.to_gate()

    num_shots = 1000
    counts = test_circuit(circ.copy(), 0, range(precision), num_shots)

    result = max(counts, key=counts.get)
    value = int(result, 2)
    m = calc_solutions(value, num_vars, precision)
    sols = round(m, 2)
    f_sols = "{:.2f}".format(sols)
    if sols == 0: 
        print("COUNT - Estimated number of solutions: 0.00")
    else:
        print("COUNT - Estimated number of solutions: {0}" .format(f_sols))

    n = 2**num_vars 
    
    if round(sols) == 0:
        print("COUNT - No solutions expected, exiting")
        return
    r = (np.pi / 4) * math.sqrt(n/round(sols))
    
    iterations = round(r, 2)
    f_iterations = "{:.2f}".format(iterations)
    print("COUNT - Estimated number of Grover Iterations: {0}" .format(f_iterations))

    while r < 1: 
        print("COUNT - Solution space too large, rerunning with additional variable")
        num_vars += 1
        print("COUNT - Counting solutions for {0} variables..." .format(num_vars))
        cnf.append([(-1 * num_vars)])
        precision = 5 
        qc = counter.quantum_counter(cnf, num_vars, precision)
        circ = qc.to_gate()

        num_shots = 1000
        counts = test_circuit(circ.copy(), 0, range(precision), num_shots)

        result = max(counts, key=counts.get)
        value = int(result, 2)
        m = calc_solutions(value, num_vars, precision)
        sols = round(m, 2)
        n = 2**num_vars
        r = (np.pi / 4) * math.sqrt(n/round(sols))
        f_sols = "{:.2f}".format(sols)
        print("COUNT - Estimated number of solutions: {0}" .format(f_sols))
        iterations = round(r, 2)
        f_iterations = "{:.2f}".format(iterations)
        print("COUNT - Estimated number of Grover Iterations: {0}" .format(f_iterations))

    iter = math.trunc(iterations)

    qc = grover.grover(cnf, num_vars, iter)
    print("GROVER - Running search with {0} Grover iteration(s)" .format(iter))

    num_shots = 1000
    circ = qc.to_gate()
    counts = test_circuit(circ.copy(), 0, range(num_vars), num_shots)
    result = max(counts, key=counts.get)
    # print(result)
    # print(dict)
    pot = {}
    count = 1
    for i in reversed(range(len(result))): 
        pot[count] = result[i]
        count += 1
    # print(pot)
    if satisfy(result, cnf, pot):
        print( "GROVER - Solution identified: ", end = '')
        i = 1
        while i < num_vars: 
            if int(pot[i]) == 1:
                print(list(dict.keys())[list(dict.values()).index(i)], end = ' ')
            i += 1
        print()
    else: 
        iter = 10
        qc = grover.grover(cnf, num_vars, iter)
        print("GROVER - Running search with {0} Grover iteration(s)" .format(iter))
        num_shots = 1000
        circ = qc.to_gate()
        counts = test_circuit(circ.copy(), 0, range(num_vars), num_shots)
        result = max(counts, key=counts.get)
        # print(result)
        # print(dict)
        pot = {}
        count = 1
        for i in reversed(range(len(result))): 
            pot[count] = result[i]
            count += 1
        if satisfy(result, cnf, pot):
            print( "GROVER - Solution identified: ", end = '')
            i = 1
            while i < num_vars: 
                if int(pot[i]) == 1:
                    print(list(dict.keys())[list(dict.values()).index(i)], end = ' ')
                i += 1
            print()
        else: 
            print("GROVER: No solution found after 10 attempts")

if __name__ == "__main__":
    main()

