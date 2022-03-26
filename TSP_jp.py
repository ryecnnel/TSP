import numpy as np
from pandas import DataFrame
import math
import copy
import time

class Salesman():
    def __init__(self, route_list):
        self.route_df = DataFrame(route_list)
        self.stack_search_nodes = [] # 緩和問題の解を出してstackしたnode群
        self.present_nodes = [] # まさに探索中のnode(1つか2つ)
        self.suitable_val = math.inf # 暫定値
        self.suitable_ans = [] # 暫定解
        self.node_num = self.route_df.shape[0] # nodeの個数

    # 与えられたDataFrameのうち最小値の[index, column]の一組を返す
    def __minimumRoute(self, target_route_df):
        min_index = target_route_df.idxmin(axis=1) # 各行ごとに最小値のcolumn
        minimum = math.inf # 最小値の初期値
        loc = [-1, -1] # 位置の初期値
        for index, column in zip(min_index.index, min_index.values):
            if math.isnan(column): # 行全てinfのときはNaNとなる, これは最小にならない
                continue
            if minimum > target_route_df[column][index]:
                minimum = target_route_df[column][index] # 最小値の更新
                loc = [index, column] # index, column位置の更新
        return loc

    # デフォルトのDataFrameと経路選択の配列を与えると最適値を返す
    def __calcSuitableSum(self, route_list):
        route_df_tmp = copy.deepcopy(self.route_df)
        route_length = 0
        for route in route_list:
            if route[2] == 0: # このrouteを選択するとき
                route_length += route_df_tmp[route[1]][route[0]] # 経路長に追加
                if (route[1] in route_df_tmp.index and route[0] in route_df_tmp.columns): # 小さくなった経路のDataFrameに該当要素がまだ存在するとき
                    route_df_tmp[route[0]][route[1]] = math.inf # DataFrame[column][index], 該当の道の逆経路(1->2のとき2->1)は採択しないのでinfとする
                route_df_tmp = route_df_tmp.drop(route[0], axis=0) # 該当経路の行削除
                route_df_tmp = route_df_tmp.drop(route[1], axis=1) # 該当経路の列削除
            else: # このrouteを選択しないとき
                if (route[0] in route_df_tmp.index and route[1] in route_df_tmp.columns): # 小さくなった経路のDataFrameに該当要素がまだ存在するとき
                    route_df_tmp[route[1]][route[0]] = math.inf # 採用しないので該当の経路をinfとする

        min_sum = 0 # 緩和問題の経路長を足していく
        next_route = copy.deepcopy(route_df_tmp) # この時点のDataFrameをnext_routeに保持
        for index in route_df_tmp.index: # 各行で実行
            min_tmp = route_df_tmp.loc[index, :].min() # 行の最小値を取得
            min_sum += min_tmp # 最小値を足す
            route_df_tmp.loc[index, :] = route_df_tmp.loc[index, :] - min_tmp # その行の各要素から最小値を引く
        for column in route_df_tmp.columns: # 各列で実行
            min_tmp = route_df_tmp.loc[:, column].min() # 列の最小値を取得
            min_sum += min_tmp # 最小値を足す
            route_df_tmp.loc[:, column] = route_df_tmp.loc[:, column] - min_tmp # その列の各要素から最小値を引く
        route_length += min_sum # 経路長に追加
        return route_length, next_route # 経路長とそのノード時点の経路のDataFrame

    # 一巡閉路かチェックする
    def __checkClosedCircle(self, route_list, route_df_tmp):
        # route_df_tmpは2x2であることが前提
        mini_route = self.__minimumRoute(route_df_tmp) # route_df_tmpの最小の要素の[index, coumn]
        if mini_route == [-1, -1]: #route_df_tmpが全てinfのとき
            return False
        mini_route.append(0) # 採択するrouteなので0を追加
        route_list.append(mini_route) # routeリストに追加
        route_df_tmp = route_df_tmp.drop(mini_route[0], axis=0) # 行削除
        route_df_tmp = route_df_tmp.drop(mini_route[1], axis=1) # 列削除
        last_route = [route_df_tmp.index[0], route_df_tmp.columns[0]] # 残りの要素を取得
        last_route.append(0) # 採択するrouteなので0を追加
        route_list.append(last_route) # routeリストに追加

        label, counter = 0, 0 # labelは現在の位置, counterは移動回数
        for i in range(self.node_num): # 繰り返しの最大はノードの個数
            for route in route_list:
                if route[0] == label and route[2] == 0: # 始点がlabelで採択経路であれば
                    new_label = route[1] # labelの更新
                    counter += 1 # couterのインクリメント
            label = new_label
            if label == 0: # labelが0なら一巡終わり
                break
        if counter == self.node_num: # 移動回数がノードの数と一致すれば一巡閉路
            return True
        else:
            return False

    # あるノードまでの経路に新たな経路を追加しpresent_nodesに追加する
    def __setPresentNodes(self, target_route, target_branch):
        for status in range(2):
            target_route_tmp = copy.deepcopy(target_route) # target_eleをコピー
            target_route_tmp.append(status) # status(採択の可否）を追加
            target_branch_tmp = copy.deepcopy(target_branch) # target_branchをコピー
            target_branch_tmp.append(target_route_tmp) # routeを追加
            self.present_nodes.append(target_branch_tmp) # present_nodesに追加

    # 該当ノードを評価する, 分岐が可能ならノードを評価, 分岐が終了なら暫定値との比較
    def __evaluateNode(self, target_node):
        if (False if target_node[1].shape == (2, 2) else True):  # まだ分岐いけるとき, 判断はtarget_nodeのDataFrameが2x2に到達していないこと
            next_route = self.__minimumRoute(target_node[1]) # 最小の要素を取得 [index, column]
            if next_route != [-1, -1]: # [-1, -1]のときは距離がinfになるので不適, present_nodesには何も追加しない
                self.__setPresentNodes(next_route, target_node[0])
        else: # 分岐終わりのとき
            if self.__checkClosedCircle(target_node[0], target_node[1]): # 一巡閉路であるか
                if self.suitable_val > target_node[2]: # 暫定値より小さいか
                    self.suitable_val = target_node[2] # 暫定値の更新
                    self.suitable_ans = target_node[0] # 暫定解の更新
        print("suitable_solution, tn[0]:{}".format(target_node[0]))
        print("dataframe, tn[1]:{}".format(target_node[1]))
        print("suitable_value, tn[2]:{}".format(target_node[2]))

    # 経路のリストをpathに変換する
    def __displayRoutePath(self, route_list):
        label, counter, route_path = 0, 0, "0" # labelは現在の位置, counterは移動回数, route_pathは経路
        for i in range(self.node_num): # 繰り返しの最大はノードの個数
            for route in route_list:
                if route[0] == label and route[2] == 0: # 始点がlabelで採択経路であれば
                    new_label = route[1] # labelの更新
                    route_path += " -> " + str(new_label)
                    counter += 1 # couterのインクリメント
            label = new_label
            if label == 0: # labelが0なら一巡終わり
                break
        return route_path

    # 最適値と最適解を計算する (メインのメソッド)
    def getSuitableAns(self):
        target_route = self.__minimumRoute(self.route_df) # routeのDataFrameの最小要素を取得
        self.__setPresentNodes(target_route, []) # present_nodesにセット
        while True:
            if self.suitable_val != math.inf: # 最適解の暫定値がセットされているとき
                self.stack_search_nodes = list(filter(lambda node: node[2] < self.suitable_val, self.stack_search_nodes))
                # stackされているノードの緩和問題の解が暫定値を超えていたら除く

            while len(self.present_nodes) != 0: # 探索のリストが存在するならば緩和問題の解を問いてstack
                first_list = self.present_nodes[0] # present_nodesを評価するために取得
                self.present_nodes.pop(0) # 評価するのでpresent_nodesからは除く
                route_length, next_route = self.__calcSuitableSum(first_list) # 緩和問題の解を取得
                self.stack_search_nodes.insert(0, [first_list, next_route, route_length]) # stackする

            if len(self.stack_search_nodes) == 0: # stackがなくなったら終了
                break;

            # stackされているノードの個数が1個のときまたはstackされているノードの1個目の緩和問題の解が2個目の緩和問題の解より小さいとき(良さそうな解から確認していくため)
            if len(self.stack_search_nodes) == 1 or self.stack_search_nodes[0][2] <= self.stack_search_nodes[1][2]:
                self.__evaluateNode(self.stack_search_nodes[0]) # 1番目のノードを評価
                self.stack_search_nodes.pop(0) # 1番目のノードの削除
            else:
                self.__evaluateNode(self.stack_search_nodes[1]) # 2番目のノードを評価
                self.stack_search_nodes.pop(1) # 2番目のノードの削除

        return self.suitable_val, self.__displayRoutePath(self.suitable_ans) # 最適値、最適経路を返す

# 問題のルートのリスト

route_list = [
        [math.inf, 30, 30, 25, 10],
        [30, math.inf, 30, 45, 20],
        [30, 30, math.inf, 25, 20],
        [25, 45, 25, math.inf, 30],
        [10, 20, 20, 30, math.inf]
    ]
# インスタンス化してメソッド使用
start_time = time.process_time()
salesman = Salesman(route_list)
suitable_val, suitable_route = salesman.getSuitableAns()
end_time = time.process_time()
print(suitable_val)
print(suitable_route)
elapsed_time = end_time - start_time
print(elapsed_time)