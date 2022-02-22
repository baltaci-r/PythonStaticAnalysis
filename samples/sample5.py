def fib(n,):
    ls = [0, 1]
    for i in range(n-2):
        ls.append(ls[-1] + ls[-2])
    return ls
