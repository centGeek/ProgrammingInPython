amount_of_numbers = 100


def sieve_of_eratosthenes(primes_to_this_number):
    tab = [True] * primes_to_this_number
    primes = []
    for i in range(2, primes_to_this_number):
        if tab[i]:
            primes.append(i)
            for j in range(i * i, primes_to_this_number, i):
                tab[j] = False
    return primes


print(f"Prime numbers to {amount_of_numbers} {sieve_of_eratosthenes(amount_of_numbers)}")
