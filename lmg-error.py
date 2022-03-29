from parameters import (
    M1_POINT_PARAMETER_VALUES,
    M2_POINT_PARAMETER_VALUES,
    M3_POINT_PARAMETER_VALUES,
)
from measurement import (
    create_clique1_circuit,
    create_clique2_circuit,
    create_clique3_circuit,
    create_clique4_circuit,
    get_measurements_for_clique,
)
import os
import jaqalpaq
from qscout.v1.std.ionsim import IonSimErrorModel
import jaqalpaq.core.result

jaqalpaq.core.result.ProbabilisticSubcircuit.CUTOFF_FAIL = 1e-4
jaqalpaq.core.result.ProbabilisticSubcircuit.CUTOFF_WARN = 1e-4
NUMBER_OF_SAMPLES = 10000
RESULTS_DIR_NAME = "results/jaqalpaq/point/ionsim/"

if not os.path.exists(RESULTS_DIR_NAME):
    os.makedirs(RESULTS_DIR_NAME)

for number_of_qubits, circuit_parameters in zip(
    [1, 2, 3],
    [M1_POINT_PARAMETER_VALUES, M2_POINT_PARAMETER_VALUES, M3_POINT_PARAMETER_VALUES],
):

    # Replace this noise model with interpygate noise model
    # backend = noisy.SNLToy1(number_of_qubits)
    # backend = None
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

    all_measurements = []
    for clique in cliques_to_measure:
        all_measurements.append(
            get_measurements_for_clique(
                clique,
                circuit_parameters,
                number_of_qubits,
                NUMBER_OF_SAMPLES,
                backend=backend,
            )
        )

    data_filename = RESULTS_DIR_NAME + "{}.txt".format(number_of_qubits)
    with open(data_filename, "w") as f:
        f.write(str(all_measurements))
    f.close()
