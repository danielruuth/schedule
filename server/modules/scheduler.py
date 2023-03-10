#!/usr/bin/env python3
# Copyright 2010-2022 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Creates a shift scheduling problem and solves it."""

from absl import app
from absl import flags

import json

from ortools.sat.python import cp_model
from google.protobuf import text_format

class Scheduler:
    def __init__(self, params):
        self._params = params
        
        
    def negated_bounded_span(works, start, length):
        sequence = []
        # Left border (start of works, or works[start - 1])
        if start > 0:
            sequence.append(works[start - 1])
        for i in range(length):
            sequence.append(works[start + i].Not())
        # Right border (end of works or works[start + length])
        if start + length < len(works):
            sequence.append(works[start + length])
        return sequence


    def add_soft_sequence_constraint(self, model, works, hard_min, soft_min, min_cost,
                                     soft_max, hard_max, max_cost, prefix):
        cost_literals = []
        cost_coefficients = []

        # Forbid sequences that are too short.
        for length in range(1, hard_min):
            for start in range(len(works) - length + 1):
                model.AddBoolOr(negated_bounded_span(works, start, length))

        # Penalize sequences that are below the soft limit.
        if min_cost > 0:
            for length in range(hard_min, soft_min):
                for start in range(len(works) - length + 1):
                    span = negated_bounded_span(works, start, length)
                    name = ': under_span(start=%i, length=%i)' % (start, length)
                    lit = model.NewBoolVar(prefix + name)
                    span.append(lit)
                    model.AddBoolOr(span)
                    cost_literals.append(lit)
                    # We filter exactly the sequence with a short length.
                    # The penalty is proportional to the delta with soft_min.
                    cost_coefficients.append(min_cost * (soft_min - length))

        # Penalize sequences that are above the soft limit.
        if max_cost > 0:
            for length in range(soft_max + 1, hard_max + 1):
                for start in range(len(works) - length + 1):
                    span = negated_bounded_span(works, start, length)
                    name = ': over_span(start=%i, length=%i)' % (start, length)
                    lit = model.NewBoolVar(prefix + name)
                    span.append(lit)
                    model.AddBoolOr(span)
                    cost_literals.append(lit)
                    # Cost paid is max_cost * excess length.
                    cost_coefficients.append(max_cost * (length - soft_max))

        # Just forbid any sequence of true variables with length hard_max + 1
        for start in range(len(works) - hard_max):
            model.AddBoolOr(
                [works[i].Not() for i in range(start, start + hard_max + 1)])
        return cost_literals, cost_coefficients


    def add_soft_sum_constraint(self, model, works, hard_min, soft_min, min_cost,
                                soft_max, hard_max, max_cost, prefix):

        cost_variables = []
        cost_coefficients = []
        sum_var = model.NewIntVar(hard_min, hard_max, '')
        # This adds the hard constraints on the sum.
        model.Add(sum_var == sum(works))

        # Penalize sums below the soft_min target.
        if soft_min > hard_min and min_cost > 0:
            delta = model.NewIntVar(-len(works), len(works), '')
            model.Add(delta == soft_min - sum_var)
            # TODO(user): Compare efficiency with only excess >= soft_min - sum_var.
            excess = model.NewIntVar(0, 7, prefix + ': under_sum')
            model.AddMaxEquality(excess, [delta, 0])
            cost_variables.append(excess)
            cost_coefficients.append(min_cost)

        # Penalize sums above the soft_max target.
        if soft_max < hard_max and max_cost > 0:
            delta = model.NewIntVar(-7, 7, '')
            model.Add(delta == sum_var - soft_max)
            excess = model.NewIntVar(0, 7, prefix + ': over_sum')
            model.AddMaxEquality(excess, [delta, 0])
            cost_variables.append(excess)
            cost_coefficients.append(max_cost)

        return cost_variables, cost_coefficients

    def solve(self):
        """Solves the shift scheduling problem."""
        # Data
        num_employees = len(self._params['resources']) #8
        num_weeks = self._params['weeks'] #3
        shifts = self._params['shifts'] #['O', 'A', 'C'] # Off, day, night

        # Fixed assignment: (employee, shift, day).
        # This fixes the first 2 days of the schedule.
        # This should come from params
        fixed_assignments = self._params['fixed_assignments']

        # Request: (employee, shift, day, weight)
        # A negative weight indicates that the employee desire this assignment.
        requests = self._params['requests']

        # Shift constraints on continuous sequence :
        #     (shift, hard_min, soft_min, min_penalty,
        #             soft_max, hard_max, max_penalty)
        shift_constraints = self._params['shift_constraints']

        # Weekly sum constraints on shifts days:
        #     (shift, hard_min, soft_min, min_penalty,
        #             soft_max, hard_max, max_penalty)
        weekly_sum_constraints = [
            # Constraints on rests per week.
            (0, 1, 2, 7, 2, 3, 4),
            # At least 1 evening shift per week (penalized). At most 4 (hard).
            (2, 0, 1, 3, 4, 4, 0),
        ]

        # Penalized transitions:
        #     (previous_shift, next_shift, penalty (0 means forbidden))
        penalized_transitions = [
            # Night to morning has a penalty of 4.
            (2, 1, 4),
        ]

        # daily demands for work shifts (day, night) for each day
        # of the week starting on Monday.
        weekly_cover_demands = self._params['cover_demands']

        # Penalty for exceeding the cover constraint per shift type.
        excess_cover_penalties = (2, 2, 5)

        num_days = num_weeks * 7
        num_shifts = len(shifts)

        model = cp_model.CpModel()

        work = {}
        for e in range(num_employees):
            for s in range(num_shifts):
                for d in range(num_days):
                    work[e, s, d] = model.NewBoolVar('work%i_%i_%i' % (e, s, d))

        # Linear terms of the objective in a minimization context.
        obj_int_vars = []
        obj_int_coeffs = []
        obj_bool_vars = []
        obj_bool_coeffs = []

        # Exactly one shift per day.
        for e in range(num_employees):
            for d in range(num_days):
                model.AddExactlyOne(work[e, s, d] for s in range(num_shifts))

        # Fixed assignments.
        for e, s, d in fixed_assignments:
            model.Add(work[e, s, d] == 1)

        # Employee requests
        for e, s, d, w in requests:
            obj_bool_vars.append(work[e, s, d])
            obj_bool_coeffs.append(w)

        # Shift constraints
        for ct in shift_constraints:
            shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
            for e in range(num_employees):
                works = [work[e, shift, d] for d in range(num_days)]
                variables, coeffs = self.add_soft_sequence_constraint(
                    model, works, hard_min, soft_min, min_cost, soft_max, hard_max,
                    max_cost,
                    'shift_constraint(employee %i, shift %i)' % (e, shift))
                obj_bool_vars.extend(variables)
                obj_bool_coeffs.extend(coeffs)

        # Weekly sum constraints
        for ct in weekly_sum_constraints:
            shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
            for e in range(num_employees):
                for w in range(num_weeks):
                    works = [work[e, shift, d + w * 7] for d in range(7)]
                    variables, coeffs = self.add_soft_sum_constraint(
                        model, works, hard_min, soft_min, min_cost, soft_max,
                        hard_max, max_cost,
                        'weekly_sum_constraint(employee %i, shift %i, week %i)' %
                        (e, shift, w))
                    obj_int_vars.extend(variables)
                    obj_int_coeffs.extend(coeffs)

        # Penalized transitions
        for previous_shift, next_shift, cost in penalized_transitions:
            for e in range(num_employees):
                for d in range(num_days - 1):
                    transition = [
                        work[e, previous_shift, d].Not(), work[e, next_shift,
                                                               d + 1].Not()
                    ]
                    if cost == 0:
                        model.AddBoolOr(transition)
                    else:
                        trans_var = model.NewBoolVar(
                            'transition (employee=%i, day=%i)' % (e, d))
                        transition.append(trans_var)
                        model.AddBoolOr(transition)
                        obj_bool_vars.append(trans_var)
                        obj_bool_coeffs.append(cost)

        # Cover constraints
        for s in range(1, num_shifts):
            for w in range(num_weeks):
                for d in range(7):
                    works = [work[e, s, w * 7 + d] for e in range(num_employees)]
                    # Ignore Off shift.
                    min_demand = weekly_cover_demands[d][s - 1]
                    worked = model.NewIntVar(min_demand, num_employees, '')
                    model.Add(worked == sum(works))
                    over_penalty = excess_cover_penalties[s - 1]
                    if over_penalty > 0:
                        name = 'excess_demand(shift=%i, week=%i, day=%i)' % (s, w,
                                                                             d)
                        excess = model.NewIntVar(0, num_employees - min_demand,
                                                 name)
                        model.Add(excess == worked - min_demand)
                        obj_int_vars.append(excess)
                        obj_int_coeffs.append(over_penalty)

        # Objective
        model.Minimize(
            sum(obj_bool_vars[i] * obj_bool_coeffs[i]
                for i in range(len(obj_bool_vars))) +
            sum(obj_int_vars[i] * obj_int_coeffs[i]
                for i in range(len(obj_int_vars))))

        # Solve the model.
        solver = cp_model.CpSolver()
        solution_printer = cp_model.ObjectiveSolutionPrinter()
        status = solver.Solve(model, solution_printer)

        # Print solution.
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print()
            header = '          '
            for w in range(num_weeks):
                header += 'M T W T F S S '
            print(header)
            for e in range(num_employees):
                schedule = ''
                for d in range(num_days):
                    for s in range(num_shifts):
                        if solver.BooleanValue(work[e, s, d]):
                            schedule += shifts[s] + ' '
                print('worker %i: %s' % (e, schedule))
            print()
            print('Penalties:')
            for i, var in enumerate(obj_bool_vars):
                if solver.BooleanValue(var):
                    penalty = obj_bool_coeffs[i]
                    if penalty > 0:
                        print('  %s violated, penalty=%i' % (var.Name(), penalty))
                    else:
                        print('  %s fulfilled, gain=%i' % (var.Name(), -penalty))

            for i, var in enumerate(obj_int_vars):
                if solver.Value(var) > 0:
                    print('  %s violated by %i, linear penalty=%i' %
                          (var.Name(), solver.Value(var), obj_int_coeffs[i]))

        print()
        print('Statistics')
        print('  - status          : %s' % solver.StatusName(status))
        print('  - conflicts       : %i' % solver.NumConflicts())
        print('  - branches        : %i' % solver.NumBranches())
        print('  - wall time       : %f s' % solver.WallTime())
        # Statistics.
        # return json.dumps(
        #  {
        #    "conflicts":solver.NumConflicts(),
        #    "branches": solver.NumBranches(),
        #    "wall_time": solver.WallTime(),
        #    "status": solver.StatusName(status),
        #    "result": solution_printer.solutions()
        #  }
        # )


def main(_):
    params = {
        'resources': ['Jim', 'Pam', 'Dwight', 'Stan', 'Creed', 'Andy', 'Michael', 'Phyllis'],
        'shifts': ['O', 'A', 'C'], # Off, day, night
        'weeks': 3,
        'fixed_assignments': [
            (0, 0, 0),
            (1, 0, 0),
            (2, 1, 0),
            (3, 1, 0),
            (4, 2, 0),
            (5, 2, 0),
            (6, 2, 3),
            (0, 1, 1),
            (1, 1, 1),
            (2, 2, 1),
            (3, 2, 1),
            (4, 2, 1),
            (5, 0, 1),
            (6, 0, 1),
        ],
        'requests': [
            # Employee 3 does not want to work on the first Saturday (negative weight
            # for the Off shift).
            (3, 0, 5, -2),
            # Employee 5 wants a night shift on the second Thursday (negative weight).
            (5, 2, 10, -2),
            # Employee 2 does not want a night shift on the first Friday (positive
            # weight).
            (2, 2, 4, 4)
        ],
        'shift_constraints':  [
            # One or two consecutive days of rest, this is a hard constraint.
            (0, 1, 1, 0, 2, 2, 0)
        ],
        
        'cover_demands': [
            (3, 3),  # Monday
            (3, 3),  # Tuesday
            (3, 3),  # Wednesday
            (3, 3),  # Thursday
            (3, 3),  # Friday
            (2, 2),  # Saturday
            (2, 2),  # Sunday
        ]
        
    }
    
        
    s = Scheduler(params)
    s.solve()


if __name__ == '__main__':
    app.run(main)
    

