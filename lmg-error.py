from parameters import M1_POINT_PARAMETER_VALUES, M2_POINT_PARAMETER_VALUES, M3_POINT_PARAMETER_VALUES
from measurement import (
    create_clique1_circuit,
    create_clique2_circuit,
    create_clique3_circuit,
    create_clique4_circuit,
    get_measurements_for_clique,
)


NUMBER_OF_QUBITS = 3
NUMBER_OF_SAMPLES = (
    2 ** 8
)  # With this many shots, you can see the effect of the noise model. With 2**10 shots,
# effects of noise are almost negligible for 3 qubits
PARAMETERS_MAP = {1: M1_POINT_PARAMETER_VALUES, 2: M2_POINT_PARAMETER_VALUES, 3: M3_POINT_PARAMETER_VALUES}
RESULTS_DIR_NAME = "results/jaqalpaq/point/{}/".format(NUMBER_OF_QUBITS)

import os
if not os.path.exists(RESULTS_DIR_NAME):
    os.makedirs(RESULTS_DIR_NAME)

from qscout.v1 import noisy
# Replace this noise model with interpygate noise model
backend = noisy.SNLToy1(NUMBER_OF_QUBITS)
# backend=None


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
            PARAMETERS_MAP[NUMBER_OF_QUBITS],
            NUMBER_OF_QUBITS,
            NUMBER_OF_SAMPLES,
            backend=backend,
        )
    )

data_filename = RESULTS_DIR_NAME + "single_point_eval.txt"
with open(data_filename, "w") as f:
    f.write(str(all_measurements))
f.close()
