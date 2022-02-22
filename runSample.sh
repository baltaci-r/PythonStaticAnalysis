python runAnalysis.py -t ast -s "def gcd(a, b):
    if a<b:
        c: int = a
        a: int = b
        b: int = c

    while b != 0 :
        c: int = a
        a: int = b
        b: int = c % b
    return a"