from Algorithms.Approximators.function_approximation import FunctionApproximation
from Algorithms.naive_dynamic_programming import NaiveDynamicProgramming
from Algorithms.constrained_dynamic_programming import ConstrainedDynamicProgramming
from Algorithms.constrained_greedy import ConstrainedGreedy
from Algorithms.Constraints.true_constraint import TrueConstraint
from DataGenerator.data_generator import *
import time
from Algorithms.Constraints.better_treatment_constraint import Constraint
from Algorithms.Approximators.statistical_approximator import StatisticalApproximator
from Database.antibioticsdatabase import AntibioticsDatabase
from Algorithms.doctor import Doctor
from Algorithms.emulated_doctor import EmulatedDoctor
from Algorithms.Approximators.doctor_approximator import DoctorApproximator


def setup_data_sets(seed):
    start = time.time()
    print("Generating training and test data")
    dist = AntibioticsDatabase(n_x=n_x, antibiotic_limit=50, seed=seed)
    training_data, test_data = dist.get_data()
    training_data = split_patients(training_data)

    print("Generating data took {:.3f} seconds".format(time.time() - start))
    return dist, training_data, test_data


def setup_algorithms(dist, training_data, n_x, n_a, n_y, delta):
    start = time.time()
    statistical_approximation = StatisticalApproximator(n_x, n_a, n_y, training_data, smoothing_mode='gaussian')
    function_approximation = FunctionApproximation(n_x, n_a, n_y, training_data)
    doctor_approximation = DoctorApproximator(n_x, n_a, n_y, training_data)

    print("Initializing Constraint")
    start = time.time()

    constraintStatUpper = Constraint(training_data, n_a, n_y, approximator=statistical_approximation, delta=delta, bound='upper')
    constraintFuncApprox = Constraint(training_data, n_a, n_y, approximator=function_approximation, delta=delta)
    constraint_exact_func = TrueConstraint(dist, approximator=function_approximation, delta=delta)

    print("Initializing the constraint took {:.3f} seconds".format(time.time() - start))
    print("Initializing algorithms")
    algorithms = [
        #ConstrainedGreedy(n_x, n_a, n_y, training_data, constraintStatUpper, statistical_approximation,
        #                  name='Constrained Greedy', label='CG'),
        # ConstrainedGreedy(n_x, n_a, n_y, split_training_data, constraintStatLower, statistical_approximation,
        #                   name='Constrained Greedy Lower', label='CG_L'),
        ConstrainedGreedy(n_x, n_a, n_y, training_data, constraintFuncApprox, function_approximation,
                         name="Constrained Greedy FuncApprox", label="CG_F"),
        #ConstrainedDynamicProgramming(n_x, n_a, n_y, training_data, constraintStatUpper,
        #                              statistical_approximation),
        ConstrainedDynamicProgramming(n_x, n_a, n_y, training_data, constraintFuncApprox,
                                      function_approximation, name="Constrained Dynamic Programming FuncApprox", label="CDP_F"),

        #NaiveGreedy(n_x, n_a, n_y, function_approximation, max_steps=n_a),
        #NaiveGreedy(n_x, n_a, n_y, function_approximation, max_steps=n_a),
        NaiveDynamicProgramming(n_x, n_a, n_y, training_data, constraintStatUpper, reward=-0.35),
        Doctor(),
        EmulatedDoctor(n_x, n_a, n_y, training_data, approximator=doctor_approximation)
    ]
    return algorithms


def load_settings():
    starting_seed = 10342  # Used for both synthetic and real data
    delta = 0.0
    n_data_sets = 4
    file_name_prefix = 'antibioticsFAdelta0'
    return starting_seed, n_data_sets, delta, file_name_prefix


n_x = 6

