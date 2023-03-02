import gurobipy as gp

# Define the parameters
num_resources = 10  # number of resources
num_shifts = 2  # number of shifts per day
shift_sizes = [3, 2]  # number of resources needed for each shift
max_shifts_per_day = 1  # maximum number of shifts per resource per day
max_shifts_per_week = 5  # maximum number of shifts per resource per week
start_date = '2023-03-01'  # start date of the schedule
end_date = '2023-03-14'  # end date of the schedule

# Create the model
model = gp.Model('Resource Scheduling')

# Create the decision variables
shifts = {}  # shifts[(r, d, s)] = 1 if resource r is assigned to shift s on day d, 0 otherwise
for r in range(num_resources):
    for d in gp.date_range(start_date, end_date):
        for s in range(num_shifts):
            shifts[(r, d, s)] = model.addVar(vtype=gp.GRB.BINARY)

# Create the constraints
for d in gp.date_range(start_date, end_date):
    for s in range(num_shifts):
        # The number of resources assigned to each shift should be equal to the shift size
        model.addConstr(gp.quicksum(shifts[(r, d, s)] for r in range(num_resources)) == shift_sizes[s])

    for r in range(num_resources):
        # A resource can only be assigned to one shift per day
        model.addConstr(gp.quicksum(shifts[(r, d, s)] for s in range(num_shifts)) <= max_shifts_per_day)

        # A resource can only be assigned to a maximum number of shifts per week
        week_start = d - gp.timedelta(days=d.weekday())
        week_end = week_start + gp.timedelta(days=6)
        model.addConstr(gp.quicksum(shifts[(r, dd, s)] for dd in gp.date_range(week_start, week_end) for s in range(num_shifts)) <= max_shifts_per_week)

        # A resource scheduled for shift B cannot be scheduled for shift A the following day
        if s == 0 and d < end_date - gp.timedelta(days=1):
            model.addConstr(shifts[(r, d, s)] + shifts[(r, d + gp.timedelta(days=1), 1)] <= 1)

    # On weekends, assign 2 resources to each shift
    if d.weekday() >= 5:  # weekend
        model.addConstr(gp.quicksum(shifts[(r, d, 0)] for r in range(num_resources)) == 2)
        model.addConstr(gp.quicksum(shifts[(r, d, 1)] for r in range(num_resources)) == 2)

# Create the objective function
obj = gp.quicksum((gp.quicksum(shifts[(r, d, s)] for s in range(num_shifts)) - (max_shifts_per_week / 2)) ** 2 for r in range(num_resources) for d in gp.date_range(start_date, end_date))
model.setObjective(obj)

# Solve the model
model.optimize()

# Print the schedule
for d in gp.date_range(start_date, end_date):
    print(f'Day {d}:')
    for s in range(num_shifts):
        print(f'Shift {s}:')
        for r in range(num_resources):
            if shifts[(r, d, s)].x > 0.5:
                print(f'Resource {r}')
    print()
