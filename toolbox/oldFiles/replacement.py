import random

def mixed_replacement(old_pop, offspring, fittnessfunc, popsize, strong):
    combined_pop = old_pop + offspring
    combined_pop.sort(key=fittnessfunc, reverse=True)


    new_pop = combined_pop[:strong]

    remains = combined_pop[strong:]
    weak = popsize - strong

    rand_weak = random.sample(remains, weak)

    new_pop += rand_weak

    return new_pop