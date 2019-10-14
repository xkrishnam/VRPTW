from itertools import combinations
import copy

distance_mtrx = [[0, 3, 26, 55, 42, 56, 63, 9, 100],
                 [3, 0, 3, 5, 4, 7, 4, 2, 3],
                 [26, 3, 0, 2, 6, 3, 6, 8, 6],
                 [55, 5, 2, 0, 5, 5, 9, 5, 5],
                 [42, 4, 6, 5, 0, 2, 5, 8, 2],
                 [56, 7, 3, 5, 2, 0, 6, 4, 6],
                 [63, 4, 6, 9, 5, 6, 0, 2, 8],
                 [9, 2, 8, 5, 8, 4, 2, 0, 3],
                 [100, 3, 6, 5, 2, 6, 8, 3, 0]]

service_time_in = [[0, 100],
                   [24, 35],
                   [20, 25],
                   [13, 15],
                   [14, 23],
                   [34, 46],
                   [87, 102],
                   [80, 89],
                   [0, 500]
                   ]

pickup_delivery_time_in = [[0, 0],
                           [2, 3],
                           [3, 5],
                           [4, 2],
                           [5, 2],
                           [2, 5],
                           [4, 4],
                           [3, 6],
                           [0, 0]]

tabu_list = []


# cost minimization function --- min(t[i][j]+wait_time[j])
def get_heuristic(src, dest, service_start_time):
    wait = get_earliest_service_time(dest) - service_start_time - get_distance(src, dest) - get_pickup_time(src
                                                                                                            ) - get_delivery_time(
        src)
    wait = wait if wait > 0 else 0
    print('waiting time : {0} Distance : {1}'.format(wait, get_distance(src, dest)))
    return get_distance(src, dest) + wait


def generate__initial_solution():
    numOfV = 3
    setOfV = range(1, numOfV + 1)
    routes = [[]]  # zero indexed route kept empty to maintain meaningful reference
    service_start_time = [[]]
    cost_data = [[]]
    unserviced = list(range(1, len(distance_mtrx) - 1))
    k = 1
    while len(unserviced) > 0 and k in setOfV:  # Vehicle level loop
        routes.append([0])
        service_start_time.append([0])
        cost_data.append([0])
        best_nbr = 0
        minim = 1000000
        end_node = len(distance_mtrx) - 1
        no_progress = False
        route_index = 1
        while len(
                unserviced) > 0 and not no_progress:  # Route level loop for vehicle gives route for vehicle when completed

            visiting = best_nbr
            print('----------------------------------------------------------------')
            print('starting looking up best next node for : {0}'.format(visiting))
            no_progress = False
            minim = 100000
            for i in range(1, len(distance_mtrx) - 1):  # finding best neighbour
                if i == visiting or not is_servisable(visiting, i, service_start_time[k][
                    route_index - 1]) or i not in unserviced:
                    no_progress = True
                    continue
                no_progress = False
                print('checking cost for : {0}'.format(i))
                cost1 = get_heuristic(visiting, i, service_start_time[k][route_index - 1])
                if int(cost1) < int(minim) and i not in routes[k] and i != end_node and i in unserviced:
                    minim = cost1
                    if len(cost_data[k]) < route_index + 1:
                        cost_data[k].append(0)
                    if len(routes[k]) < route_index + 1:
                        routes[k].append(0)
                    if len(service_start_time[k]) < route_index + 1:
                        service_start_time[k].append(0)
                    cost_data[k][route_index] = minim
                    routes[k][route_index] = i
                    best_nbr = i
                    print('now best next node for : {0} is {1}'.format(visiting, i))
                    service_start_time[k][route_index] = get_service_start_time(i, service_start_time[k][
                        route_index - 1], visiting)
            # print(no_progress)
            if best_nbr != 0:
                unserviced.remove(best_nbr)
            route_index = route_index + 1
        routes[k].append(end_node)
        cost_data[k].append(distance_mtrx[routes[k][-2]][end_node])
        k = k + 1

    if len(unserviced) > 0:
        print('making route for customer which are not serviced due to delay the route will be used during tabu search')
        routes.append([0])
        for i in unserviced:
            routes[k].append(i)
        routes[k].append(len(distance_mtrx) - 1)
        print(routes[k])

    for route in routes:
        if is_empty_route(route):
            print('removing empty routes that is from start depot to end depot only')
            cost_data.remove(cost_data[routes.index(route)])
            routes.remove(route)
    return cost_data, routes


def is_servisable(src, dest, src_service_start_time):
    if get_distance(src, dest) + src_service_start_time + get_pickup_time(src) + get_delivery_time(
            src) > get_latest_service_time(dest):
        return False
    return True


def get_delay(src, dest, si_src):
    return service_time_in[dest][1] - distance_mtrx[src][dest] - pickup_delivery_time_in[src][0] - \
           pickup_delivery_time_in[src][1] - si_src


def get_exchange_neighbour(soln):
    neighbours = []
    for combo in list(combinations(soln, 2)):
        for i in combo[0][:-1]:
            for j in combo[1][:-1]:
                if i == 0 or j == 0:
                    continue
                _tmp = copy.deepcopy(soln)
                _c0 = copy.deepcopy(combo[0])
                _c1 = copy.deepcopy(combo[1])
                idx1 = _tmp.index(_c0)
                idx2 = _tmp.index(_c1)
                if contains(tabu_list, lambda x: x.found_match((j, i, idx1, idx2))):
                    continue
                print('removing {0} from {1}'.format(i, combo[0]))
                _c1.insert(_c1.index(j), i)
                _c0.insert(_c0.index(i), j)
                _c1.remove(j)
                _c0.remove(i)
                _tmp[idx1] = _c0
                _tmp[idx2] = _c1
                neighbours.append((_tmp, get_solution_cost(_tmp), (3, j, i, idx2, idx1, 3)))

        for i in combo[1][1:-1]:
            for j in combo[0][1:-1]:
                if i == 0 or j == 0:
                    continue
                _tmp = copy.deepcopy(soln)
                _c0 = copy.deepcopy(combo[1])
                _c1 = copy.deepcopy(combo[0])
                idx1 = _tmp.index(_c0)
                idx2 = _tmp.index(_c1)
                if contains(tabu_list, lambda x: x.found_match((j, i, idx1, idx2))):
                    continue
                print('removing {0} from {1}'.format(i, combo[1]))
                _c1.insert(_c1.index(j), i)
                _c0.insert(_c0.index(i), j)
                _tmp[idx1] = _c0
                _tmp[idx2] = _c1
                neighbours.append((_tmp, get_solution_cost(_tmp), (3, j, i, idx2, idx1, 3)))

    # print("{0} number of Neighbours after Exchange {1}".format(len(neighbours), neighbours))
    neighbours.sort(key=lambda x: x[1][-1])
    print("{0} number of sorted Neighbours after exchange {1}".format(len(neighbours), neighbours))
    return neighbours[0]


def get_relocate_neighbour(soln):
    neighbours = []
    for combo in list(combinations(soln, 2)):
        for i in combo[0][:-1]:
            for j in combo[1][:-1]:
                if j == 0:
                    continue
                _tmp = copy.deepcopy(soln)
                _c0 = copy.deepcopy(combo[0])
                _c1 = copy.deepcopy(combo[1])
                idx1 = _tmp.index(_c0)
                idx2 = _tmp.index(_c1)
                if contains(tabu_list, lambda x: x.found_match((j, i, idx1, idx2))):
                    continue
                print('removing {0} from {1}'.format(i, combo[0]))
                _c1.remove(j)
                _c0.insert(_c0.index(i) + 1, j)
                _tmp[idx1] = _c0
                _tmp[idx2] = _c1
                neighbours.append((_tmp, get_solution_cost(_tmp), (1, j, i, idx2, idx1, 3)))

        for i in combo[1][:-1]:
            for j in combo[0][:-1]:
                if j == 0:
                    continue
                _tmp = copy.deepcopy(soln)
                _c0 = copy.deepcopy(combo[1])
                _c1 = copy.deepcopy(combo[0])
                idx1 = _tmp.index(_c0)
                idx2 = _tmp.index(_c1)
                if contains(tabu_list, lambda x: x.found_match((j, i, idx1, idx2))):
                    continue
                print('removing {0} from {1}'.format(i, combo[1]))
                _c1.remove(j)
                _c0.insert(_c0.index(i) + 1, j)
                _tmp[idx1] = _c0
                _tmp[idx2] = _c1
                neighbours.append((_tmp, get_solution_cost(_tmp), (1, j, i, idx2, idx1, 3)))

    # print("{0} number of Neighbours after relocation {1}".format(len(neighbours), neighbours))
    neighbours.sort(key=lambda x: x[1][-1])
    print("{0} number of sorted Neighbours after relocation {1}".format(len(neighbours), neighbours))
    return neighbours[0]


def get_neighbours(op, soln):
    if op == 1:
        # relocate op
        return get_relocate_neighbour(soln)
    elif op == 2:
        # relocate split op
        # return get_relocate_split_neighbour(soln)
        pass
    elif op == 3:
        return get_exchange_neighbour(soln)
    elif op == 4:
        # return get_2opt_neighbour(soln)
        pass


def get_solution_cost(soln: list):
    t = 0
    wait = 0
    delay = 0
    for route in soln:
        prev = 0
        for customer in route:
            t = t + get_distance(prev, customer) + get_pickup_time(prev) + get_delivery_time(prev)
            wait = wait + ((get_earliest_service_time(customer) - t) if (get_earliest_service_time(
                customer) - t) > 0 else 0)
            delay = delay + ((t - get_latest_service_time(customer)) if (t - get_latest_service_time(
                customer)) > 0 else 0)
            prev = customer

    return t, delay, wait, t + delay + wait


def tabu_search(routes: list, itrations):
    best_soln = routes
    best_cost = ()
    for i in range(itrations - 1):
        _sol1 = get_neighbours(1, best_soln)
        _sol2 = get_neighbours(3, best_soln)
        if _sol1[1][-1] < _sol2[1][-1]:
            best_soln = _sol1[0]
            best_cost = _sol1[1]
            tabu_list.append(TabuListClass(_sol1[2][0], _sol1[2][1:-1], _sol1[2][-1]))
        else:
            best_soln = _sol2[0]
            best_cost = _sol2[1]
            tabu_list.append(TabuListClass(_sol1[2][0], _sol1[2][1:-1], _sol1[2][-1]))

    return best_soln, best_cost


# input provider methods
def get_distance(src, dest):
    return distance_mtrx[src][dest]


def get_pickup_time(cust):
    return pickup_delivery_time_in[cust][0]


def get_delivery_time(cust):
    return pickup_delivery_time_in[cust][1]


def get_earliest_service_time(cust):
    return service_time_in[cust][0]


def get_latest_service_time(cust):
    return service_time_in[cust][1]


def get_service_start_time(cust, prev_cust_service_start_time, prev_cust):
    time_distance = prev_cust_service_start_time + get_delivery_time(prev_cust) + get_pickup_time(
        prev_cust) + get_distance(prev_cust, cust)
    if time_distance > get_earliest_service_time(cust):
        return time_distance
    else:
        return get_earliest_service_time(cust)


def is_empty_route(route: list):
    if len(route) == 2 and 0 in route and len(distance_mtrx) - 1 in route:
        return True
    return False


def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False


class TabuListClass:
    def __init__(self, op, move, valid_for):
        self.op = op
        self.move = move
        self.valid_for = valid_for

    def checked(self):
        self.valid_for -= 1

    def found_match(self, move):
        if self.move == move and self.valid_for > 0:
            print("found tabu match op : {0} move : {1}".format(self.op, self.move))
            self.valid_for -= 1
            return True
        return False


cost, routes = generate__initial_solution()
print("Best solution: {0}, with total cost: {1}".format(routes, cost))
routes.remove([])
best_soln, best_cost = tabu_search(routes, 20)
print("solution is : {0} with costs : {1}".format(best_soln, best_cost))
for route in best_soln:
    print("Route{0} is: {1}".format(best_soln.index(route), route))

print("total distance: {0}".format(best_cost[0]))
print("total waiting: {0}".format(best_cost[1]))
print("total delay: {0}".format(best_cost[2]))
print("total cost: {0}".format(best_cost[3]))
