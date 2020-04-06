import numpy as np
from Algorithms.betterTreatmentConstraint import Constraint
from Algorithms.help_functions import *


class GreedyShuffled2:
    def __init__(self, n_x, n_a, n_y, data, constraint):
        self.n_x = n_x
        self.n_a = n_a
        self.n_y = n_y
        self.data = data
        self.probabilities = None
        self.name = 'Constrained Greedy'
        self.label = 'CG'
        self.constraint = constraint

    def learn(self):
        histories = self.data['h']
        covariates = self.data['x']

        patient_statistics = np.zeros(((2,) * self.n_x + (self.n_y + 1,) * self.n_a + (self.n_a,) + (self.n_y,)), dtype=int)
        for i in range(len(covariates)):
            history = histories[i]
            covariate = covariates[i]
            treatment, outcome = history[-1]
            history = history[:-1]
            index = np.hstack((covariate, np.ones(self.n_a, dtype=int) * -1))
            new = np.zeros((self.n_a, self.n_y), dtype=int)
            for h in history:
                index[h[0] + self.n_x] = h[1]
            new[treatment, outcome] = 1
            ind = tuple(index)
            patient_statistics[ind] += new
        self.probabilities = patient_statistics

        return patient_statistics

    def evaluate(self, patient):
        best_outcome = 0
        x = patient[1]
        y_fac = patient[2]
        y = np.array([-1] * self.n_a)
        stop = False
        history = []
        while not stop:
            state = np.array([x, y])
            prob_matrix = self.probabilities[tuple(np.hstack(state))]

            tot = np.sum(prob_matrix, axis=1)
            tot[tot == 0] = 1
            ev_vec = np.zeros(self.n_a)
            for i in range(best_outcome+1, self.n_y):
                ev_vec += prob_matrix[:, i] * i

            ev_vec = np.divide(ev_vec, tot)
            hstate = history_to_state(history, self.n_a)
            for i, hs in enumerate(hstate):
                if hs != -1:
                    ev_vec[i] = -np.inf
            mask_unknown_actions = y_fac.copy().astype(float)
            mask_unknown_actions[mask_unknown_actions != -1] = 0
            mask_unknown_actions[mask_unknown_actions == -1] = -np.inf
            decision_probabilities = ev_vec+mask_unknown_actions
            new_treatment = np.argmax(decision_probabilities)
            if np.max(decision_probabilities) == -np.inf:
                break
            outcome = int(y_fac[new_treatment])
            if outcome > best_outcome:
                best_outcome = outcome
            y[new_treatment] = outcome
            history.append([new_treatment, outcome])
            no_better_treatment_exist = self.constraint.no_better_treatment_exist(history_to_state(history, self.n_a), x)
            if no_better_treatment_exist == 1:
                stop = True
        return history

    def set_constraint(self, constraint):
        self.constraint = constraint
