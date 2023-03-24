def tohex(value, number_of_bits):
    return hex((value + (1 << number_of_bits)) % (1 << number_of_bits))