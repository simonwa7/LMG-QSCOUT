# Ansatz Circuit Construction
import jaqalpaq as jql
from qscout.v1.std.jaqal_gates import ALL_GATES


def _prepare_state(
    circuit_parameters,
    number_of_qubits,
    circuit_builder,
):
    """Constructs the circuit to prepare the initial state that is used during measurement of all cliques"""
    assert len(circuit_parameters) == number_of_qubits
    assert number_of_qubits > 0

    # Must create three distinct lists of parameters (theta, theta/2, -theta) for re-evaluation of the circuit
    #     using different theta values when batching
    full_circuit_parameters = [
        circuit_builder.let("theta{}".format(i), circuit_parameter)
        for i, circuit_parameter in enumerate(circuit_parameters)
    ]
    positive_halved_parameters = [
        circuit_builder.let("(1/2)theta{}".format(i), circuit_parameter / 2)
        for i, circuit_parameter in enumerate(circuit_parameters)
    ]
    negative_halved_parameters = [
        circuit_builder.let("-(1/2)theta{}".format(i), -circuit_parameter / 2)
        for i, circuit_parameter in enumerate(circuit_parameters)
    ]

    # The reduced-unarily-encoded EGO circuit
    qubits = circuit_builder.register("q", number_of_qubits)
    circuit_builder.gate("prepare_all")

    #     Ry
    circuit_builder.gate("Ry", qubits[0], full_circuit_parameters[0])

    for target_qubit_index in range(1, number_of_qubits):
        #######     Controlled Ry         #######
        target_qubit = qubits[target_qubit_index]
        control_qubit = qubits[target_qubit_index - 1]
        positive_halved_parameter = positive_halved_parameters[target_qubit_index]
        negative_halved_parameter = negative_halved_parameters[target_qubit_index]

        circuit_builder.gate("Ry", target_qubit, positive_halved_parameter)
        circuit_builder = _add_cnot_gate(circuit_builder, control_qubit, target_qubit)
        circuit_builder.gate("Ry", target_qubit, negative_halved_parameter)
        circuit_builder = _add_cnot_gate(circuit_builder, control_qubit, target_qubit)

    return circuit_builder, qubits


def _add_cnot_gate(circuit_builder, control, target):
    """CNOT Gate from Maslov (2017)"""
    circuit_builder.gate("Sy", control)
    circuit_builder.gate("Sxx", control, target)
    circuit_builder.gate("Sxd", control)
    circuit_builder.gate("Sxd", target)
    circuit_builder.gate("Syd", control)
    return circuit_builder


def _add_hadamard_gate(circuit_builder, qubit):
    """Hadamard Gate from JAQAL (https://www.sandia.gov/quantum/Projects/quantum_assembly_spec.pdf)"""
    circuit_builder.gate("Sy", qubit)
    circuit_builder.gate("Px", qubit)
    return circuit_builder


def create_clique1_circuit(circuit_parameters, number_of_qubits):
    """Constructs the ansatz circuit used to measure clique 1 (All Z-basis)"""
    builder = jql.core.circuitbuilder.CircuitBuilder(native_gates=ALL_GATES)

    builder, _ = _prepare_state(
        circuit_parameters,
        number_of_qubits,
        builder,
    )
    builder.gate("measure_all")

    junk_state_indices = []
    if number_of_qubits == 1:
        junk_state_indices = []
    elif number_of_qubits == 2:
        junk_state_indices = [2]
    elif number_of_qubits == 3:
        junk_state_indices = [2, 4, 5, 6]

    return builder.build(), junk_state_indices


def create_clique2_circuit(circuit_parameters, number_of_qubits):
    """Constructs the ansatz circuit used to measure clique 2 (All X-basis)"""
    builder = jql.core.circuitbuilder.CircuitBuilder(native_gates=ALL_GATES)

    builder, qubits = _prepare_state(
        circuit_parameters,
        number_of_qubits,
        builder,
    )

    # Hadamard rotation on all qubits to change measurement context
    for i in range(number_of_qubits):
        builder = _add_hadamard_gate(builder, qubits[i])
    builder.gate("measure_all")
    return builder.build(), []


def create_clique3_circuit(circuit_parameters, number_of_qubits):
    """Constructs the ansatz circuit used to measure clique 3"""
    assert number_of_qubits > 1
    builder = jql.core.circuitbuilder.CircuitBuilder(native_gates=ALL_GATES)

    builder, qubits = _prepare_state(
        circuit_parameters,
        number_of_qubits,
        builder,
    )

    builder = _add_hadamard_gate(builder, qubits[1])
    builder = _add_cnot_gate(builder, qubits[0], qubits[1])
    builder = _add_hadamard_gate(builder, qubits[0])

    builder.gate("measure_all")
    return builder.build(), []


def create_clique4_circuit(circuit_parameters, number_of_qubits):
    """Constructs the ansatz circuit used to measure clique 4"""
    assert number_of_qubits > 2
    builder = jql.core.circuitbuilder.CircuitBuilder(native_gates=ALL_GATES)

    builder, qubits = _prepare_state(
        circuit_parameters,
        number_of_qubits,
        builder,
    )

    builder = _add_hadamard_gate(builder, qubits[2])
    builder = _add_cnot_gate(builder, qubits[1], qubits[2])
    builder = _add_hadamard_gate(builder, qubits[1])

    builder.gate("measure_all")
    return builder.build(), []
