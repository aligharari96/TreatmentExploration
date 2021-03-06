import time

from Algorithms.Constraints.better_treatment_constraint import Constraint
from Algorithms.constrained_greedy import ConstrainedGreedy
from Algorithms.Approximators.statistical_approximator import StatisticalApproximator
from Algorithms.Constraints.true_constraint import TrueConstraint
from DataGenerator.data_generator import split_patients, generate_data, generate_test_data
from DataGenerator.distributions import DiscreteDistributionWithSmoothOutcomes


def setup_data_sets(n_z, n_x, n_a, n_y, n_training_samples, n_test_samples, seed):
    start = time.time()
    print("Generating training and test data")
    dist = DiscreteDistributionWithSmoothOutcomes(n_z, n_x, n_a, n_y, seed=seed)
    training_data = split_patients(generate_data(dist, n_training_samples))
    test_data = generate_test_data(dist, n_test_samples)
    print("Generating data took {:.3f} seconds".format(time.time() - start))
    return dist, training_data, test_data


def setup_algorithms(training_data, dist, delta):
    start = time.time()
    n_x = dist.n_x
    n_a = dist.n_a
    n_y = dist.n_y
    statistical_approximation_prior = StatisticalApproximator(n_x, n_a, n_y, training_data, smoothing_mode='gaussian')

    constraint_upper = Constraint(training_data, n_a, n_y, approximator=statistical_approximation_prior, delta=delta, bound='upper')
    constraint_lower = Constraint(training_data, n_a, n_y, approximator=statistical_approximation_prior, delta=delta, bound='lower')
    constraint_exact = TrueConstraint(dist, approximator=statistical_approximation_prior, delta=delta)

    algorithms = [
        #ConstrainedDynamicProgramming(n_x, n_a, n_y, training_data, constraint_upper, statistical_approximation_prior, name="Dynamic Programming Upper Bound", label="CDP_U"),
        #ConstrainedDynamicProgramming(n_x, n_a, n_y, training_data, constraint_lower, statistical_approximation_prior, name="Dynamic Programming Lower bound", label="CDP_L"),
        #ConstrainedDynamicProgramming(n_x, n_a, n_y, training_data, constraint_exact, statistical_approximation_prior, name="Dynamic Programming Exact Bound", label="CDP_E"),
        ConstrainedGreedy(n_x, n_a, n_y, training_data, constraint_upper, statistical_approximation_prior, name="Greedy Upper Bound", label="CG_U"),
        ConstrainedGreedy(n_x, n_a, n_y, training_data, constraint_lower, statistical_approximation_prior, name="Greedy Lower Bound", label="CG_L"),
        ConstrainedGreedy(n_x, n_a, n_y, training_data, constraint_exact, statistical_approximation_prior, name="Greedy Exact Bound", label="CG_E"),
    ]

    print("Setting up algorithms took {:.3f} seconds".format(time.time() - start))
    return algorithms


def load_settings():
    starting_seed = 90821
    n_data_sets = 10
    n_deltas = 40
    n_z = 2
    n_x = 1
    n_a = 5
    n_y = 3
    n_training_samples = 15000
    n_test_samples = 3000
    file_name_prefix = "GBounds_15ksamples_"

    return starting_seed, n_data_sets, n_deltas, n_z, n_x, n_a, n_y, n_training_samples, n_test_samples, file_name_prefix