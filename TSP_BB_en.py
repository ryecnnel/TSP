import numpy as np
from pandas import DataFrame
import math
import copy

class TSP():
    def __init__(self, route_list):
        self.route_df = DataFrame(route_list)
        self.stack_search_nodes = [] # A group of nodes that have been stacked with solutions to the relaxation problem.
        self.present_nodes = [] # The node you are exploring (one or two)
        self.suitable_val = math.inf # Temporary value
        self.suitable_ans = [] # Temporary solution
        self.node_num = self.route_df.shape[0] # the number of node

    # Return the smallest pair of [index, column] values in the given DataFrame.
    def __minimumRoute(self, target_route_df):
        min_index = target_route_df.idxmin(axis=1) # Minimum value column for each row
        minimum = math.inf # Initial value of minimum value
        loc = [-1, -1] # Initial value of position
        for index, column in zip(min_index.index, min_index.values):
            if math.isnan(column): # If all rows are inf, then NaN, which is not minimal
                continue
            if minimum > target_route_df[column][index]:
                minimum = target_route_df[column][index] # Update the minimum value
                loc = [index, column] # Update index and column positions
        return loc

    # Given a default DataFrame and an array of route choices, return the optimal value
    def __calcSuitableSum(self, route_list):
        route_df_tmp = copy.deepcopy(self.route_df)
        route_length = 0
        for route in route_list:
            if route[2] == 0: # When you select this route
                route_length += route_df_tmp[route[1]][route[0]] # Add to path length
                if (route[1] in route_df_tmp.index and route[0] in route_df_tmp.columns):
                    # If the corresponding element still exists in the DataFrame of the reduced path
                    route_df_tmp[route[0]][route[1]] = math.inf
                    # DataFrame[column][index], the reverse path of the corresponding path (2->1 when 1->2) is not adopted, so it is inf
                route_df_tmp = route_df_tmp.drop(route[0], axis=0)
                # Delete the row of the corresponding route
                route_df_tmp = route_df_tmp.drop(route[1], axis=1)
                # Delete the column of the corresponding route
            else: # When this route is not selected
                if (route[0] in route_df_tmp.index and route[1] in route_df_tmp.columns):
                    # If the corresponding element still exists in the DataFrame of the reduced path
                    route_df_tmp[route[1]][route[0]] = math.inf
                    # Since we are not going to adopt it, we will use inf for the corresponding route.

        min_sum = 0 # Add up the path length of the relaxation problem.
        next_route = copy.deepcopy(route_df_tmp) # Keep the DataFrame at this point in next_route
        for index in route_df_tmp.index: # Run on each line
            min_tmp = route_df_tmp.loc[index, :].min() #  Get the minimum value of a row
            min_sum += min_tmp # Add the minimum value
            route_df_tmp.loc[index, :] = route_df_tmp.loc[index, :] - min_tmp # Subtract the minimum value from each element in the row
        for column in route_df_tmp.columns: # Run on each line
            min_tmp = route_df_tmp.loc[:, column].min() # Get the minimum value of a column
            min_sum += min_tmp # Add the minimum value
            route_df_tmp.loc[:, column] = route_df_tmp.loc[:, column] - min_tmp # Subtract the minimum value from each element in the column
        route_length += min_sum # Add to path length
        return route_length, next_route # DataFrame of the route length and the route at the node

    # Check for a closed circuit.
    def __checkClosedCircle(self, route_list, route_df_tmp):
        # route_df_tmp is assumed to be 2x2
        mini_route = self.__minimumRoute(route_df_tmp) # The [index, coumn] of the smallest element of route_df_tmp.
        if mini_route == [-1, -1]: # When route_df_tmp is all inf
            return False
        mini_route.append(0) # Add 0 since this is the route to adopt
        route_list.append(mini_route) # Add to route list
        route_df_tmp = route_df_tmp.drop(mini_route[0], axis=0) # Delete the row
        route_df_tmp = route_df_tmp.drop(mini_route[1], axis=1) # Delete the column
        last_route = [route_df_tmp.index[0], route_df_tmp.columns[0]] # Get the rest of the elements
        last_route.append(0) # Add 0 since this is the route to adopt
        route_list.append(last_route) # Add to route list

        label, counter = 0, 0 # label is the current position, counter is the number of moves
        for i in range(self.node_num): # The maximum number of iterations is the number of nodes
            for route in route_list:
                if route[0] == label and route[2] == 0: # If the starting point is label and it is an adopted path, then
                    new_label = route[1] # Update the label
                    counter += 1 # Incrementing counter
            label = new_label
            if label == 0: # If label is zero, the round is over.
                break
        if counter == self.node_num: # If the number of moves is equal to the number of nodes, then the circuit is closed.
            return True
        else:
            return False

    # Add a new route to the route to a node and add it to present_nodes
    def __setPresentNodes(self, target_route, target_branch):
        for status in range(2):
            target_route_tmp = copy.deepcopy(target_route) # Copy target_route
            target_route_tmp.append(status) # Add status (adoption status).
            target_branch_tmp = copy.deepcopy(target_branch) # Copy target_branch
            target_branch_tmp.append(target_route_tmp) # Add route
            self.present_nodes.append(target_branch_tmp) # Add to present_nodes

    #Evaluate the corresponding node, if branching is possible, evaluate the node, if branching is finished, compare with provisional value
    def __evaluateNode(self, target_node):
        if (False if target_node[1].shape == (2, 2) else True):  # When we can still branch. Condition is that the DataFrame of target_node has reached 2x2.
            next_route = self.__minimumRoute(target_node[1]) # Get the minimum value [index, column]
            if next_route != [-1, -1]: # If [-1, -1], the distance will be inf, so not suitable, do not add anything to present_nodes
                self.__setPresentNodes(next_route, target_node[0])
        else: # At the end of the branch
            if self.__checkClosedCircle(target_node[0], target_node[1]): # Is it a closed circuit?
                if self.suitable_val > target_node[2]: # Less than the provisional value?
                    self.suitable_val = target_node[2] # Update the temporary value
                    self.suitable_ans = target_node[0] # Update the temporary solution

    # Converting a list of routes into a path
    def __displayRoutePath(self, route_list):
        label, counter, route_path = 0, 0, "0" # label is the current position, counter is the number of moves, and route_path is the route.
        for i in range(self.node_num): # The maximum number of iterations is the number of nodes
            for route in route_list:
                if route[0] == label and route[2] == 0: # If the starting point is label and it is an adopted path, then
                    new_label = route[1] # Update the label
                    route_path += " -> " + str(new_label)
                    counter += 1 # Incrementing counter
            label = new_label
            if label == 0: # If label is zero, the round is over.
                break
        return route_path

    # Compute the optimal value and optimal solution (main method)
    def getSuitableAns(self):
        target_route = self.__minimumRoute(self.route_df) # Get the minimum element of the route's DataFrame.
        self.__setPresentNodes(target_route, []) # Set to present_nodes

        while True:
            if self.suitable_val != math.inf: # When the tentative value of the optimal solution is set
                self.stack_search_nodes = list(filter(lambda node: node[2] < self.suitable_val, self.stack_search_nodes)) # Exclude if the solution to the relaxation problem for the stacked nodes exceeds the provisional value.

            while len(self.present_nodes) != 0: # If there is a list of search, then we ask for a solution to the relaxation problem and stack
                first_list = self.present_nodes[0] # Get present_nodes to evaluate
                self.present_nodes.pop(0) # Evaluate, so exclude from present_nodes
                route_length, next_route = self.__calcSuitableSum(first_list) # Get the solution to the relaxation problem
                self.stack_search_nodes.insert(0, [first_list, next_route, route_length]) # stack

            if len(self.stack_search_nodes) == 0: # When the stack runs out, it's done.
                break;

            # When the number of stacked nodes is one, or when the solution of the first relaxation problem of a stacked node is smaller than the solution of the second relaxation problem (in order to check the best solution first)
            if len(self.stack_search_nodes) == 1 or self.stack_search_nodes[0][2] <= self.stack_search_nodes[1][2]:
                self.__evaluateNode(self.stack_search_nodes[0]) # Evaluate the first node
                self.stack_search_nodes.pop(0) # Delete the first node
            else:
                self.__evaluateNode(self.stack_search_nodes[1]) # Evaluate the second node
                self.stack_search_nodes.pop(1) # Delete the second node

        return self.suitable_val, self.__displayRoutePath(self.suitable_ans) # Return optimal value, optimal path

# Route List ( c_ij : distance between city i and j )
C = [
        [math.inf, 30, 30, 25, 10],
        [30, math.inf, 30, 45, 20],
        [30, 30, math.inf, 25, 20],
        [25, 45, 25, math.inf, 30],
        [10, 20, 20, 30, math.inf]
    ]
# Instantiate and use methods
salesman = TSP(C)
suitable_val, suitable_route = salesman.getSuitableAns()
print(suitable_val)
print(suitable_route)