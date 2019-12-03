import fileinput

for line in fileinput.input():
    line = line.strip()
    a, b, c, d = line.split(".")
    print(".".join([d,c,b,a]) + ".in-addr.arpa")
