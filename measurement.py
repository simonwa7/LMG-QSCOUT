import numpy as np
import jaqalpaq as jql
from jaqalpaq.generator import generate_jaqal_program


def sample_bitstrings_from_probability_distribution(
    number_of_qubits, number_of_samples, probability_distribution
):
    bitstrings = [
        format(i, "0{}b".format(number_of_qubits))[::-1]
        for i in range(2 ** number_of_qubits)
    ]
    samples = list(
        np.random.choice(bitstrings, size=number_of_samples, p=probability_distribution)
    )
    return samples


def get_batched_probabilities_for_clique_on_simulator(
    circuit_generator,
    circuit_parameters_list,
    number_of_qubits,
    post_selection=False,
    **jaqal_emulator_kwargs
):
    all_probabilities = []
    for circuit_parameters in circuit_parameters_list:
        circuit, junk_state_indices = circuit_generator(
            circuit_parameters, number_of_qubits
        )

        sim_result = jql.emulator.run_jaqal_circuit(circuit, **jaqal_emulator_kwargs)
        probability_distribution = sim_result.subcircuits[0].probability_by_int

        if post_selection:
            print(probability_distribution, sum(probability_distribution))
            for junk_state_index in junk_state_indices:
                probability_distribution[junk_state_index] = 0.00000001
            probability_distribution /= np.linalg.norm(probability_distribution, ord=1)
            print(probability_distribution, sum(probability_distribution))

        all_probabilities.append(list(probability_distribution))

    return all_probabilities


def get_bitstrings_from_measured_probability_distribution(
    number_of_qubits, number_of_samples, probability_distribution
):
    bitstrings = [
        format(i, "0{}b".format(number_of_qubits))[::-1]
        for i in range(2 ** number_of_qubits)
    ]
    counts = [
        int(probability * number_of_samples) for probability in probability_distribution
    ]
    return [bitstrings[i] for i, count in enumerate(counts) for _ in range(count)]


def get_batched_probabilities_for_clique_on_hardware(
    circuit_generator, circuit_parameters_list, number_of_qubits, number_of_samples
):
    # Initialize ansatz circuit using placeholder (theta=0) for parameter values
    empty_parameters = [0 for _ in circuit_parameters_list[0]]
    circuit = circuit_generator(empty_parameters, number_of_qubits)

    # Construct jaqal code for circuit
    circuit_code = "\n".join(
        ["from UserPulseDefinitions.LaserRamseyGates usepulses *"]
        + [generate_jaqal_program(circuit)]
    )

    # Construct dictionary to use when batching circuits
    batch_dictionary = {"__repeats__": number_of_samples}

    # Adding parameter values to loop over in parallel when batching
    #    For example, when given theta1 = [pi/4, pi/2, pi]
    #                            (1/2)theta1 = [pi/8, pi/4, pi/2]
    #                            -(1/2)theta1 = [-pi/8, -pi/4, -pi/2]
    #                            theta2 = [pi/6, pi/8, pi/10]
    #                            (1/2)theta2 = [pi/12, pi/16, pi/20]
    #                            -(1/2)theta2 = [-pi/12, -pi/16, -pi/20]
    #        Then we should run three circuits, with parameter values:
    #            [theta1, (1/2)theta1, -(1/2)theta1, theta2, (1/2)theta2, -(1/2)theta2] =
    #            [pi/4, pi/8, -pi/8, pi/6, pi/12, -pi/12]
    #            [pi/2, pi/4, -pi/4, pi/8, pi/16, -pi/16]
    #            [pi, pi/2, -pi/2, pi/10, pi/20, -pi/20]
    #    len(circuit_parameters_list) number of circuits should be run)
    batch_dictionary.update(
        {
            "theta{}".format(i): [
                parameters[i] for parameters in circuit_parameters_list
            ]
            for i, _ in enumerate(circuit_parameters_list[0])
        }
    )
    batch_dictionary.update(
        {
            "(1/2)theta{}".format(i).format(i): [
                parameters[i] / 2 for parameters in circuit_parameters_list
            ]
            for i, _ in enumerate(circuit_parameters_list[0])
        }
    )
    batch_dictionary.update(
        {
            "-(1/2)theta{}".format(i).format(i): [
                -parameters[i] / 2 for parameters in circuit_parameters_list
            ]
            for i, _ in enumerate(circuit_parameters_list[0])
        }
    )

    # Run code on device and record probabilities of measurement outcomes indexed by parameter values
    # return [list(np.random.uniform(size=len(circuit_parameters_list)))]

    return [
        experiment.subcircuits[0].probability_by_int
        for experiment in jql.run.run_jaqal_batch(circuit_code, batch_dictionary)
    ]
