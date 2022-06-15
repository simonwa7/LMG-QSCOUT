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
NUMBER_OF_SAMPLES = 10000
RESULTS_DIR_NAME = "results/point/ionsim_bad_errors_post_selection/"

if not os.path.exists(RESULTS_DIR_NAME):
    os.makedirs(RESULTS_DIR_NAME)

for number_of_qubits, circuit_parameters in zip(
    [1, 2, 3],
    [M1_POINT_PARAMETER_VALUES, M2_POINT_PARAMETER_VALUES, M3_POINT_PARAMETER_VALUES],
):
    # Choose noise model
    # backend = None
    backend = IonSimErrorModel(
        number_of_qubits,
        model="standard",
        params=["dpower12", "dfreq1", "dphase1", "dtime"],
        v0={"dpower12": 5e-3, "dfreq1": 5e3, "dphase1": 5e-2, "dtime": 5e-3},
        sigmas={"dpower12": 5e-3, "dfreq1": 5e3, "dphase1": 5e-2, "dtime": 5e-3},
    )

    cliques_to_measure = [create_clique1_circuit, create_clique2_circuit]
    if number_of_qubits > 1:
        cliques_to_measure.append(create_clique3_circuit)
    if number_of_qubits > 2:
        cliques_to_measure.append(create_clique4_circuit)

    # Will return a 1D list indexed by clique measurements
    all_probability_measurements = [
        get_batched_probabilities_for_clique_on_simulator(
            clique,
            [circuit_parameters],
            number_of_qubits,
            backend=backend,
            post_selection=True,
        )[0]
        for clique in cliques_to_measure
    ]

    probability_data_filename = (
        RESULTS_DIR_NAME + "probability_data_{}_qubits.json".format(number_of_qubits)
    )
    with open(probability_data_filename, "w") as f:
        f.write(json.dumps(all_probability_measurements))
    f.close()

    all_measurements = [
        sample_bitstrings_from_probability_distribution(
            number_of_qubits, NUMBER_OF_SAMPLES, probability_distribution
        )
        for probability_distribution in all_probability_measurements
    ]

    measurement_data_filename = (
        RESULTS_DIR_NAME + "measurement_data_{}_qubits.json".format(number_of_qubits)
    )
    with open(measurement_data_filename, "w") as f:
        f.write(json.dumps(all_measurements))
    f.close()
