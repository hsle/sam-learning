import itertools

from .fama_learning.pddl.conditions import Conjunction, Literal

def generate_all_possible_literals(predicates, action_params):
    all_literals = []
    for p in predicates:
        predicate_types = []
        if not p.arguments:
            all_literals += [Literal(p.name, [], True)]
            all_literals += [Literal(p.name, [], False)]
        else:
            for obj in p.arguments:
                predicate_types.append(obj.type_name)

        objects_for_predicate = [[o for o in action_params if o.type_name in types] for types in predicate_types]

        combinations = list(itertools.product(*objects_for_predicate))

        for comb in combinations:
            if (len(comb) == 1 or (len(comb) > 1 and comb[0].name != comb[1].name)):
                for valuation in [True, False]:
                    all_literals += [Literal(p.name, [o.name for o in comb], valuation)]
            elif (len(comb) > 1 and comb[0].name == comb[1].name):
                all_literals += [Literal(p.name, [o.name for o in comb], True)]

    return all_literals


def get_precondition_effect(model, trajectories):
    for action in model.schemata:
        all_literals = generate_all_possible_literals(model.predicates, action.parameters)
        effects = []

        for trajectory in trajectories:
            for index in range(trajectory.length - 1):
                pre_state = trajectory.states[index]
                post_state = trajectory.states[index + 1]
                next_action = pre_state.next_action
                if action.name != next_action.name:
                    continue

                parameters_name = [p.name for p in action.parameters]
                param_binding = dict(zip(parameters_name, next_action.arguments))
                invert_binding = dict(zip(next_action.arguments, parameters_name))

                all_literals = [literal for literal in all_literals if (literal.rename_variables(param_binding)
                                                                        in pre_state.literals) or (
                                            len(literal.args) == 0 and literal in pre_state.literals)]

                for literal in pre_state.literals:
                    if literal.valuation == True:
                        if literal.negate() in post_state.literals:
                            new_eff = literal.rename_variables(invert_binding).negate()
                            if new_eff not in effects:
                                effects.append(new_eff)
                    else:
                        if literal.positive() in post_state.literals:
                            new_eff = literal.rename_variables(invert_binding).positive()
                            if new_eff not in effects:
                                effects.append(new_eff)
        action.precondition = Conjunction(all_literals)
        action.effects = effects

if __name__ == '__main__':
    print('test')