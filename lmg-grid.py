from parameters import M1_GRID_PARAMETERS, M2_GRID_PARAMETERS, M3_GRID_PARAMETERS
from parameters import (
    M1_POINT_PARAMETER_VALUES,
    M2_POINT_PARAMETER_VALUES,
    M3_POINT_PARAMETER_VALUES,
)
from ansatz import (
    create_clique1_circuit,
    create_clique2_circuit,
    create_clique3_circuit,
    create_clique4_circuit,
)
from measurement import (
    get_batched_probabilities_for_clique_on_simulator,
    sample_bitstrings_from_probability_distribution,
)

import json
import os
from qscout.v1.std.ionsim import IonSimErrorModel
import jaqalpaq.core.result

jaqalpaq.core.result.ProbabilisticSubcircuit.CUTOFF_FAIL = 1e-4
jaqalpaq.core.result.ProbabilisticSubcircuit.CUTOFF_WARN = 1e-4
NUMBER_OF_SAMPLES = 2 ** 13

for number_of_qubits, grid_parameters in zip(
    [1, 2, 3],
    [M1_GRID_PARAMETERS, M2_GRID_PARAMETERS, M3_GRID_PARAMETERS],
):
    RESULTS_DIR_NAME = "results/grid/ionsim_4_1_22/{}/".format(number_of_qubits)

    if not os.path.exists(RESULTS_DIR_NAME):
        os.makedirs(RESULTS_DIR_NAME)

    # Choose noise model
    # backend=None
    backend = IonSimErrorModel(
        number_of_qubits,
        model="standard",
        params=["dpower12", "dfreq1", "dphase1", "dtime"],
        v0={"dpower12": 5e-4, "dfreq1": 5e3, "dphase1": 5e-2, "dtime": 5e-3},
        sigmas={"dpower12": 5e-4, "dfreq1": 5e3, "dphase1": 5e-2, "dtime": 5e-3},
    )

    cliques_to_measure = [create_clique1_circuit, create_clique2_circuit]
    if number_of_qubits > 1:
        cliques_to_measure.append(create_clique3_circuit)
    if number_of_qubits > 2:
        cliques_to_measure.append(create_clique4_circuit)

    # Will return a 2D list, first index being clique measurements, second index being parameter values
    all_probability_measurements = [
        get_batched_probabilities_for_clique_on_simulator(
            clique,
            grid_parameters,
            number_of_qubits,
            backend=backend,
        )
        for clique in cliques_to_measure
    ]

    data_filename = RESULTS_DIR_NAME + "probability_data_{}_qubits.json".format(
        number_of_qubits
    )
    with open(data_filename, "w") as f:
        f.write(json.dumps(all_probability_measurements))
    f.close()

    # Reorder probability distributions
    reordered_probability_measurements = [
        [[] for _ in all_probability_measurements]
        for _ in all_probability_measurements[0]
    ]
    for i, clique_probability_distributions in enumerate(all_probability_measurements):
        for j, probability_distribution in enumerate(clique_probability_distributions):
            reordered_probability_measurements[j][i] = probability_distribution

    for i, probability_distributions_for_parameters in enumerate(
        reordered_probability_measurements
    ):
        measurements_for_parameters = []
        for j, probability_distribution_for_clique in enumerate(
            probability_distributions_for_parameters
        ):
            measurements = sample_bitstrings_from_probability_distribution(
                number_of_qubits, NUMBER_OF_SAMPLES, probability_distribution_for_clique
            )
            measurements_for_parameters.append(measurements)

        measurement_data_filename = (
            RESULTS_DIR_NAME + "measurement_data_point_{}.json".format(i + 1)
        )
        with open(measurement_data_filename, "w") as f:
            f.write(json.dumps(measurements_for_parameters))
        f.close()
