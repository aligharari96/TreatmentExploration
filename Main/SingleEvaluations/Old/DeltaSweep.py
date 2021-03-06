from Algorithms.constrained_greedy import ConstrainedGreedy
from Algorithms.Approximators.function_approximation import FunctionApproximation
from Algorithms.constrained_dynamic_programming import ConstrainedDynamicProgramming
from Algorithms.Approximators.exact_approximator import ExactApproximator
from Algorithms.Constraints.true_constraint import TrueConstraint
from DataGenerator.data_generator import *
import time
from Algorithms.Constraints.better_treatment_constraint import Constraint
from Algorithms.Approximators.statistical_approximator import StatisticalApproximator

if __name__ == '__main__':
    # Training values
    seed = 10342

    n_z = 2
    n_x = 1
    n_a = 3
    n_y = 3
    n_training_samples = 1000
    n_test_samples = 1000
    epsilon = 0
    delta = 0.0
    # for grid search
    nr_deltas = 7
    n_algorithms = 3
    delta_limit = 1.0

    # Plot values
    treatment_slack = 0     # Eg, how close to max must we be to be considered "good enough"
    plot_colors = ['k', 'r', 'b', 'g', 'm', 'c', 'y']
    plot_markers = ['s', 'v', 'P', '1', '2', '3', '4']
    plot_lines = ['-', '--', ':', '-.']
    plot_delta_grid_search = True
    delta_grid_search_percentage = True
    main_start = time.time()

    values = np.zeros((n_algorithms, nr_deltas))
    values_var = np.zeros((n_algorithms, nr_deltas))
    times = np.zeros((n_algorithms, nr_deltas))
    times_var = np.zeros((n_algorithms, nr_deltas))
    deltas = np.linspace(0, delta_limit, nr_deltas)
    # Generate the data
    dist = DiscreteDistributionWithSmoothOutcomes(n_z, n_x, n_a, n_y, seed=seed, outcome_sensitivity_x_z=1)
    dist.print_moderator_statistics()
    dist.print_covariate_statistics()
    dist.print_treatment_statistics()
    dist.print_detailed_treatment_statistics()

    datasets = {'training': {'data': split_patients(generate_data(dist, n_training_samples))}, 'test': {'data': generate_test_data(dist, n_test_samples)}}

    split_training_data = datasets['training']['data']
    test_data = datasets['test']['data']
    print("Initializing statistical approximator")
    start = time.time()
    statistical_approximationPrior = StatisticalApproximator(n_x, n_a, n_y, split_training_data, smoothing_mode='gaussian')
    statistical_approximationNone = StatisticalApproximator(n_x, n_a, n_y, split_training_data, smoothing_mode='none')
    true_approximation = ExactApproximator(dist)
    function_approximation = FunctionApproximation(n_x, n_a, n_y, split_training_data)
    print("Initializing approximators took {:.3f} seconds".format(start - time.time()))

    print("Initializing Constraint")
    start = time.time()

    constraintNone = Constraint(split_training_data, n_a, n_y, approximator=statistical_approximationNone, delta=delta, epsilon=epsilon)
    constraintPrior = Constraint(split_training_data, n_a, n_y, approximator=statistical_approximationPrior, delta=delta, epsilon=epsilon)
    constraintFunc = Constraint(split_training_data, n_a, n_y, approximator=function_approximation, delta=delta, epsilon=epsilon)
    constraintATrue = Constraint(split_training_data, n_a, n_y, approximator=true_approximation, delta=delta, epsilon=epsilon)
    constraintTrue = TrueConstraint(dist, approximator=true_approximation, delta=delta, epsilon=epsilon)

    print("Initializing the constraint took {:.3f} seconds".format(time.time()-start))
    print("Initializing algorithms")
    algorithms = [
        #ConstrainedDynamicProgramming(n_x, n_a, n_y, split_training_data, constraintNone, statistical_approximationNone, name="Dynamic Programming Uniform Prior", label="CDP_U"),
        ConstrainedDynamicProgramming(n_x, n_a, n_y, split_training_data, constraintPrior, statistical_approximationPrior, name="Dynamic Programming Historical Prior", label="CDP_H"),
        #ConstrainedDynamicProgramming(n_x, n_a, n_y, split_training_data, constraintFunc, function_approximation, name="Dynamic Programming Function Approximation", label="CDP_F"),
        ConstrainedDynamicProgramming(n_x, n_a, n_y, split_training_data, constraintATrue, true_approximation, name="Dynamic Programming True", label="CDP_T"),
        #ConstrainedGreedy(n_x, n_a, n_y, split_training_data, constraintNone, statistical_approximationNone, name="Greedy Uniform Prior", label="CG_U"),
        ConstrainedGreedy(n_x, n_a, n_y, split_training_data, constraintPrior, statistical_approximationPrior, name="Greedy Historical Prior", label="CG_H"),
        #ConstrainedGreedy(n_x, n_a, n_y, split_training_data, constraintFunc, function_approximation, name="Greedy Function Approximation", label="CG_F"),
    ]

    assert len(algorithms) == n_algorithms

    time_name = 'time'
    outcome_name = 'outcome'
    evaluations_delta = {}
    for delta in deltas:
        for alg in algorithms:
            if alg.name not in evaluations_delta:
                evaluations_delta[alg.name] = {outcome_name: [], time_name: []}
            try:
                alg.constraint.delta = delta
                alg.constraint.better_treatment_constraint_dict = {}
            except AttributeError:
                pass
            print("Training {}".format(alg.name))
            alg.learn()
            total_outcome = 0
            total_time = 0
            print("Evaluating {} with delta = {}".format(alg.name, delta))
            for i in range(n_test_samples):
                interventions = alg.evaluate(test_data[i])
                search_time = len(interventions)
                best_outcome = max([treatment[1] for treatment in interventions])
                if delta_grid_search_percentage:
                    if best_outcome == np.max(test_data[i][2]):
                        total_outcome += 1
                else:
                    total_outcome += best_outcome
                total_time += search_time
            mean_outcome = total_outcome/n_test_samples
            mean_time = total_time/n_test_samples
            evaluations_delta[alg.name][outcome_name].append(mean_outcome)
            evaluations_delta[alg.name][time_name].append(mean_time)
    print("Running Evaluate (and training) over delta took {:.3f} seconds".format(time.time() - main_start))

    # Plot mean treatment effect vs delta
    fig, ax1 = plt.subplots(figsize=(10, 7))
    plt.title('Mean treatment effect/mean search time vs delta')
    plt.xlabel('delta')
    ax2 = ax1.twinx()
    ax1.set_ylabel('Mean treatment effect')
    ax2.set_ylabel('Mean search time')
    lns = []
    for i_plot, alg in enumerate(algorithms):
        ln1 = ax1.plot(deltas, evaluations_delta[alg.name][outcome_name], plot_colors[i_plot],
                       label='{} {}'.format(alg.label, 'effect'))
        ln2 = ax2.plot(deltas, evaluations_delta[alg.name][time_name], plot_colors[i_plot] + plot_lines[1],
                       label='{} {}'.format(alg.label, 'time'))
        lns.append(ln1)
        lns.append(ln2)
    plt.grid(True)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    plt.legend(lines1 + lines2, labels1 + labels2, bbox_to_anchor=(1.04, 0), loc='upper left')
    plt.show(block=False)

    plt.show()