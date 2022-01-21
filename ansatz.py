def prepare_state(circuit_parameters, number_of_qubits, circuit_builder):
    assert len(circuit_parameters) == number_of_qubits
    assert number_of_qubits > 0

    # The reduced-unarily-encoded EGO circuit
    qubits = circuit_builder.register("q", number_of_qubits)
    circuit_builder.gate("prepare_all")

    #     Ry
    circuit_builder.gate("Ry", qubits[0], circuit_parameters[0])

    for target_qubit_index in range(1, number_of_qubits):
        #######     Controlled Ry         #######
        target_qubit = qubits[target_qubit_index]
        control_qubit = qubits[target_qubit_index - 1]
        circuit_parameter = circuit_parameters[target_qubit_index]

        circuit_builder.gate("Ry", target_qubit, circuit_parameter / 2)
        circuit_builder = add_cnot_gate(circuit_builder, control_qubit, target_qubit)
        circuit_builder.gate("Ry", target_qubit, -circuit_parameter / 2)
        circuit_builder = add_cnot_gate(circuit_builder, control_qubit, target_qubit)

    return circuit_builder, qubits


def add_cnot_gate(circuit_builder, control, target):
    # CNOT Gate from Maslov (2017)
    circuit_builder.gate("Sy", control)
    circuit_builder.gate("Sxx", control, target)
    circuit_builder.gate("Sxd", control)
    circuit_builder.gate("Sxd", target)
    circuit_builder.gate("Syd", control)
    return circuit_builder


def add_hadamard_gate(circuit_builder, qubit):
    # Hadamard Gate from JAQAL (https://www.sandia.gov/quantum/Projects/quantum_assembly_spec.pdf)
    circuit_builder.gate("Sy", qubit)
    circuit_builder.gate("Px", qubit)
    return circuit_builder
