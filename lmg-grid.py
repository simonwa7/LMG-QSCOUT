from parameters import M1_GRID_PARAMETERS, M2_GRID_PARAMETERS, M3_GRID_PARAMETERS
from measurement import (
    create_clique1_circuit,
    create_clique2_circuit,
    create_clique3_circuit,
    create_clique4_circuit,
    get_measurements_for_clique,
)


NUMBER_OF_QUBITS = 1
NUMBER_OF_SAMPLES = 2 ** 13
PARAMETERS_MAP = {1: M1_GRID_PARAMETERS, 2: M2_GRID_PARAMETERS, 3: M3_GRID_PARAMETERS}
RESULTS_DIR_NAME = "results/jaqalpaq/grid/ionsim/{}/".format(NUMBER_OF_QUBITS)

import os

if not os.path.exists(RESULTS_DIR_NAME):
    os.makedirs(RESULTS_DIR_NAME)

import jaqalpaq

from qscout.v1.std.ionsim import IonSimErrorModel

import jaqalpaq.core.result

jaqalpaq.core.result.ProbabilisticSubcircuit.CUTOFF_FAIL = 1e-4
jaqalpaq.core.result.ProbabilisticSubcircuit.CUTOFF_WARN = 1e-4

# backend=None
# backend = noisy.SNLToy1(NUMBER_OF_QUBITS)
backend = IonSimErrorModel(
    NUMBER_OF_QUBITS,
    model="standard",
    params=["dpower12", "dfreq1", "dphase1", "dtime"],
    v0={"dpower12": 5e-4, "dfreq1": 5e3, "dphase1": 5e-2, "dtime": 5e-3},
    sigmas={"dpower12": 5e-4, "dfreq1": 5e3, "dphase1": 5e-2, "dtime": 5e-3},
)


for i, circuit_parameters in enumerate(PARAMETERS_MAP[NUMBER_OF_QUBITS]):
    cliques_to_measure = [create_clique1_circuit, create_clique2_circuit]
    if NUMBER_OF_QUBITS > 1:
        cliques_to_measure.append(create_clique3_circuit)
    if NUMBER_OF_QUBITS > 2:
        cliques_to_measure.append(create_clique4_circuit)

    all_measurements = []
    for clique in cliques_to_measure:
        all_measurements.append(
            get_measurements_for_clique(
                clique,
                circuit_parameters,
                NUMBER_OF_QUBITS,
                NUMBER_OF_SAMPLES,
                backend=backend,
            )
        )

    data_filename = RESULTS_DIR_NAME + "{}.txt".format(i + 1)
    with open(data_filename, "w") as f:
        f.write(str(all_measurements))
    f.close()
