from constraints import get_sector_angle
from edge_fold import bend_around_vertex
from scipy.optimize import minimize
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
        p_angle = torch.tensor(p_angle, dtype=torch.float32)
    
    print('pangle')
    print('p_angle', p_angle)
    
    sector_angle = get_sector_angle(edge_obj)
    
    if not isinstance(sector_angle, torch.Tensor):
        sector_angle = torch.tensor(get_sector_angle(edge_obj), dtype=torch.float32)
    
    dihedral_angle = p_angle if edge_obj.fold_type == 'V' else (torch.pi * 2) - p_angle

    sin_theta, cos_theta = rem_floating_point_errors(torch.sin(sector_angle)), rem_floating_point_errors(torch.cos(sector_angle))
    sin_rho, cos_rho = rem_floating_point_errors(torch.sin(dihedral_angle)), rem_floating_point_errors(torch.cos(dihedral_angle))
    
    print('th', sin_theta, cos_theta)
    print('rh', sin_rho, cos_rho)
    sector_angle_matrix = torch.stack([torch.stack([cos_theta, -sin_theta, torch.tensor(0.0)]),
                                       torch.stack([sin_theta, cos_theta,  torch.tensor(0.0)]),
                                       torch.stack([torch.tensor(0.0),   torch.tensor(0.0),    torch.tensor(1.0)])])

    fold_angle_matrix = torch.stack([torch.stack([torch.tensor(1.0), torch.tensor(0.0),       torch.tensor(0.0)]),
                                     torch.stack([torch.tensor(0.0), cos_rho, -sin_rho]),
                                     torch.stack([torch.tensor(0.0), sin_rho, cos_rho])]) ###tracks gradient
    
    print(sector_angle_matrix)
    print(fold_angle_matrix)

    print('inner tac')
    print(torch.matmul(sector_angle_matrix, fold_angle_matrix))
    return torch.matmul(sector_angle_matrix, fold_angle_matrix)
    
def tachi_constraints_vertex_level_inputted(vertex_obj, p_angles):
    ident = torch.eye(3, dtype=torch.float32)
    prod = ident.clone()
    print('anglesss')
    print(p_angles)
    for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
        prod = torch.matmul(prod, tachi_constraints_edge_level_inputted(edge_obj, p_angles[i]))
   
    #compute frobenius norm of the difference
    closeness_val = torch.norm(prod-ident, p="fro")
    
    print('tac', closeness_val)
    return closeness_val #this return a number indicating the closeness of both matrices


def obj_function(angles, vertex_obj, uniform_angle, opt):
        """
        Objective function checking loop closure constraint, closeness to uniform angle, and relative closeness between angles
        We want to minimise its output later.
        
        If optimiser is the sequential quadratic programming method, 
        we do not need to write the loop_closure_check into the objective function
        """
        print('2.angles', angles)

        if not isinstance(angles, torch.Tensor):
            angles = torch.tensor(angles, dtype=torch.float32, requires_grad=True)
            
        if not isinstance(uniform_angle, torch.Tensor):
            uniform_angle = torch.tensor(uniform_angle, dtype=torch.float32)
    
        print('3.angles', angles)
        
        loop_closure_check = 0 if opt=="SQP" else tachi_constraints_vertex_level_inputted(vertex_obj, angles) 
        loop_weight = 1.2 if opt=="LBFGSB" else 0.1 ##loop weight needs to be pretty high to aim that loop closure is satisfied for gradient descent. Otherwise, algorithm priorises satisfying other two constraints
        
        uniform_closeness = torch.sum((angles - uniform_angle) ** 2)
        uniform_weight = 1
        diff_matrix = diff_matrix = angles.unsqueeze(1) - angles.unsqueeze(0)  # Expands dimensions to (N, N)
        relative_closeness = torch.sum(diff_matrix ** 2)
        
        print('loop_closure_check', loop_closure_check)
        print('uni', uniform_closeness)
        
        return ((loop_weight*loop_closure_check) + (uniform_weight*uniform_closeness))
    

    

def get_new_angles(vertex_obj):
    new_angles = []
    
    for edge_obj in vertex_obj.surrounding_edges:
        new_angles.append(edge_obj.curve_angle)
    
    print('0.angle', new_angles)
    return new_angles

def compute_gradient(angles, vertex_obj, uniform_angle, opt):
        #compute objective function
    angles_tensor = torch.tensor(angles, dtype=torch.float32, requires_grad=True)

    loss = obj_function(angles_tensor, vertex_obj, uniform_angle, opt)

    # Compute gradients using autograd
    loss.backward()
    
    return angles_tensor.grad.numpy()

def gradient_descent(vertex_obj, uniform_angle):
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
    num_of_iterations = 50
    iteration = 1
    
    input_angles = [uniform_angle] * num_edges
    bend_around_vertex(vertex_obj, uniform_angle)
    actual_angles = get_new_angles(vertex_obj)

    # print('iteration', iteration, input_angles)
    # print('iteration', iteration, actual_angles)
        
    while iteration <= num_of_iterations:
        iteration += 1
        
        input_angles = gradient_descent_iteration(vertex_obj, uniform_angle, obj_function, actual_angles, 0.1, 3) ##this version uses the actual angles of the previous iteration
        # input_angles = gradient_descent_iteration(vertex_obj, uniform_angle, obj_function, input_angles, 0.0001, 0.0001, 3) ##this version uses the previous iteration's input angles

        start_edge = random.randint(0, len(vertex_obj.surrounding_edges)-1) ##we want to start the refolding process from a random point to spread the offset (otherwise going counter clockwise from edge 0, only 0 and 1 would have the errors)
        bend_around_vertex(vertex_obj, input_angles, start_edge=start_edge)
        actual_angles = get_new_angles(vertex_obj)
        
        # print('iteration', iteration, input_angles)
        # print('iteration', iteration, actual_angles)
        ##if input angles and actual angles are the same then we terminate immediately
        ##we then check if the vertex loop constraint is satisfied  
    
    print('done')

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
    
        
    gradient = compute_gradient(angles, vertex_obj, uniform_angle, opt="GD")

    print('HEREE', np.array(angles) - learning_rate * gradient)
    return np.array(angles) - learning_rate * gradient


def obj_function_numpy(angles, vertex_obj, uniform_angle, opt):
    print('1.angles', angles)
    

    loss = obj_function(angles, vertex_obj, uniform_angle, opt)
    
    print('loss', loss)
    return loss.detach().item()



def l_bfgs_b(vertex_obj, uniform_angle):
    """
    This function aims to minimize the objective function using second-order approximation
    It should converge faster than simple gradient descent, and handle the constraints baked into the objective function better (though not explicitly)
    Here we use the scipy library 
    Note: sciPy converst everything to numpy
    """

    num_edges = len(vertex_obj.surrounding_edges)
    
    bend_around_vertex(vertex_obj, uniform_angle)
    initial_bend = get_new_angles(vertex_obj)
    input_angles = np.array(initial_bend.copy())
    # input_angles_tensor = torch.tensor(input_angles, dtype=torch.float32, requires_grad=True)


    
    
    print('hhh')  
    
    l_bfgs_b_helper(vertex_obj, uniform_angle, input_angles)
    


def l_bfgs_b_helper(vertex_obj, uniform_angle, initial_angles):
    new_angles = minimize(obj_function_numpy, 
                         initial_angles, 
                         (vertex_obj, uniform_angle, 'LBFGSB'),
                         method="L-BFGS-B", 
                         jac=compute_gradient,
                         bounds=None,
                         options = {'maxiter': 10000, 'disp':True})   
    
    
    ##seems to solve for angles properly ... intended angles are good.
    ##what is visually folded differs drastically
    bend_around_vertex(vertex_obj, new_angles.x)
    print('!!!COMPUTED fold angles', get_new_angles(vertex_obj))

    print("done folding")
 