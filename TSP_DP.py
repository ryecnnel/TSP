import math
import time

def dfs(S, v, dp):
    if dp[S][v] != -1: # 訪問済みならメモを返す
        return dp[S][v]
    if S==(1<<V)-1 and v==0: # 全ての頂点を訪れて頂点0に戻ってきた
        return 0 # もう動く必要はない

    res = math.inf
    for u in range(V):
        if S>>u & 1 == 0: # 未訪問かどうか
            res = min(res, dfs(S|1<<u, u, dp)+cost[v][u])
    dp[S][v] = res
    return res


cost = [
        [math.inf, 30, 30, 25, 10],
        [30, math.inf, 30, 45, 20],
        [30, 30, math.inf, 25, 20],
        [25, 45, 25, math.inf, 30],
        [10, 20, 20, 30, math.inf]
    ]

V, E = 5, 10


# 開始
start_time = time.process_time()
dp = [[-1] * V for _ in range(1<<V)] # dp[S][v]

ans = dfs(0, 0, dp) # 頂点0からスタートする。ただし頂点0は未訪問とする
# 修了
end_time = time.process_time()

if ans == math.inf:
    print(-1)
else:
    print (ans)
    elapsed_time = end_time - start_time
    print(elapsed_time)

