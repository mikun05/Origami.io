from constraints import get_sector_angle
from edge_fold import bend_around_vertex
from scipy.optimize import minimize
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as R
from vertex_point_optimisation import *
import numpy as np
import torch
import random

def rem_floating_point_errors(flt):
    return torch.where(torch.abs(flt) < 1e-7, torch.tensor(0.0), flt)
    
def tachi_constraints_edge_level_inputted(edge_obj, p_angle):
    """This differs from the other version as it checks the constraints for
    non_uniform inputted angles
    This can not always be uniform all around
    A check (mainly out of curiosity) to see if the resultant folds (non-uniform)
    satisfy the constraints
    """
    
    if not isinstance(p_angle, torch.Tensor):
        p_angle = torch.tensor(p_angle, dtype=torch.float64)
    
    # print('pangle')
    # print('p_angle', p_angle)
    
    sector_angle = get_sector_angle(edge_obj)
    
    if not isinstance(sector_angle, torch.Tensor):
        sector_angle = torch.tensor(get_sector_angle(edge_obj), dtype=torch.float64)
    
    dihedral_angle = p_angle if edge_obj.fold_type == 'V' else (torch.pi * 2) - p_angle

    sin_theta, cos_theta = rem_floating_point_errors(torch.sin(sector_angle)), rem_floating_point_errors(torch.cos(sector_angle))
    sin_rho, cos_rho = rem_floating_point_errors(torch.sin(dihedral_angle)), rem_floating_point_errors(torch.cos(dihedral_angle))
    
    # print('th', sin_theta, cos_theta)
    # print('rh', sin_rho, cos_rho)
    sector_angle_matrix = torch.stack([torch.stack([cos_theta, -sin_theta, torch.tensor(0.0)]),
                                       torch.stack([sin_theta, cos_theta,  torch.tensor(0.0)]),
                                       torch.stack([torch.tensor(0.0),   torch.tensor(0.0),    torch.tensor(1.0)])])

    fold_angle_matrix = torch.stack([torch.stack([torch.tensor(1.0), torch.tensor(0.0),       torch.tensor(0.0)]),
                                     torch.stack([torch.tensor(0.0), cos_rho, -sin_rho]),
                                     torch.stack([torch.tensor(0.0), sin_rho, cos_rho])]) ###tracks gradient
    
    # print(sector_angle_matrix)
    # print(fold_angle_matrix)

    # print('inner tac')
    # print(torch.matmul(sector_angle_matrix, fold_angle_matrix))
    #return torch.matmul(sector_angle_matrix, fold_angle_matrix)
    return sector_angle_matrix @ fold_angle_matrix
    
def tachi_constraints_vertex_level_inputted(vertex_obj, p_angles):
    ident = torch.eye(3, dtype=torch.float64)
    prod = ident.clone()
    # print('anglesss')
    # print(p_angles)
    for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
        prod = torch.matmul(prod, tachi_constraints_edge_level_inputted(edge_obj, p_angles[i]))
   
    #compute frobenius norm of the difference
    closeness_val = torch.norm(prod-ident, p="fro") **2
    
    # print('tac', closeness_val)
    return [prod, closeness_val] #this return a number indicating the closeness of both matrices

def obj_function(angles, vertex_obj, uniform_angle, opt, loop_weight, uniform_weight):
        """
        Objective function checking loop closure constraint, closeness to uniform angle, and relative closeness between angles
        We want to minimise its output later.
        
        If optimiser is the sequential quadratic programming method, 
        we do not need to write the loop_closure_check into the objective function
        """

        if not isinstance(angles, torch.Tensor):
            angles = torch.tensor(angles, dtype=torch.float64, requires_grad=True)
            
        #if not isinstance(uniform_angle, torch.Tensor):
        uniform_angle = torch.tensor(uniform_angle, dtype=torch.float64)
    
        
        loop_closure_check = 0 if opt=="SQP" else tachi_constraints_vertex_level_inputted(vertex_obj, angles)[1] 
        #loop_weight = 1.2 if opt=="LBFGSB" else 0.1 ##loop weight needs to be pretty high to aim that loop closure is satisfied for gradient descent. Otherwise, algorithm priorises satisfying other two constraints
        
        uniform_closeness = (torch.sum(torch.sqrt((angles - uniform_angle) ** 2)))
        
        count = 0
        
        for angle in angles:
            count += (angle - uniform_angle) **2
            
        #uniform_weight = 1
        diff_matrix = diff_matrix = angles.unsqueeze(1) - angles.unsqueeze(0)  # Expands dimensions to (N, N)
        relative_closeness = torch.sum(diff_matrix ** 2)
        
        ##ADD IN CHECK THAT THE ANGLE ALONG THE PLANE OF EACH FACE AT THE VERTEX REMAINS FIXED
        ##This check can also be implemented by checking that the distance the creases around a face are form each other has not changed.
        
        
        # print('loop_closure_check', loop_closure_check)
        # print('uni', uniform_closeness)
        
        return (loop_weight * torch.sqrt(loop_closure_check)) #+ (uniform_weight*torch.sqrt(count))
      
def get_new_angles(vertex_obj):
    new_angles = []
    
    for edge_obj in vertex_obj.surrounding_edges:
        new_angles.append(edge_obj.curve_angle)
    
    return new_angles

def compute_gradient(angles, vertex_obj, uniform_angle, opt, loop_weight, uniform_weight):
        #compute objective function
    angles_tensor = torch.tensor(angles, dtype=torch.float64, requires_grad=True)

    loss = obj_function(angles_tensor, vertex_obj, uniform_angle, opt,  loop_weight, uniform_weight)

    # Compute gradients using autograd
    loss.backward()
    
    return angles_tensor.grad.numpy()

def gradient_descent(vertex_obj, uniform_angle, maxiter=1000):
    """
    This function initially calls gradient_descent_iteration with the actual angles obtained from trying to fold by certain inputted angles
    So when we try to fold by uniform angle 100, the fold function returns an invalid fold of 100+-x1, 100+-x2 and so on.
    It is the latter we call  gradient_descent_iteration with. 
    
    We get back a new set of angles
    We attempt to fold by these also, if the actualy angles obtained do not equal the inputted, 
    we call gradient_descent_iteration again with (not sure yet, could be):
    1. the outputted angles
    2. the angles from the previous iteration
    """
    num_edges = len(vertex_obj.surrounding_edges)
    num_of_iterations = maxiter
    iteration = 1
    
    input_angles = [uniform_angle] * num_edges
    bend_around_vertex(vertex_obj, uniform_angle)
    actual_angles = get_new_angles(vertex_obj)

    # print('iteration', iteration, input_angles)
    # print('iteration', iteration, actual_angles)
        
    while iteration <= num_of_iterations:
        iteration += 1
        
        input_angles = gradient_descent_iteration(vertex_obj, uniform_angle, obj_function, input_angles, 0.1, 3) ##this version uses the actual angles of the previous iteration
        # input_angles = gradient_descent_iteration(vertex_obj, uniform_angle, obj_function, input_angles, 0.0001, 0.0001, 3) ##this version uses the previous iteration's input angles

        start_edge = random.randint(0, len(vertex_obj.surrounding_edges)-1) ##we want to start the refolding process from a random point to spread the offset (otherwise going counter clockwise from edge 0, only 0 and 1 would have the errors)
        bend_around_vertex(vertex_obj, input_angles, start_edge=start_edge)
        actual_angles = get_new_angles(vertex_obj)
        
        
        
        # print('iteration', iteration, input_angles)
        # print('iteration', iteration, actual_angles)
        ##if input angles and actual angles are the same then we terminate immediately
        ##we then check if the vertex loop constraint is satisfied  
    print('!!!COMPUTED fold angles', [ang.item() for ang in get_new_angles(vertex_obj)])
    print('gd done')
    return( [ang.item() for ang in get_new_angles(vertex_obj)])

def gradient_descent_iteration(vertex_obj, uniform_angle, obj_function, angles, learning_rate, stopping_threshold):
    """
    This function takes in:
    -> A set of fold angles around a vertex
    -> Uniform fold angle X
    -> vertex_obj (so we can check the vertex loop closure constraint)
    
    It then, in each iteration, aims to minimise the objective function.
    
    The objective function factors in:
    -> satisfaction of the vertex loop closure constraint
    -> closeness of each angle to the uniform angle X
    -> relative closeness of each angle to all other angles
    
    This function takes care of a single iteration.
    
    It will get called again from another function which checks the results of that iteration againsit another metric
    This will probably be whether the given angles are actually folded by vertex edge folder, or if some other fold (close to but not quite the sepcified angles) occurs
    """
    
        
    gradient = compute_gradient(angles, vertex_obj, uniform_angle, "GD", 0.1, 1)

    # print('HEREE', np.array(angles) - learning_rate * gradient)
    return np.array(angles) - learning_rate * gradient


def obj_function_numpy(angles, vertex_obj, uniform_angle, opt, loop_weight, uniform_weight):
    

    loss = obj_function(angles, vertex_obj, uniform_angle, opt, loop_weight, uniform_weight)
    
    return loss.detach().item()



def l_bfgs_b(vertex_obj, uniform_angle, maxiter=200000, ftol=1e-14, eps=1e-15):
    """
    This function aims to minimize the objective function using second-order approximation
    It should converge faster than simple gradient descent, and handle the constraints baked into the objective function better (though not explicitly)
    Here we use the scipy library 
    Note: sciPy converst everything to numpy
    """

    num_edges = len(vertex_obj.surrounding_edges)
    
    # bend_around_vertex(vertex_obj, uniform_angle)
    # initial_bend = get_new_angles(vertex_obj)
    # input_angles = np.array(initial_bend.copy())
    # # input_angles_tensor = torch.tensor(input_angles, dtype=torch.float64, requires_grad=True)
    # print('!!!COMPUTED fold angles', [ang.item() for ang in get_new_angles(vertex_obj)])

    input_angles = [uniform_angle] * num_edges
    
    
    
    new_angles = l_bfgs_b_helper(vertex_obj, uniform_angle, input_angles, 3.43, 0, maxiter, ftol, eps)
    print(new_angles)
    ##seems to solve for angles properly ... intended angles are good.
    ##what is visually folded differs drastically
    
    #bend_around_vertex(vertex_obj, np.array(new_angles.x, dtype=np.float64))
    
    #vertex_slsq(vertex_obj, np.array(new_angles.x, dtype=np.float64))
    return new_angles.x
    print('Intended Fold Angles @ src', new_angles.x)
    print(new_angles.x)
    print('!!!COMPUTED fold angles', [ang.item() for ang in get_new_angles(vertex_obj)])


    
    
    


def l_bfgs_b_helper(vertex_obj, uniform_angle, initial_angles, loop_weight, uniform_weight, maxiter, ftol, eps):
    new_angles = minimize(obj_function_numpy, 
                         initial_angles, 
                         (vertex_obj, uniform_angle, 'LBFGSB', loop_weight, uniform_weight),
                         method="L-BFGS-B", 
                         jac=compute_gradient,
                         bounds=None,
                         options={
                                    'maxiter': maxiter,
                                    'disp': True,
                                    'gtol': 1e-12,
                                    'ftol': ftol,
                                    'maxfun': 100000,
                                    'eps': eps
                                })
    
    return new_angles


def re_l_bfgs_b(vertex_obj, uniform_angle):
    num_edges = len(vertex_obj.surrounding_edges)

    input_angles = [uniform_angle] * num_edges
    
    intended_angles = l_bfgs_b_helper(vertex_obj, uniform_angle,input_angles, 3.43, 0).x
    bend_around_vertex(vertex_obj, np.array(intended_angles, dtype=np.float64))

    computed_angles = [ang.item() for ang in get_new_angles(vertex_obj)]
    
    iterations = 5
    
    while iterations > 0 and not(np.allclose(intended_angles, computed_angles)):
        print('it', iterations)
        print('$$$INTENDED', intended_angles)
        print('$$$COMPUTED', computed_angles)
        residual = 0
        for i in range(num_edges):
            residual += computed_angles[i] - intended_angles[i]
        
        res_for_each = residual / num_edges
        input_angles = [intended_angle + res_for_each for intended_angle in intended_angles]
        
        intended_angles = l_bfgs_b_helper(vertex_obj, uniform_angle, input_angles, 3.43, 0).x
        bend_around_vertex(vertex_obj, np.array(intended_angles, dtype=np.float64))
        computed_angles = [ang.item() for ang in get_new_angles(vertex_obj)]
        
        iterations -= 1
    
    return intended_angles

        

    
    
    
def annealing_optimiser(vertex_obj, uniform_angle, maxiter=200000, ftol=1e-14, eps=1e-15):
    new_angles = annealing_optimiser_helper(vertex_obj, uniform_angle, 0.1, 1, maxiter, ftol, eps) #based on graphs loop weight 5 works best for positive annealing
    print(new_angles)
    ##seems to solve for angles properly ... intended angles are good.
    ##what is visually folded differs drastically
    return new_angles.x
    #bend_around_vertex(vertex_obj, new_angles.x)
    print('Intended Fold Angles @ src', new_angles.x)
    print(new_angles.x)
    print('!!!COMPUTED fold angles', [ang.item() for ang in get_new_angles(vertex_obj)])
    


def annealing_optimiser_helper(vertex_obj, uniform_angle, loop_weight, uniform_weight, maxiter, ftol, eps):
    num_edges = len(vertex_obj.surrounding_edges)
    initial_angles = np.array([0.0] * num_edges)
    step_deg = 1
    step_rad = np.deg2rad(step_deg)  

    start_angle = np.deg2rad(step_deg)
    end_angle = uniform_angle  # already in radians
    
    new_angles = l_bfgs_b_helper(vertex_obj, 0.0, initial_angles, loop_weight, uniform_weight, maxiter, ftol, eps)
    # new_angles = minimize(obj_function_numpy, 
    #                      initial_angles, 
    #                      (vertex_obj, 0.0, 'LBFGSB'),
    #                      method="L-BFGS-B", 
    #                      jac=compute_gradient,
    #                      bounds=None,
    #                      options={
    #                                 'maxiter': 20000,
    #                                 'disp': True,
    #                                 'gtol': 1e-12,
    #                                 'ftol': 1e-14,
    #                                 'maxfun': 100000,
    #                                 'eps': 1e-10
    #                             })
  
    
    for angle in np.arange(start_angle, end_angle + 1e-8, step_rad):
        #print('inm', angle)
        new_angles = l_bfgs_b_helper(vertex_obj, angle, new_angles.x,  loop_weight, uniform_weight, maxiter, ftol, eps)

        # new_angles = minimize(obj_function_numpy, 
        #                  new_angles.x, 
        #                  (vertex_obj, angle, 'LBFGSB'),
        #                  method="L-BFGS-B", 
        #                  jac=compute_gradient,
        #                  bounds=None,
        #                  options={
        #                             'maxiter': 20000,
        #                             'disp': True,
        #                             'gtol': 1e-12,
        #                             'ftol': 1e-14,
        #                             'maxfun': 100000,
        #                             'eps': 1e-10
        #                         })
    
    return new_angles
    
def annealing_optimiser_dec(vertex_obj, uniform_angle,maxiter=200000, ftol=1e-14, eps=1e-15):
    new_angles = annealing_optimiser_dec_helper(vertex_obj, uniform_angle, 1.2, 1, maxiter, ftol, eps)
    print(new_angles)
    ##seems to solve for angles properly ... intended angles are good.
    ##what is visually folded differs drastically
    return new_angles.x
    #bend_around_vertex(vertex_obj, new_angles.x)
    print('Intended Fold Angles @ src', new_angles.x)
    print(new_angles.x)
    print('!!!COMPUTED fold angles', [ang.item() for ang in get_new_angles(vertex_obj)])
    
def annealing_optimiser_dec_helper(vertex_obj, uniform_angle, loop_weight, uniform_weight, maxiter, ftol, eps):
    num_edges = len(vertex_obj.surrounding_edges)
    initial_angles = np.array([np.deg2rad(180)] * num_edges)
    step_deg = 1
    step_rad = np.deg2rad(step_deg)  

    start_angle = np.deg2rad(180)
    end_angle = uniform_angle  # already in radians
    
    new_angles = l_bfgs_b_helper(vertex_obj, np.deg2rad(180), initial_angles, loop_weight, uniform_weight, maxiter, ftol, eps)

    
    # new_angles = minimize(obj_function_numpy, 
    #                      initial_angles, 
    #                      (vertex_obj, np.deg2rad(180), 'LBFGSB'),
    #                      method="L-BFGS-B", 
    #                      jac=compute_gradient,
    #                      bounds=None,
    #                      options={
    #                                 'maxiter': 20000,
    #                                 'disp': True,
    #                                 'gtol': 1e-12,
    #                                 'ftol': 1e-14,
    #                                 'maxfun': 100000,
    #                                 'eps': 1e-10
    #                             })
  
    
    for angle in np.arange(start_angle, end_angle - 1e-8, -step_rad):
        #print('inm', angle)
        new_angles = l_bfgs_b_helper(vertex_obj, angle, new_angles.x,  loop_weight, uniform_weight, maxiter, ftol, eps)

        # new_angles = minimize(obj_function_numpy, 
        #                  new_angles.x, 
        #                  (vertex_obj, angle, 'LBFGSB'),
        #                  method="L-BFGS-B", 
        #                  jac=compute_gradient,
        #                  bounds=None,
        #                  options={
        #                             'maxiter': 20000,
        #                             'disp': True,
        #                             'gtol': 1e-12,
        #                             'ftol': 1e-14,
        #                             'maxfun': 100000,
        #                             'eps': 1e-10
        #                         })
    return(new_angles)
    # print(new_angles)
    
    # ##seems to solve for angles properly ... intended angles are good.
    # ##what is visually folded differs drastically
    # bend_around_vertex(vertex_obj, new_angles.x)
    # print('Intended Fold Angles @ src', new_angles.x)
    # print(new_angles.x)
    # print('!!!COMPUTED fold angles', [ang.item() for ang in get_new_angles(vertex_obj)])
    
    
def objective_uniformity(angles, uniform_angle):
    count = 0
        
    for angle in angles:
        count += (angle - uniform_angle) **2
    
    return count

def objective_uniformity_mean(angles, uniform_angle):
    count = 0
    
    # print(angles)
    for angle in angles:
        count += angle
    return np.sqrt((count / len(angles) - uniform_angle) ** 2)

def ssd_objective_angles(angles, uniform_angle, n, main_vertex_start_index):
    ssd = 0
    for angle in angles[main_vertex_start_index: main_vertex_start_index+n]:
        ssd += (angle - uniform_angle) ** 2
        
    return ssd

    
    
def jac_combined(p_angles, vertex_obj, uniform_angle):
    return ([1/len(p_angles) + 1] * len(p_angles))

def jac_mean(angles, uniform_angles):
    return ([1/len(angles)] * len(angles))

def jac(angles, uniform_angles):
    return ([2]* len(angles))
    
def loop_closure_constraint(p_angles, vertex_obj):
    ident = torch.eye(3, dtype=torch.float64)
    prod = ident.clone()
    # print('anglesss')
    # print(p_angles)
    for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
        prod = torch.matmul(prod, tachi_constraints_edge_level_inputted(edge_obj, p_angles[i]))
   
    #compute frobenius norm of the difference
    return np.sqrt(torch.norm(prod - ident, p="fro").item() ** 2)



def angles_rotatable(p_angles, vertex_obj):
    bend_around_vertex(vertex_obj, p_angles)
    computed_angles = [ang.item() for ang in get_new_angles(vertex_obj)]
    
    n = len(p_angles)
    diff = 0
    
    for i in range(0,n):
        diff += np.absolute(p_angles[i] - computed_angles[i])
    
    return diff

def combined_obj(p_angles, vertex_obj, uniform_angle):
    return angles_rotatable(p_angles, vertex_obj) + objective_uniformity_mean(p_angles, uniform_angle)


def sector_angle_constraint(vertex_obj):
    pass

def norm_compute_transformations(vertex_index, vertices, edge_start_index, angles, start_edge):
    """
    Sequential folding is almost.
    But the start edge has the wrong dihedral angle due to interference from folding the last edge.
    Due to this, 
    even when we have a valid fold configuration from gradient_descent or lbfgs,
    we can not visualise the fold configuration, we can instead only simulate one which is close except for two angles
    """
    vertex_obj = vertices[vertex_index]
    surrounding_faces = vertex_obj.surrounding_faces
    n = len(surrounding_faces)
    
    
    
    # print('angles', angles)
    # print('vertex_inds', vertex_index)
    # print('vertex_inds', vertex_index)

    
    angle = angles[edge_start_index: edge_start_index+n]
    # print('angle', angle)
    # print('vertex_obj.surrounding_edges', n)
    # print(angle)
    transforms = {} #these are transformations as applied to faces, since sym is 0.5, I need to consider the edge that affects this face as its right face, and the other that does so as its left face
    #transforms[start_edge] = np.eye(3)  #face 0 remains unrotated.
    # print('!!!INTENDED fold angles', angle)
    transforms[start_edge] = np.eye(3) 
    right_edge_obj = vertex_obj.surrounding_edges[start_edge]
    fold_angle = angle[start_edge] if isinstance(angle,(list, tuple, np.ndarray)) else angle
    ang = fold_angle + np.pi if  right_edge_obj.fold_type == "V" else np.pi - fold_angle
    prod = rodrigues_rotation_matrix(right_edge_obj, ang)
    for i_count in range(1,n):
        i = (start_edge + i_count) % (n)
        right_edge_obj = vertex_obj.surrounding_edges[i]

        fold_angle = angle[i] if isinstance(angle,(list, tuple, np.ndarray)) else angle
        ang = fold_angle + np.pi if  right_edge_obj.fold_type == "V" else np.pi - fold_angle

        R = rodrigues_rotation_matrix(right_edge_obj, ang)
        
        
        prod = prod @ R
    # print(prod)
    # print('norm', np.linalg.matrix_norm(np.eye(3) - prod))
    return [prod, np.linalg.matrix_norm(np.eye(3) - prod)]



def constraints_on_other_angles(vertex_index, vertex_objs):
    adds = 0
    
    for vertex_obj in vertex_objs:
        for edge_obj in vertex_obj.surrounding_edges:
            edge_obj.curve_angle 
    

def slsq(vertex_index, vertices, edge_start_dict, uniform_angle, maxiter, ftol, eps, obj_fn=ssd_objective_angles, hasJac=False):
    vertex_obj = vertices[vertex_index]
    num_edges = len(vertex_obj.surrounding_edges)
    print('numb', num_edges)
  
        
        
    if len(vertices) > 1:
        pass
    
    constraints = [{
    'type': 'eq',
    'fun': lambda h: norm_compute_transformations(vertex_index, vertices, edge_start_dict[vertex_index], h, 0)[1]
    }]
    
    
    
    ##Constraints:
    ####-> keep angles of other vertices as fixed as possible but valid around the vertices also. 
    
    
    
    ##Since Uniform angles already staisfy the objective function, input the failed rotation t uniform folds as x_0 of the optimisation process
   # bend_around_vertex(vertex_obj, [uniform_angle]*num_edges)
    print('prestart', uniform_angle)

    start_angles = [uniform_angle] * num_edges#[ang.item() for ang in get_new_angles(vertex_obj)]
    new_start_angles = []
    
    for (i, vertex) in enumerate(vertices):
        if not (vertex.isBoundary): 
            for edge in vertex.surrounding_edges: 
                new_start_angles.append(uniform_angle if i == vertex_index else edge.curve_angle)
        
    print('start', new_start_angles)
    new_angles = minimize(
        obj_fn,  # your objective function
        new_start_angles,
        (uniform_angle, num_edges, edge_start_dict[vertex_index]),
        method='SLSQP',
        jac= jac_mean if hasJac else None,
        constraints=constraints,
        bounds=[(np.deg2rad(0), np.deg2rad(180))] * len(new_start_angles),
        options={
                    'maxiter': maxiter,
                    'disp': True,
                    'ftol': ftol,
                    'eps': eps
                }
        )
    
    # print(new_angles)
    ##seems to solve for angles properly ... intended angles are good.
    ##what is visually folded differs drastically
    
    print('mews', new_angles.x)
    return new_angles.x

def constraint_single_edge(angles,  main_vertex_start_index, pre_fold_angles, index, angle):
    """We want to minimise deviations of untouched angles, but get rotated angle to specified new angle
    """
    ssd = 0
    # print('wuttt angles', len(angles))
    
    for i in range(len(angles)):
        if i != main_vertex_start_index + index:
            ssd += (angles[i] - pre_fold_angles[i]) ** 2
        else:
            print('nonconstraint', i)
            
    return ssd

def objective_fold_to_edge_angle(angles, main_vertex_start_index, index, angle):
    print('fol', angles[main_vertex_start_index+index], angle)
    return (angles[main_vertex_start_index+index] - angle)**2
            
    

def slsq_specific_edge(vertices, vertex_index, angle, index, maxiter=200, ftol=1e-14, eps=1e-15):
    results = {}
    edge_start_dict = {}
    current_angles = []

    pos = 0
    for (i, vert) in enumerate(vertices):        
        if not vert.isBoundary:
            edge_start_dict[i] = pos
            pos += len(vert.surrounding_edges)
            current_angles += [ang.item() for ang in get_new_angles(vert)]  

        
    
            
    # current_angles = [ang.item() for ang in get_new_angles(vertex_obj)]
    
    constraints = [{
    'type': 'eq',
    'fun': lambda h: norm_compute_transformations(vertex_index, vertices, edge_start_dict[vertex_index], h, 0)[1]
    }, {
    'type': 'ineq',
    'fun': lambda h: constraint_single_edge(h,  edge_start_dict[vertex_index], current_angles, index, angle)
    }]
    
    ##Since Uniform angles already staisfy the objective function, input the failed rotation t uniform folds as x_0 of the optimisation process
    current_angles[edge_start_dict[vertex_index]+index] = float(angle)
    vertex_points = bend_around_vertex(vertices, vertex_index, edge_start_dict, current_angles)
    #start_angles = [ang.item() for ang in get_new_angles(vertex_obj)]
    start_angles = []
    for vert in vertices:
        if not (vert.isBoundary):
            start_angles += [ang.item() for ang in get_new_angles(vert)]  
            
    print('START', start_angles)
    print(start_angles)
    
    new_angles = minimize(
        objective_fold_to_edge_angle,  # your objective function
        start_angles,
        (edge_start_dict[vertex_index], index, angle),
        method='SLSQP',
        # jac=jac_mean,
        constraints=constraints,
        bounds=[(np.deg2rad(0), np.deg2rad(180))] * len(start_angles),
        options={
                    'maxiter': maxiter,
                    'disp': True,
                    'ftol': ftol,
                    'eps': eps
                }
        )
    
    print('ff', new_angles) #vertex_index, vertices, main_vertex_indices, h, 0
    print('norm diff 2', norm_compute_transformations(vertex_index, vertices, edge_start_dict[vertex_index],new_angles.x, 0)[1])
    ##seems to solve for angles properly ... intended angles are good.
    ##what is visually folded differs drastically
    
    vertex_points = bend_around_vertex(vertices, vertex_index, edge_start_dict, new_angles.x)
    
    new_angles = []
    for vert in vertices:
        if not (vert.isBoundary):
            new_angles += [ang.item() for ang in get_new_angles(vert)]
    
    results['angle_approx_loop_closure'] = f"{float(norm_compute_transformations(vertex_index, vertices, edge_start_dict[vertex_index], new_angles, 0)[1]):.{8}g}"
    results['angle_approx_loop_closure_matrix'] = [[f"{float(item):.{3}g}" for item in row] for row in norm_compute_transformations(vertex_index, vertices, edge_start_dict[vertex_index], new_angles, 0)[0].tolist()]

    results['vertex_approx_new_angles'] = new_angles
    results['dist_from_angle_results'] =     f"{float(vertex_points['mean']):.{8}g}"
    results['total_edge_deviation'] =     f"{float(vertex_points['obj_length']):.{8}g}"
    results['total_sector_angle_deviation'] =     f"{float(vertex_points['sec_size']):.{8}g}"

    
    return results

    