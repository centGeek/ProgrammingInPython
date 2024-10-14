import math
from collections import Counter
def prime_factors(n):
    if not is_integer(n):
        raise ValueError("You number have to be integer")
    factors = Counter()
    for i in range(2, round(math.sqrt(n)) + 1):
        while n % i == 0:
            factors[i] += 1
            n = n // i
    if n < 1:
        raise ValueError("Number can not be lower than 1")
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors
def is_integer(num):
    return num == int(num)
def lcm(a, b):
    factors_a = prime_factors(a)
    factors_b = prime_factors(b)
    lcm_factors = factors_a | factors_b    
    
    lcm = 1
    lcm_factors_keys = list(lcm_factors.keys())
    lcm_factors_values = list(lcm_factors.values())

    for i in range(0, len(lcm_factors)):
        lcm *= lcm_factors_keys[i] ** lcm_factors_values[i]
    return lcm
print(lcm(192, 348))