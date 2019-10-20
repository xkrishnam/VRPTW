import sys
from itertools import combinations
import copy
from time import perf_counter

distance_mtrx = [
    [0, 14, 4, 5, 22, 6, 7, 9, 7, 7, 2, 100],
    [14, 0, 12, 7, 9, 15, 18, 12, 11, 19, 7, 31],
    [4, 12, 0, 11, 12, 17, 7, 6, 12, 9, 4, 21],
    [5, 7, 11, 0, 8, 11, 16, 5, 9, 7, 12, 14],
    [22, 9, 12, 8, 0, 7, 8, 4, 9, 14, 12, 24],
    [6, 15, 17, 11, 7, 0, 6, 4, 6, 24, 11, 19],
    [7, 18, 7, 16, 8, 6, 0, 12, 8, 15, 9, 11],
    [9, 12, 6, 5, 4, 4, 12, 0, 12, 14, 4, 16],
    [7, 11, 12, 9, 9, 6, 8, 12, 0, 21, 25, 21],
    [7, 19, 9, 7, 14, 24, 15, 14, 21, 0, 12, 20],
    [2, 7, 4, 12, 12, 11, 9, 4, 25, 12, 0, 14],
    [100, 31, 21, 14, 24, 19, 11, 16, 21, 20, 14, 0]]

service_time_in = [[0, 150],
                   [25, 40],
                   [145, 160],
                   [20, 35],
                   [410, 430],
                   [55, 70],
                   [375, 390],
                   [60, 85],
                   [45, 55],
                   [220, 235],
                   [95, 110],
                   [0, 720]]

pickup_delivery_time_in = [[0, 0],
                           [2, 1],
                           [2, 1],
                           [2, 2],
                           [4, 3],
                           [2, 2],
                           [3, 2],
                           [4, 3],
                           [4, 3],
                           [3, 2],
                           [3, 2],
                           [0, 0]]

number_of_vehicle = 3
tabu_itrs = 40
aspiration = 100
sn = 0
retention = 7
en = len(distance_mtrx) - 1
unserviced = list(range(1, en + 1))
tabu_list = []
logging=False

def remove_us(c):
    if c != en and c in unserviced:
        unserviced.remove(c)



'''
following method calculates cost for travelling to one node to other node
Parameters :
1. prev     -- previous node number -- if travelling from node 2 to node 5 then prev = 2
2. c        -- next node(customer)  -- if travelling from node 2 to node 5 then c = 5
3. sst_prev -- service start time for previous node
4. isPdl    -- boolean -- True if there is delay reaching to previous customer false otherwise

returns:

1. d                        -- distance travelled
2. w                        -- waiting time
3. dl                       -- delay time
4. (w/4)+(dl/4)+(dl)        -- cost which needs to be minimized by greedy and tabu search
5. sst                      -- Service start time
6. isd                      -- is delayed 
'''
def get_cost(prev, c, sst_prev, ispdl):
    d = distance_mtrx[prev][c]
    pd = pickup_delivery_time_in[prev][0] + pickup_delivery_time_in[prev][1] if not ispdl else 0
    dl = sst_prev + pd + d - service_time_in[c][1] if sst_prev + pd + d - service_time_in[c][1] > 0 else 0
    w = service_time_in[c][0] - sst_prev - pd - d if service_time_in[c][0] - sst_prev - pd - d > 0else 0
    sst = sst_prev + pd + d + w
    isd = True if dl > 0 else False
    return d, w, dl, (w/4)+(dl/4)+(dl), sst, isd


'''
Greedy algorithm to find initial solution

NO parameters passed
returns: solution with route in 2D array like solution : [[route-1][route-2].....] 
'''
def get_initial_solution():
    rs = []
    k = 1
    sst_prev = 0
    ispdl = False
    bn = 0
    bc = 0
    while k in range(1, number_of_vehicle + 1):
        prev = 0
        rt = [0]

        while not prev == en:
            minim = 99999
            for c in unserviced:
                if prev == en:
                    break
                if prev == 0 and c == en:
                    continue
                if k == number_of_vehicle and len(unserviced) > 1 and c == en:
                    continue
                d, w, dl, cost, sst, isd = get_cost(prev, c, sst_prev, ispdl)
                if cost < minim:
                    bn = c
                    bc = cost
                    minim = cost
                    sst_prev = sst
                    ispdl = isd
            rt.append(bn)
            prev = bn
            remove_us(bn)
        rs.append(rt)
        k += 1
    return rs


'''
Following function takes solution as input and returns the neighbouring solution by exchanging one node from a solution 
to one node from other solution

returns the all neighbouring solution sorted with cost in ascending order
'''
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
                _c1.insert(_c1.index(j), i)
                _c0.insert(_c0.index(i), j)
                _c1.remove(j)
                _c0.remove(i)
                _tmp[idx1] = _c0
                _tmp[idx2] = _c1
                if is_move_allowed((j, i, idx1, idx2), soln, _tmp, 3):
                    neighbours.append((_tmp, get_solution_actual_cost(_tmp), (3, j, i, idx2, idx1, retention)))
                    print_log('exchanging {0} from {1} to {2} from {3} resulting solution {4}'.format(j, soln[idx2], i, soln[idx1], _tmp))

        for i in combo[1][:-1]:
            for j in combo[0][:-1]:
                if i == 0 or j == 0:
                    continue
                _tmp = copy.deepcopy(soln)
                _c0 = copy.deepcopy(combo[1])
                _c1 = copy.deepcopy(combo[0])
                idx1 = _tmp.index(_c0)
                idx2 = _tmp.index(_c1)
                _c1.insert(_c1.index(j), i)
                _c0.insert(_c0.index(i), j)
                _c1.remove(j)
                _c0.remove(i)
                _tmp[idx1] = _c0
                _tmp[idx2] = _c1
                if is_move_allowed((j, i, idx1, idx2), soln, _tmp, 3):
                    neighbours.append((_tmp, get_solution_actual_cost(_tmp), (3, j, i, idx2, idx1, retention)))
                    print_log('exchanging {0} from {1} to {2} from {3} resulting solution {4}'.format(j, soln[idx2], i, soln[idx1], _tmp))

    # print("{0} number of Neighbours after Exchange {1}".format(len(neighbours), neighbours))
    neighbours.sort(key=lambda x: x[1][-1])
    print_log("{0} number of sorted Neighbours after exchange {1}".format(len(neighbours), neighbours))
    return neighbours[0] if len(neighbours) > 0 else -1;


'''
Following function takes solution as input and returns the neighbouring solution by relocating one node from a solution 
in to other solution

returns the all neighbouring solution sorted with cost in ascending order
'''
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
                _c1.remove(j)
                _c0.insert(_c0.index(i) + 1, j)
                _tmp[idx1] = _c0
                _tmp[idx2] = _c1
                if is_move_allowed((j, i, idx1, idx2), soln, _tmp, 1):
                    print_log('relocating {0} from {1} to {2} after {3} resulting solution {4}'.format(j, soln[idx2], soln[idx1], i, _tmp))
                    neighbours.append((_tmp, get_solution_actual_cost(_tmp), (1, j, i, idx2, idx1, retention)))

        for i in combo[1][:-1]:
            for j in combo[0][:-1]:
                if j == 0:
                    continue
                _tmp = copy.deepcopy(soln)
                _c0 = copy.deepcopy(combo[1])
                _c1 = copy.deepcopy(combo[0])
                idx1 = _tmp.index(_c0)
                idx2 = _tmp.index(_c1)
                _c1.remove(j)
                _c0.insert(_c0.index(i) + 1, j)
                _tmp[idx1] = _c0
                _tmp[idx2] = _c1
                if is_move_allowed((j, i, idx1, idx2), soln, _tmp, 1):
                    neighbours.append((_tmp, get_solution_actual_cost(_tmp), (1, j, i, idx2, idx1, retention)))
                    print_log('relocating {0} from {1} to {2} after {3} resulting solution {4}'.format(j, soln[idx2], soln[idx1], i, _tmp))

    # print("{0} number of Neighbours after relocation {1}".format(len(neighbours), neighbours))
    neighbours.sort(key=lambda x: x[1][-1])
    print_log("{0} number of sorted Neighbours after relocation {1}".format(len(neighbours), neighbours))
    return neighbours[0]


'''
Following function takes solution as input and returns the neighbouring solution by shuffling nodes within a route with each other


returns the all neighbouring solution sorted with cost in ascending order
'''
def get_shuffle_neighbours(soln):
    neighbours = []
    for r in soln:
        for i in r[1:-1]:
            for j in r[1:-1]:
                _tmp=copy.deepcopy(soln)
                _r=copy.deepcopy(r)
                idx=_tmp.index(r)
                if i == j:
                    continue
                tmp = j
                idxi=r.index(i)
                _r[r.index(j)]=i
                _r[idxi] = j
                _tmp[idx] = _r
                if is_move_allowed((j, i, idx, idx), soln, _tmp, 2):
                    neighbours.append((_tmp, get_solution_actual_cost(_tmp), (2, j, i, idx, idx, retention)))
                    print_log("changing position of {0} with {1} in route {2} resulting {3}".format(i, j, r, _r))
    neighbours.sort(key=lambda x: x[1][-1])
    print_log("{0} number of sorted Neighbours after shuffling {1}".format(len(neighbours), neighbours))
    return neighbours[0] if len(neighbours)>0 else -1



'''
wrapper for above three functions
'''
def get_neighbours(op, soln):
    if op == 1:
        return get_relocate_neighbour(soln)
    elif op == 2:
        return get_shuffle_neighbours(soln)
    elif op == 3:
        return get_exchange_neighbour(soln)



'''
following function calculate the cost for solution it uses the  get_cost function internally

parameters :
1. soln -- solution

Returns :
1. distance     -- distance
2. delay        -- delay time
3. wait         -- wait time
4. cost         -- cost 
5. serviced     -- number of customers (nodes) services successfully 
6. unserviced   -- number of customers (nodes) not serviced due to delay 
7. details      -- route details for route [(wait time,delay time,service start time)] each () have details for each 
                   customer and each row represents a route 
'''
def get_solution_cost(soln: list):
    cost = 0
    wait = 0
    delay = 0
    serviced = 0
    unserviced = 0
    distance = 0
    details =[]
    for route in soln:
        prev = 0
        prev_sst=0
        details_tmp=[]
        is_delayed = False
        for customer in route[1:]:
            d, w, dl, c, sst, isd=get_cost(prev,customer,prev_sst,is_delayed)
            prev_sst=sst
            is_delayed=isd
            prev=customer
            if isd:
                unserviced += 1
            else:
                serviced += 1
            distance += d
            delay += dl
            wait += w
            cost += c
            details_tmp.append((w,dl,sst))
        details.append(details_tmp)

    return distance, delay, wait, cost,serviced,unserviced,details



'''
following function calculate the cost for solution it uses the  get_cost function internally its same as above but 
returns less parameters

parameters :
1. soln -- solution

Returns :
1. distance     -- distance
2. delay        -- delay time
3. wait         -- wait time
4. cost         -- cost 
'''
def get_solution_actual_cost(soln: list):
    cost = 0
    wait = 0
    delay = 0
    serviced = 0
    unserviced = 0
    distance = 0
    details = []
    for route in soln:
        prev = 0
        prev_sst = 0
        details_tmp = []
        is_delayed = False
        for customer in route[1:]:
            d, w, dl, c, sst, isd = get_cost(prev, customer, prev_sst, is_delayed)
            #c = c + (dl * 39)
            prev_sst = sst
            is_delayed = isd
            prev = customer
            if isd:
                unserviced += 1
            else:
                serviced += 1
            distance += d
            delay += dl
            wait += w
            cost += c
            details_tmp.append((w, dl, sst))
        details.append(details_tmp)

    return distance, delay, wait, cost


'''
Function is to find total distance for solution without pickup/delivery time
'''
def get_distance_for_solution(soln: list):
    d=0
    distance=[]
    for route in soln:
        prev=0
        for customer in route[1:]:
            d += get_distance(prev, customer)
            prev=customer
        distance.append(d)
        d=0
    return distance



'''
Tabu search driver method
'''
def tabu_search(routes: list, itrations):
    best_solution_ever=routes
    best_cost_ever=get_solution_actual_cost(routes)
    best_solution_ever_not_chaned_itr_count = 0
    best_soln = routes
    best_cost = ()
    tmp12=[]
    global tabu_list
    for i in range(itrations - 1):
        tmp12=[]
        if best_solution_ever_not_chaned_itr_count > 7:
            break
        tmp12.append(get_neighbours(1, best_soln))
        tmp12.append(get_neighbours(3, best_soln))
        tmp11=get_neighbours(2, best_soln)
        if not tmp11 == -1:
            tmp12.append(tmp11)
        if tmp12[1] == -1  or tmp12[0] == -1:
            break
        tmp12.sort(key=lambda x: x[1][-1])
        best_soln = tmp12[0][0]
        best_cost = tmp12[0][1]
        tabu_list.append(TabuListClass(tmp12[0][2][0], tmp12[0][2][1:-1], tmp12[0][2][-1]))

        if best_cost_ever[-1] > best_cost[-1]:
            best_cost_ever = best_cost
            best_solution_ever = best_soln
        else:
            best_solution_ever_not_chaned_itr_count +=1
        print("best solution so far {0}".format(best_soln))
        iteration_update_tabu_list()

    return best_solution_ever, best_cost_ever


#------------- input provider methods-----------------------------------------------------------------
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


def read_input_file(filename):
    with open(filename) as f:
        lines = list(f)
        i = 0
        for line in lines[:-3]:
            set_input(i, parse_line_to_list(line))
            i += 1
        set_input(i, int(lines[-3]))
        set_input(i+1, int(lines[-2]))
        set_input(i + 1, int(lines[-1]))

def parse_line_to_list(line):
    ret = []
    str = line[2:-3]
    #print(str)
    for in1 in str.split(']['):
        tmp = []
        for i in in1.split(','):
            if i.isnumeric():
                tmp.append(int(i))
        ret.append(tmp)
    return ret


def set_input(inp, value):
    if inp == 0:
        global distance_mtrx
        distance_mtrx = value
    elif inp == 1:
        global service_time_in
        service_time_in = value
    elif inp == 2:
        global pickup_delivery_time_in
        pickup_delivery_time_in = value
    elif inp == 3:
        global number_of_vehicle
        number_of_vehicle = value
    elif inp == 4:
        global tabu_itrs
        tabu_itrs = value
    elif inp == 5:
        global aspiration
        aspiration = value

#-----------------end ---------input provider methods---------------------------------------------------------

class TabuListClass:
    def __init__(self, op, move, valid_for):
        self.op = op
        self.move = move
        self.valid_for = valid_for

    def checked(self):
        if self.valid_for > 0:
            self.valid_for -= 1
            return self.valid_for
        else:
            return -1

    def find(self, move, aspired, op):
        if self.op == op and self.move == move and self.valid_for > 0 and not aspired:
            print("found tabu match op : {0} move : {1}".format(self.op, self.move))
            return True
        return False


'''
to check current move against tabu list if not available in tabu list then move is allowed otherwise not allowed
function also check for aspiration criteria
'''
def is_move_allowed(move, soln_prev, soln_curr, op):
    if len(tabu_list) < 1:
        return True
    cost_prev = get_solution_actual_cost(soln_prev)[-1]
    cost_curr = get_solution_actual_cost(soln_curr)[-1]
    if cost_prev-cost_curr > aspiration:
        return not contains(tabu_list, lambda x: x.find(move, True, op))
    else:
        return not contains(tabu_list, lambda x: x.find(move, False, op))


'''
to update tabu list iteration wise
'''
def iteration_update_tabu_list():
    for i in tabu_list:
        if i.checked() < 0:
            tabu_list.remove(i)

#utility function to print 2d array linewise rows
def print2D(arr):
    for row in arr:
        print(row)

# log utility method
def print_log(log):
    if logging:
        print(log)

# log = open("myprog.log", "a")
# sys.stdout = log

#read_input_file("vrptw_test_4_nodes.txt")
start_time=perf_counter();
routes = get_initial_solution()
print("Best solution: {0}".format(routes))
#routes.remove([])
best_soln, best_cost = tabu_search(routes, tabu_itrs)
print("solution is : {0} with costs : {1}".format(best_soln, best_cost))
best_cost = get_solution_actual_cost(best_soln)
index1 = 0
for route in best_soln:
    print("Route{0} is: {1}".format(index1, route))
    index1 += 1

distance, delay, wait, cost,serviced,unserviced,details=get_solution_cost(best_soln)
end_time = perf_counter()
print("total distance: {0}".format(distance))
print("total waiting: {0}".format(wait))
print("total delay: {0}".format(delay))
print("total cost: {0}".format(cost))
print("Total serviced customers: {0}".format(serviced - index1))
print("Total unserviced customers: {0}".format(unserviced))
print("route wise Distance without pickup /delivery is {0}".format(get_distance_for_solution(best_soln)))

print("Below is the route details for route [(wait time,delay time,service start time)] each () have details for each "
      "customer and each row represents a route")
print2D(details)
print("total time taken in  seconds is : {0}".format(end_time-start_time))