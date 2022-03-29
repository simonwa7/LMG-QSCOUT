import numpy as np
import jaqalpaq as jql
from qscout.v1.std.jaqal_gates import ALL_GATES
from ansatz import prepare_state, add_cnot_gate, add_hadamard_gate


def create_clique1_circuit(circuit_parameters, number_of_qubits):
    builder = jql.core.circuitbuilder.CircuitBuilder(native_gates=ALL_GATES)
    builder, _ = prepare_state(circuit_parameters, number_of_qubits, builder)
    builder.gate("measure_all")
    return builder.build()


def create_clique2_circuit(circuit_parameters, number_of_qubits):
    builder = jql.core.circuitbuilder.CircuitBuilder(native_gates=ALL_GATES)
    builder, qubits = prepare_state(circuit_parameters, number_of_qubits, builder)
    for i in range(number_of_qubits):
        builder = add_hadamard_gate(builder, qubits[i])
    builder.gate("measure_all")
    return builder.build()


def create_clique3_circuit(circuit_parameters, number_of_qubits):
    assert number_of_qubits > 1
    builder = jql.core.circuitbuilder.CircuitBuilder(native_gates=ALL_GATES)
    builder, qubits = prepare_state(circuit_parameters, number_of_qubits, builder)

    builder = add_hadamard_gate(builder, qubits[1])
    builder = add_cnot_gate(builder, qubits[0], qubits[1])
    builder = add_hadamard_gate(builder, qubits[0])

    builder.gate("measure_all")
    return builder.build()


def create_clique4_circuit(circuit_parameters, number_of_qubits):
    assert number_of_qubits > 2
    builder = jql.core.circuitbuilder.CircuitBuilder(native_gates=ALL_GATES)
    builder, qubits = prepare_state(circuit_parameters, number_of_qubits, builder)

    builder = add_hadamard_gate(builder, qubits[2])
    builder = add_cnot_gate(builder, qubits[1], qubits[2])
    builder = add_hadamard_gate(builder, qubits[1])

    builder.gate("measure_all")
    return builder.build()


def get_measurements_for_clique(
    circuit_generator,
    circuit_parameters,
    number_of_qubits,
    number_of_samples,
    **jaqal_emulator_kwargs
):
    circuit = circuit_generator(circuit_parameters, number_of_qubits)
    sim_result = jql.emulator.run_jaqal_circuit(circuit, **jaqal_emulator_kwargs)
    sim_probs = sim_result.subcircuits[0].probability_by_int
    bitstrings = [
        format(i, "0{}b".format(number_of_qubits))[::-1]
        for i in range(2 ** number_of_qubits)
    ]
    samples = list(np.random.choice(bitstrings, size=number_of_samples, p=sim_probs))
    return samples
