import numpy as np
from angle_optimisation import *
from smooth_fold_gens import *
import matplotlib.pyplot as plt

angles_in_deg = np.arange(0,180+5, 5)

#LBFGS
residuals_uniform_start = [] ##holds the frobeius norm difference for x_0 = uniform
residuals_neg_anneal = []  ##holds the frobeius norm difference for starting from 180, and folding downwards
residuals_pos_anneal = [] ##holds the frobeius norm difference for starting from 0, and folding upwards

water_bomb_base_fold_data = {
            "vertices_coords": [
                [-10, 10, 0], [10, 10, 0], [10, 0, 0], [10, -10, 0], [-10, -10, 0], [-10, 0, 0], [0, 0, 0]
            ],
            "edges_vertices": [
                [0, 1], [0, 6], [1, 6], [0, 5], [1,2], [5,6], [6,2], [5,4], [6,4], [6,3], [2,3], [4,3]
            ],
            "faces_vertices": [
                [6,1,0], [6,2,1], [6,3,2], [6,4,3], [6,5,4], [6,0,5]
            ],
            "edges_assignment": [
                "B", "V", "V", "B", "B", "M", "M", "B", "V", "V", "B", "B",
            ]
        }

example_fold_data = water_bomb_base_fold_data
pattern = SmoothFoldPattern(example_fold_data)

vertex_obj = pattern.vertex_objects[6] ##make this the 6th  vertex of waterbomb base for testing
num_edges = len(vertex_obj.surrounding_edges)

# for angle_deg in angles_in_deg:
#     angle_rad = np.deg2rad(angle_deg)
    
#     angle_results = l_bfgs_b_helper(vertex_obj, angle_rad, [angle_rad] * num_edges, 1.2, 1)
#     dist_from_identity = tachi_constraints_vertex_level_inputted(vertex_obj, angle_results.x)
#     residuals_uniform_start.append(dist_from_identity)
    
#     angle_results = annealing_optimiser_helper(vertex_obj, angle_rad, 1.2, 1)
#     dist_from_identity = tachi_constraints_vertex_level_inputted(vertex_obj, angle_results.x)
#     residuals_pos_anneal.append(dist_from_identity)
    
#     angle_results = annealing_optimiser_dec_helper(vertex_obj, angle_rad, 1.2, 1)
#     dist_from_identity = tachi_constraints_vertex_level_inputted(vertex_obj, angle_results.x)
#     residuals_neg_anneal.append(dist_from_identity)



# ##plot anneal vs uniform start
# plt.figure(figsize=(10, 6))
# plt.plot(angles_in_deg, residuals_uniform_start, label='Uniform Start L-BFGS', marker='o')
# plt.plot(angles_in_deg, residuals_pos_anneal, label='Positive Annealed L-BFGS', marker='s')
# plt.plot(angles_in_deg, residuals_neg_anneal, label='Negative Annealed L-BFGS', marker='x')

# plt.xlabel('Target Uniform Fold Angle (degrees)')
# plt.ylabel('Loop Closure Residual (Frobenius Norm)')
# plt.title('Loop Closure vs Fold Angle: Positive Annealing vs Negative Annealing vs Uniform Start')
# plt.legend()
# plt.grid(True)
# plt.show()

############################### NEW GRAPH 

# test_angles = np.arange(0,180+1, 45)
# loop_weights = [0.1, 0.5, 1.0, 2.0, 5.0]
# uniform_weight = 1 #fix to 1 for test   
# res = {}

# for loop_weight in loop_weights:
#     print('loop weight', loop_weight)
#     residual = []
#     for angle_deg in test_angles:
#         angle_rad = np.deg2rad(angle_deg)
        
#         angle_results = l_bfgs_b_helper(vertex_obj, angle_rad, [angle_rad] * num_edges, loop_weight, uniform_weight)
#         #dist_from_identity = tachi_constraints_vertex_level_inputted(vertex_obj, angle_results.x) #check against dist to I for loop closure only
#         obj_func_res = angle_results.fun#obj_function_numpy(angle_results.x, vertex_obj, angle_deg, 'LBFGS', loop_weight, uniform_weight)
#         residual.append(obj_func_res)
        
#     res[f"{loop_weight:.2f}"] = residual
#     print(res)
    
# for loop_weight, residuals in res.items():
#     print(loop_weight)
#     plt.plot(test_angles, residuals, label=f'Loop weight: {loop_weight}', marker='o')

# plt.xlabel('Target Uniform Fold Angle (degrees)')
# plt.ylabel('Objective Function Result') ##Aim is for this to be as close as posible to 0 but only exactly 0 for angle = 0, 180
# # plt.ylabel('Loop Closure Residual (Frobenius Norm)')
# plt.title('Effect of Loop Closure Weight on Uniform Start Performance')
# plt.legend()
# plt.grid(True)
# plt.show()


############################### NEW GRAPH 


# num_iterations = 10
# loop_weight = 2
# angle_deg = 100
# uniform_closeness = np.inf
# residual = {}
# uniform_weight = 0


# while num_iterations > 0:
#     print('iteration:', num_iterations)
#     print('loop_weight', loop_weight)
#     angle_rad = np.deg2rad(angle_deg)
    
#     angle_results = l_bfgs_b_helper(vertex_obj, angle_rad, [angle_rad] * num_edges, loop_weight, uniform_weight)
#     dist_from_identity = np.sqrt(tachi_constraints_vertex_level_inputted(vertex_obj, angle_results.x)[1]) #check against dist to I for loop closure only
    
#     count = 0
#     for angle in angle_results.x:
#         count += (angle - angle_rad) **2
            
#     curr_uniformity = (np.sqrt(count))
#     # residual.append(curr_uniformity)
        
#     residual[loop_weight] = [dist_from_identity, curr_uniformity/ 1e-7]
    
    
#     if curr_uniformity < uniform_closeness:
#         uniform_closeness = curr_uniformity
#         loop_weight -= loop_weight/2
#     else:
#         loop_weight += loop_weight/2
    
#     num_iterations -= 1
    
    
# for loop_weight, item in residual.items():
#     print(loop_weight)

#     #plt.plot(loop_weight, item[0], marker='o')
#     plt.plot(loop_weight, item[0], marker='x')

    
# plt.xlabel('Loop Weight Binary Search')
# plt.ylabel('Overall Closeness to Satisfying Vertex Loop Closure') ##Aim is for this to be as close as posible to 0 but only exactly 0 for angle = 0, 180
# # plt.ylabel('Loop Closure Residual (Frobenius Norm)')
# plt.title('Variable Loop Weight for Uniform Fold at 90 deg (Uniform Weight = 0)')
# plt.legend()
# plt.grid(True)
# plt.show()


##################################
##Graph SLQP with varying ftol and fix max iterations.
##Graph against number of iterations before termination and frobenius difference

mean_frob_diff = []
ssd_frob_diff = []
angles = [uniform_angle for uniform_angle in range(0,180)]

for angle in angles:
    uniform_angle = np.deg2rad(angle)
    print('at', uniform_angle)

    angle_results_obj_mean = slsq(vertex_obj, uniform_angle, maxiter=200, ftol=1e-10, eps=1e-14)
    # frob_diff = norm_compute_transformations(vertex_obj, angle_results_obj_mean, 0)[1]
    mean_mean = ((np.sum(angle_results_obj_mean) / len(angle_results_obj_mean)) - uniform_angle) ** 2
    mean_frob_diff.append(mean_mean)
    
    angle_results_obj_ssd = slsq(vertex_obj, uniform_angle, maxiter=200, ftol=1e-10, eps=1e-14, obj_fn=ssd_objective_angles, hasJac=False)
    #frob_diff_ssd = norm_compute_transformations(vertex_obj, angle_results_obj_ssd, 0)[1]
    ssd_mean = ((np.sum(angle_results_obj_ssd) / len(angle_results_obj_ssd)) - uniform_angle) ** 2
    ssd_frob_diff.append(ssd_mean)    



    
fig, ax = plt.subplots()

 
    
#plt.plot(loop_weight, item[0], marker='o')
ax.plot(angles, ssd_frob_diff, linewidth=1, label="Sum of Squared Differences")
ax.plot(angles, mean_frob_diff, linewidth=1, label="Mean")


    
plt.xlabel('Uniform Angles')
plt.ylabel('Mean') ##Aim is for this to be as close as posible to 0 but only exactly 0 for angle = 0, 180
# plt.ylabel('Loop Closure Residual (Frobenius Norm)')
plt.title('Comparing Objective Functions. Mean vs Sum of Squared Differences')
plt.legend()
plt.grid(True)
plt.show()
