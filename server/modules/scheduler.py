#!/usr/bin/env python3
from absl import app
from absl import flags

import json
import logging
from ortools.sat.python import cp_model
from google.protobuf import text_format

class Scheduler(cp_model.CpSolverSolutionCallback):
    def __init__(self, params):
        self._params = params
        self._solution_count = 0
        self._solution_limit = params["limit"]

        cp_model.CpSolverSolutionCallback.__init__(self)
         
    def negated_bounded_span(self, works, start, length):
        """Filters an isolated sub-sequence of variables assined to True.
        Extract the span of Boolean variables [start, start + length), negate them,
        and if there is variables to the left/right of this span, surround the span by
        them in non negated form.
        Args:
            works: a list of variables to extract the span from.
            start: the start to the span.
            length: the length of the span.
        Returns:
            a list of variables which conjunction will be false if the sub-list is
            assigned to True, and correctly bounded by variables assigned to False,
            or by the start or end of works.
        """   
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


    def add_soft_sequence_constraint(self, model, works, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost, prefix):
        """Sequence constraint on true variables with soft and hard bounds.
        This constraint look at every maximal contiguous sequence of variables
        assigned to true. If forbids sequence of length < hard_min or > hard_max.
        Then it creates penalty terms if the length is < soft_min or > soft_max.
        Args:
            model: the sequence constraint is built on this model.
            works: a list of Boolean variables.
            hard_min: any sequence of true variables must have a length of at least
            hard_min.
            soft_min: any sequence should have a length of at least soft_min, or a
            linear penalty on the delta will be added to the objective.
            min_cost: the coefficient of the linear penalty if the length is less than
            soft_min.
            soft_max: any sequence should have a length of at most soft_max, or a linear
            penalty on the delta will be added to the objective.
            hard_max: any sequence of true variables must have a length of at most
            hard_max.
            max_cost: the coefficient of the linear penalty if the length is more than
            soft_max.
            prefix: a base name for penalty literals.
        Returns:
            a tuple (variables_list, coefficient_list) containing the different
            penalties created by the sequence constraint.
        """
        cost_literals = []
        cost_coefficients = []

        # Forbid sequences that are too short.
        for length in range(1, hard_min):
            for start in range(len(works) - length + 1):
                model.AddBoolOr(self.negated_bounded_span(works, start, length))

        # Penalize sequences that are below the soft limit.
        if min_cost > 0:
            for length in range(hard_min, soft_min):
                for start in range(len(works) - length + 1):
                    span = self.negated_bounded_span(works, start, length)
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
                    span = self.negated_bounded_span(works, start, length)
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


    def add_soft_sum_constraint(self, model, works, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost, prefix):
        """Sum constraint with soft and hard bounds.
        This constraint counts the variables assigned to true from works.
        If forbids sum < hard_min or > hard_max.
        Then it creates penalty terms if the sum is < soft_min or > soft_max.
        Args:
            model: the sequence constraint is built on this model.
            works: a list of Boolean variables.
            hard_min: any sequence of true variables must have a sum of at least
            hard_min.
            soft_min: any sequence should have a sum of at least soft_min, or a linear
            penalty on the delta will be added to the objective.
            min_cost: the coefficient of the linear penalty if the sum is less than
            soft_min.
            soft_max: any sequence should have a sum of at most soft_max, or a linear
            penalty on the delta will be added to the objective.
            hard_max: any sequence of true variables must have a sum of at most
            hard_max.
            max_cost: the coefficient of the linear penalty if the sum is more than
            soft_max.
            prefix: a base name for penalty variables.
        Returns:
            a tuple (variables_list, coefficient_list) containing the different
            penalties created by the sequence constraint.
        """
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
    def on_solution_callback(self):
        self._solution_count += 1
        print('Found %i solutions' % self._solution_count)
        if self._solution_count >= self._solution_limit:
            print('Stop search after %i solutions' % self._solution_limit)
            self.StopSearch()
    
    def solution_count(self):
        return self._solution_count

    def solve(self):
        """Solves the shift scheduling problem."""
        # Data
        num_employees = len(self._params['resources']) #8
        num_weeks = self._params['weeks'] #3
        shifts = self._params['shifts'] #['O', 'A', 'C'] # Off, day, night

        # Fixed assignment: (employee, shift, day).
        fixed_assignments = self._params['fixed_assignments']

        # Request: (employee, shift, day, weight)
        # A negative weight indicates that the employee desire this assignment.
         # Employee 3 does not want to work on the first Saturday (negative weight
        # for the Off shift).
        # (3, 0, 5, -2),
        # Employee 5 wants a night shift on the second Thursday (negative weight).
        # (5, 3, 10, -2),
        # Employee 2 does not want a night shift on the first Friday (positive
        # weight).
        # (2, 3, 4, 4)
        requests = self._params['requests']

        # Shift constraints on continuous sequence :
        #     (shift, hard_min, soft_min, min_penalty,
        #             soft_max, hard_max, max_penalty)
        # One or two consecutive days of rest, this is a hard constraint.
        # (0, 1, 1, 0, 2, 2, 0),
        # between 2 and 3 consecutive days of night shifts, 1 and 4 are
        # possible but penalized.
        # (3, 1, 2, 20, 3, 4, 5),
        shift_constraints = self._params['shift_constraints']

        # Weekly sum constraints on shifts days:
        #     (shift, hard_min, soft_min, min_penalty,
        #             soft_max, hard_max, max_penalty)
        # Constraints on rests per week.
        #(0, 1, 2, 7, 2, 3, 4),
        # At least 1 night shift per week (penalized). At most 4 (hard).
        # (3, 0, 1, 3, 4, 4, 0),
        weekly_sum_constraints = self._params['weekly_sum_constraints']

        # Penalized transitions:
        #     (previous_shift, next_shift, penalty (0 means forbidden))
        # Afternoon to night has a penalty of 4.
        #(2, 3, 4),
        # Night to morning is forbidden.
        #(3, 1, 0),
        penalized_transitions = self._params['penalized_transitions']

        # daily demands for work shifts (day, night) for each day
        # of the week starting on Monday.
        weekly_cover_demands = self._params['cover_demands']

        # Penalty for exceeding the cover constraint per shift type.
        excess_cover_penalties = self._params['excess_cover_penalties'] #(2, 2, 5, 5) #Denna måste representera per shift


        #Weekend shift constraints
        max_weekend_shifts = self._params['max_weekend_shifts']

        num_days = num_weeks * 7
        num_shifts = len(shifts)


        model = cp_model.CpModel()

        work = {}
        for e in range(num_employees):
            for s in range(num_shifts):
                for d in range(num_days):
                    work[e, s, d, d % 7] = model.NewBoolVar('work%i_%i_%i_%i' % (e, s, d, d % 7))
       
        # Linear terms of the objective in a minimization context.
        obj_int_vars = []
        obj_int_coeffs = []
        obj_bool_vars = []
        obj_bool_coeffs = []

        # Exactly one shift per day.
        for e in range(num_employees):
            for d in range(num_days):
                model.AddExactlyOne(work[e, s, d, d % 7] for s in range(num_shifts))


        # Weekend shift constraints to make sure we only work x shifts per scheduling period
        for e in range(num_employees):
            num_weekend_shifts = sum(work[e, s, d, d % 7] for s in range(num_shifts) for d in range(num_days) if d % 7 == 5 or d % 7 == 6)
            model.Add(num_weekend_shifts <= max_weekend_shifts)

        # Fixed assignments.
        for e, s, d in fixed_assignments:
            model.Add(work[e, s, d, d % 7] == 1)

        # Employee requests
        for e, s, d, w in requests:
            obj_bool_vars.append(work[e, s, d, d % 7])
            obj_bool_coeffs.append(w)

        # Shift constraints
        for ct in shift_constraints:
            shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
            for e in range(num_employees):
                works = [work[e, shift, d, d % 7] for d in range(num_days)]
                variables, coeffs = self.add_soft_sequence_constraint(
                    model, works, hard_min, soft_min, min_cost, soft_max, hard_max,
                    max_cost,
                    'shift_constraint(employee=%i, shift=%i)' % (e, shift))
                obj_bool_vars.extend(variables)
                obj_bool_coeffs.extend(coeffs)

        # Weekly sum constraints
        for ct in weekly_sum_constraints:
            shift, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
            for e in range(num_employees):
                for w in range(num_weeks):
                    works = [work[e, shift, d + w * 7, d % 7] for d in range(7)]
                    variables, coeffs = self.add_soft_sum_constraint(
                        model, works, hard_min, soft_min, min_cost, soft_max,
                        hard_max, max_cost,
                        'weekly_sum_constraint(employee=%i, shift=%i, week=%i)' %
                        (e, shift, w))
                    obj_int_vars.extend(variables)
                    obj_int_coeffs.extend(coeffs)
        # Day sum constraints
        # Day, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost
        """day_sum_constraints = [
            (5, 1, 2, 3, 2, 2, 6),
            (6, 1, 2, 3, 2, 2, 6)
        ]
        # Day sum constraints
        for ct in day_sum_constraints:
            day, hard_min, soft_min, min_cost, soft_max, hard_max, max_cost = ct
            for e in range(num_employees):
                for d in range(num_days):
                    if d % 7 == day:
                        works = [work[e, s, d, day] for s in range(num_shifts)]
                        variables, coeffs = self.add_soft_sum_constraint(
                            model, works, hard_min, soft_min, min_cost, soft_max,
                            hard_max, max_cost,
                            'day_sum_constraint(employee=%i, day=%i)' %
                            (e, day))
                        obj_int_vars.extend(variables)
                        obj_int_coeffs.extend(coeffs)"""

        ##
        # Penalized transitions
        for previous_shift, next_shift, cost in penalized_transitions:
            for e in range(num_employees):
                for d in range(num_days - 1):
                    transition = [
                        work[e, previous_shift, d, d % 7].Not(), work[e, next_shift,
                                                               d + 1, (d + 1) % 7].Not()
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
                    works = [work[e, s, w * 7 + d, d % 7] for e in range(num_employees)]
                    # Ignore Off shift.
                    min_demand = weekly_cover_demands[d][s - 1]
                    worked = model.NewIntVar(min_demand, num_employees, '')
                    model.Add(worked == sum(works))
                    over_penalty = excess_cover_penalties[s - 1][d]
                    if over_penalty > 0:
                        name = 'excess_demand(shift=%i, week=%i, day=%i)' % (s, w,
                                                                             d)
                        excess = model.NewIntVar(0, num_employees - min_demand,
                                                 name)
                        model.Add(excess == worked - min_demand)
                        obj_int_vars.append(excess)
                        obj_int_coeffs.append(over_penalty)
                    else:
                        # If penalty is 0, forbid excess cover completely
                        model.Add(worked <= min_demand)

        # Objective
        model.Minimize(
            sum(obj_bool_vars[i] * obj_bool_coeffs[i]
                for i in range(len(obj_bool_vars))) +
            sum(obj_int_vars[i] * obj_int_coeffs[i]
                for i in range(len(obj_int_vars))))

        
        # Solve the model.
        solver = cp_model.CpSolver()
        #solver.parameters.enumerate_all_solutions = True
        solution_printer = cp_model.ObjectiveSolutionPrinter()
        status = solver.Solve(model, self)
        
        
        # Print solution.
        retval_shifts = []
        for e in range(num_employees):
            retval_shifts.append({'name':self._params['resources'][e], 'shifts':[]})
        retval_penalties = []

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for e in range(num_employees):
                schedule = ''
                for d in range(num_days):
                    for s in range(num_shifts):
                        if solver.BooleanValue(work[e, s, d, d % 7]):
                            schedule += shifts[s] + ' '
                            retval_shifts[e]['shifts'].append(shifts[s])
                
            for i, var in enumerate(obj_bool_vars):
                if solver.BooleanValue(var):
                    penalty = obj_bool_coeffs[i]
                    if penalty > 0:
                        #retval_penalties.append('%s violated, penalty=%i' % (var.Name(), penalty))
                        retval_penalties.append({
                            "name": var.Name(),
                            "penalty": penalty,
                            "solver": False
                        })
                    else:
                        #retval_penalties.append('%s fulfilled, gain=%i' % (var.Name(), -penalty)) #
                        retval_penalties.append({
                            "name": var.Name(),
                            "penalty": -penalty,
                            "solver": False
                        })

            for i, var in enumerate(obj_int_vars):
                if solver.Value(var) > 0:
                    #retval_penalties.append('%s violated by %i, linear penalty=%i' %
                    #      (var.Name(), solver.Value(var), obj_int_coeffs[i])
                    retval_penalties.append({
                        "name": var.Name(),
                        "penalty": obj_int_coeffs[i],
                        "solver": solver.Value(var)
                    })

            # Statistics.
            return json.dumps(
            {
                "status":solver.StatusName(status),
                "conflicts": solver.NumConflicts(),
                "branches": solver.NumBranches(),
                "wall_time": solver.WallTime(),
                "result": {"shifts": retval_shifts, "penalties": retval_penalties}
            }
            )
        else:
            if status == cp_model.INFEASIBLE:
                print('Model is infeasible')
            return json.dumps({
                "result":[],
                "status": 'NOT FEASABLE'
            }) 


