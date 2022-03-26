# print(S|1<<u, u, d)
# bitで、0 or 1<<0(=1)
for u in range(5):
    if 0>>u & 1 == 0: # Unvisited or not
        print(0|1<<u)
        print(0, u)