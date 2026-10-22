import random 

def flip(chromosome, mp):
    for i in range(len(chromosome)):

        r = random.uniform(0,1)
        if r <= mp:
            chromosome[i] ^= 1
            # if chromosome[i] == 0:
            #     chromosome[i] = 1
            # else:
            #     chromosome[i] = 0

    return chromosome
