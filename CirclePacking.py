import pyomo.environ as pe


def CirclePacking(size):

    model = pe.AbstractModel()
    # size
    model.n = pe.Param(default=4)
    # set of variables, useful for sum and iterations
    model.N = pe.RangeSet(model.n)
    model.x = pe.Var(model.N,  bounds=(0.0, 1.0))
    model.y = pe.Var(model.N,  bounds=(0.0, 1.0))
    model.r = pe.Var(bounds=(0.0, 1.0))

    def no_overlap_rule(model, i, j):
        if i < j:
            return(
                (model.x[i] - model.x[j])**2
                + (model.y[i] - model.y[j])**2 >= 4*model.r**2
            )
        else:
            return pe.Constraint.Skip

    model.no_overlap = pe.Constraint(model.N, model.N, rule=no_overlap_rule)

    def Inside_x_min_rule(model, i):
        return model.x[i] >= model.r
    model.Inside_x_min = pe.Constraint(model.N, rule=Inside_x_min_rule)

    def Inside_y_min_rule(model, i):
        return model.y[i] >= model.r
    model.Inside_y_min = pe.Constraint(model.N, rule=Inside_y_min_rule)

    def Inside_x_max_rule(model, i):
        return model.x[i] <= 1-model.r
    model.Inside_x_max = pe.Constraint(model.N, rule=Inside_x_max_rule)

    def Inside_y_max_rule(model, i):
        return model.y[i] <= 1-model.r
    model.Inside_y_max = pe.Constraint(model.N, rule=Inside_y_max_rule)

    def radius_rule(model):
        return - model.r

    # then we created the objective: function and sense of optimization
    model.obj = pe.Objective(rule=radius_rule, sense=pe.minimize)

    model.n = size
    # return instance
    return model.create_instance()


def CirclePacking_3D(size):

    model = pe.AbstractModel()
    # size
    model.n = pe.Param(default=4)
    # set of variables, useful for sum and iterations
    model.N = pe.RangeSet(model.n)
    model.x = pe.Var(model.N,  bounds=(0.0, 1.0))
    model.y = pe.Var(model.N,  bounds=(0.0, 1.0))
    model.z = pe.Var(model.N,  bounds=(0.0, 1.0))
    model.r = pe.Var(bounds=(0.0, 1.0))

    def no_overlap_rule(model, i, j):
        if i < j:
            return(
                (model.x[i] - model.x[j])**2
                + (model.y[i] - model.y[j])**2
                + (model.z[i] - model.z[j])**2 >= 4*model.r**2
            )
        else:
            return pe.Constraint.Skip

    model.no_overlap = pe.Constraint(model.N, model.N, rule=no_overlap_rule)

    def Inside_x_min_rule(model, i):
        return model.x[i] >= model.r
    model.Inside_x_min = pe.Constraint(model.N, rule=Inside_x_min_rule)

    def Inside_y_min_rule(model, i):
        return model.y[i] >= model.r
    model.Inside_y_min = pe.Constraint(model.N, rule=Inside_y_min_rule)

    def Inside_z_min_rule(model, i):
        return model.z[i] >= model.r
    model.Inside_z_min = pe.Constraint(model.N, rule=Inside_z_min_rule)

    def Inside_x_max_rule(model, i):
        return model.x[i] <= 1-model.r
    model.Inside_x_max = pe.Constraint(model.N, rule=Inside_x_max_rule)

    def Inside_y_max_rule(model, i):
        return model.y[i] <= 1-model.r
    model.Inside_y_max = pe.Constraint(model.N, rule=Inside_y_max_rule)

    def Inside_z_max_rule(model, i):
        return model.z[i] <= 1-model.r
    model.Inside_z_max = pe.Constraint(model.N, rule=Inside_z_max_rule)

    def radius_rule(model):
        return - model.r

    # then we created the objective: function and sense of optimization
    model.obj = pe.Objective(rule=radius_rule, sense=pe.minimize)

    model.n = size
    # return instance
    return model.create_instance()
