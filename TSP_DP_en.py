import math
i = 0
def tsp_dp(stack_search_nodes, present_node, dp, count):
    print("cycle{}: ssn:{}, pn:{}".format(count, bin(stack_search_nodes), present_node))
    if dp[stack_search_nodes][present_node] != -1: # If you've already visited, return the note.
        print("already visited. return dp")
        print(dp[stack_search_nodes][present_node])
        return dp[stack_search_nodes][present_node]
    if stack_search_nodes==(1<<V)-1 and present_node==0: # you've visited all nodes, and you are back at nodes 0.
        print("have visited all nodes")
        return 0 # We don't have to move anymore.

    res = math.inf
    for u in range(V):
        if stack_search_nodes>>u & 1 == 0: # Unvisited or not
            res = min(res, tsp_dp(stack_search_nodes|1<<u, u, dp, count+1) + C[present_node][u])
            print("unvisited, so updated, res:{}, present_node:{}, u;{}, count:{}".format(res, bin(present_node), u, count))
    dp[stack_search_nodes][present_node] = res
    return res


C = [
        [math.inf, 30, 30, 25, 10],
        [30, math.inf, 30, 45, 20],
        [30, 30, math.inf, 25, 20],
        [25, 45, 25, math.inf, 30],
        [10, 20, 20, 30, math.inf]
    ]

V, E = 5, 10

dp = [[-1] * V for _ in range(1<<V)] # dp[stack_search_nodes][present_node]

ans = tsp_dp(0, 0, dp, 0) # Start at vertex 0. However, vertex 0 is not visited.
if ans == math.inf:
    print(-1)
else:
    print (ans)

