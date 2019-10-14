Files-
    greedy_tabu_search.py
        - this is source code
    vrptw_test.txt, vrptw_test_4_nodes.txt
        - This is Input file
        - first line contains distance matrix
        - second line contains early/latest service time
        - third line contains pickup/delivery times
        - fourth line will be single number = number of vehicles
        - fifth line will be max number of iterations for tabu search will be used in stoping criteria for tabu
        - Sixth line tell the mangnitude of improvement of cost for aspiration criteria

Terms :
    - soln(solution or routes) : is as list of routes
    - route                    : is a list of customers
    - src                      : source customer
    - dest                     : destination customer

Source file Functions and global variables :
tabu_list                   : tabu list used in tabu search algo
get_heuristic               : function to return cost from heuristic used during greedy
generate__initial_solution  : function implementing greedy heuristic Dijkstra like algorithm to find initial solution to be used in tabu search
is_servisable               : Utility function to find if customer can be serviced with current route or not i.e. no delay
get_delay                   : utility function to find delay which will happen by current route
get_exchange_neighbour      : function to get neighbours of solution using exchange operator
get_relocate_neighbour      : function to get neighbours of solution using relocate operator
get_neighbours              : function wrapping above 2 functions
get_solution_cost           : function to calculate cost for any solution
tabu_search                 : function for tabu search
get_distance                : function to get input distance b/t src and dest
get_pickup_time             : function to get input pickup time at customer
get_delivery_time           : function to get input delivery time at customer
get_earliest_service_time   : function to get input earliest service time at customer
get_latest_service_time     : function to get input latest service time at customer
get_service_start_time      : function to get input delivery time at customer
is_empty_route              : function to check if route is empty i.e. having only start depot and end depot
contains                    : function to check existence with filtering
read_input_file             : function to read input from file
parse_line_to_list          : helper for input reading
set_input                   : function for setting input from file
is_move_allowed             : function to chk the current move against tabu_list
iteration_update_tabu_list  : functions used to update tabu_list per iteration


Class :

TabuListClass : class representing one entry in tabu list
    -function checked use to decrement tabu move iteration count per iteration i.e. for how many more iterations move will be considered tabu
    -function find is used to find if current move is tabu of not
