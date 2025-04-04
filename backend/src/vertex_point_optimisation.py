import numpy as np
from edge_fold import *
from scipy.optimize import minimize


def get_adjacent_edges(vertex_points, index, vertex_obj):
    n = len(vertex_obj.surrounding_edges)
    source = vertex_obj.vertex
    edge_vec = np.array(vertex_points[(index*3):((index+1)*3)]) - np.array(source)
    
    left_index = (index + 1) % n
    right_index = (index - 1) % n
    
    left_edge_vec = np.array(vertex_points[(left_index*3):((left_index+1)*3)]) - np.array(source)
    right_edge_vec = np.array(vertex_points[(right_index*3):((right_index+1)*3)]) - np.array(source)    
    
    if np.any(np.isnan([left_edge_vec, edge_vec, right_edge_vec])):
        print('GET ADJACENT EDGES CAUSES NAN')
        
        
    return [left_edge_vec, edge_vec, right_edge_vec]

def get_new_dihedral_angle(left_edge_vec, edge_vec, right_edge_vec):    
    # print('vecs', edge_vec, left_edge_vec, right_edge_vec)
    
    normalised_left = np.cross(left_edge_vec ,edge_vec) / (np.linalg.norm(np.cross(left_edge_vec ,edge_vec)) + 1e-8)
    
    normalised_right = np.cross(edge_vec ,right_edge_vec) / (np.linalg.norm(np.cross(edge_vec ,right_edge_vec)) + 1e-8)
    
    ang = np.pi - np.arccos(np.clip(np.dot(normalised_left, normalised_right), -1.0, 1.0))
    
    if np.isnan(ang):
        print('GET NEW DIHEDRAL ANGLE CAUSES NAN')
        
    return ang
    
    

def get_starting_vertex_points(vertex_obj, angles):
    current_crease = vertex_obj.parent_crease  

    bend_around_vertex(vertex_obj, angles)
    
    surrounding_vertices = []
    
    for edge_obj in vertex_obj.surrounding_edges:
        end_vertex_pos = edge_obj.edge_pointer[0] if edge_obj.edge_pointer[1] == vertex_obj.index else edge_obj.edge_pointer[1]
        surrounding_vertices.append(current_crease.new_vertices[end_vertex_pos])
    
    flattened = [item for vertex in surrounding_vertices for item in vertex]
    
    return flattened

    
def apply_vertices_around_vertex(vertex_points, vertex_obj):
    """
    Assuming vertex_points in flattened
    """
    current_crease = vertex_obj.parent_crease  

    num_edges = len(vertex_obj.surrounding_edges)
    unflattened_vertex_points = np.array_split(np.array(vertex_points), num_edges)

    ##Go around, counterclockwise, to all edge vectors around the vertex, and change the value of its end point. 
    ##vertex points are therefore ordered counterclockwise around the vertex
    for (i,edge_obj) in enumerate(vertex_obj.surrounding_edges):
        end_vertex_pos = edge_obj.edge_pointer[0] if edge_obj.edge_pointer[1] == vertex_obj.index else edge_obj.edge_pointer[1]
        current_crease.new_vertices[end_vertex_pos] = unflattened_vertex_points[i].tolist()
    update_edges_around_vertex(vertex_obj)
    
    print('ALTERING VERTEX OBJ')

    

 
def objective_function(vertex_points, vertex_obj, final=False):
    """
    Written to minimise stretching of edges.
    So minimise change is length of edge vectors 
    Could also minimise over edges joining edge vectors
    """
    tots = 0

    for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
        flat_length = edge_obj.flat_length
        
        vertex_point_np = np.array(vertex_points[i*3:(i+1)*3])
        new_edge_vector = vertex_point_np - edge_obj.original_source_vertex
        new_length = np.linalg.norm(new_edge_vector)
        
        if (final):
            edge_obj.length = new_length
        
        tots += np.abs(flat_length - new_length)
    
    if np.isnan(tots):
        print('OBJ FUNC RETURNS NAN')
    
    return tots #+ objective_function_end_point_distances(vertex_points, vertex_obj)


def objective_function_end_point_distances(vertex_points, vertex_obj, final=False):
    """
    This aims to fix the distance between end points (could also be done by fixing sector angle)
    For waterbomb base, this aims to fix the length of the boundary edges for example.
    """
    totss = 0
    
    num_edges = len(vertex_obj.surrounding_edges)
    
    for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
        sector_angle = get_sector_angle(edge_obj)
        new_edge_vector_i = np.array(vertex_points[(3*i): (3*i)+3]) - np.array(vertex_obj.vertex)
        new_edge_vector_prev_i = np.array(vertex_points[(3*((i+1) % num_edges)): (3*((i+1) % num_edges))+3]) - np.array(vertex_obj.vertex)
        
        cos_theta = np.dot(new_edge_vector_i, new_edge_vector_prev_i) / ((np.linalg.norm(new_edge_vector_i) * np.linalg.norm(new_edge_vector_prev_i)) + 1e-8)
        curr_sector = np.arccos(np.clip(cos_theta, -1, 1))
        
        if (final):
            edge_obj.folded_sector_angle = f"{float(curr_sector):.{5}g}"
        # print('secs', np.rad2deg(sector_angle), np.rad2deg(curr_sector))
        totss += (sector_angle - curr_sector) ** 2
        
    if np.isnan(totss):
        print('SECTOR ANG CAUSES NAN')
        
    return totss
        
combined_objective = lambda a, b: objective_function(a,b) + (1/4 *objective_function_end_point_distances(a,b)  )
combined_jac = lambda a, b: jac(a,b) + (1/4 * jac_sector_lengths(a,b))
        
def jac(vertex_points, vertex_obj):

    deriv = np.zeros_like(vertex_points)
    
    for i, edge_obj in enumerate(vertex_obj.surrounding_edges):
        flat_length = edge_obj.flat_length
        origin = edge_obj.original_source_vertex
        vi = np.array(vertex_points[i*3:(i+1)*3])
        direction = vi - origin
        norm = np.linalg.norm(direction)

        safe_norm = norm if norm >= 1e-8 else 1e-8

        factor = 2 * (norm - flat_length) / safe_norm
        deriv[i*3:(i+1)*3] = factor * direction
        
    if np.any(np.isnan(deriv)):
        print('JAC CAUSES NAN')
        
    return deriv


def jac_objective_function_end_point_distances(vertex_points, vertex_obj):
    grad = np.zeros_like(vertex_points)
    num_edges = len(vertex_obj.surrounding_edges)
    v0 = np.array(vertex_obj.vertex)

    for i in range(num_edges):
        i_prev = (i - 1) % num_edges

        vi = np.array(vertex_points[3 * i : 3 * (i + 1)])
        vprev = np.array(vertex_points[3 * i_prev : 3 * (i_prev + 1)])

        ei = vi - v0
        eprev = vprev - v0

        ru = np.linalg.norm(ei)
        rv = np.linalg.norm(eprev)

        if ru < 1e-8 or rv < 1e-8:
            continue

        dot = np.dot(ei, eprev)
        cos_theta = dot / (ru * rv)
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        theta = np.arccos(cos_theta)

        theta_target = get_sector_angle(vertex_obj.surrounding_edges[i])
        diff = theta - theta_target

        denom = np.sqrt(1 - cos_theta**2)
        if denom < 1e-8:
            continue

        dcos_du = (eprev / (ru * rv)) - (cos_theta * ei / ru**2)
        dtheta_du = -1 / denom * dcos_du
        dfi_du = 2 * diff * dtheta_du

        dcos_dv = (ei / (ru * rv)) - (cos_theta * eprev / rv**2)
        dtheta_dv = -1 / denom * dcos_dv
        dfi_dv = 2 * diff * dtheta_dv

        grad[3 * i : 3 * (i + 1)] += dfi_du
        grad[3 * i_prev : 3 * (i_prev + 1)] += dfi_dv

    return grad

        
    
def check_dihedral(vertex_points, angles, vertex_obj):
    # apply_vertices_around_vertex(vertex_points, vertex_obj)
    # curr_dihedral = [ang.item() for ang in get_new_angles(vertex_obj)]
    
    
    totsss = 0
    for i in range(len(vertex_obj.surrounding_edges)):
        [left_edge_vec, edge_vec, right_edge_vec] = get_adjacent_edges(vertex_points, i, vertex_obj)
        new_angle = get_new_dihedral_angle(left_edge_vec, edge_vec, right_edge_vec)
        diff = (angles[i] - new_angle) **2
        # print('currc',curr_dihedral[i], new_angle)
        totsss += np.sqrt(diff) if diff != 0 else 0
        
    if np.isnan(totsss):
        print('DIHEDRAL ANG CAUSES NAN')
    return totsss

def jac_check_dihedral(vertex_points, angles, vertex_obj):
    jac = np.zeros(len(vertex_points))
    
    epsilon = 1e-6  # finite difference step
    
    for i in range(len(vertex_points)):
        # Perturb one variable at a time
        step = np.zeros_like(vertex_points)
        step[i] = epsilon
        
        plus = vertex_points + step
        minus = vertex_points - step
        
        apply_vertices_around_vertex(plus, vertex_obj)
        dihedral_plus = [a.item() for a in get_new_angles(vertex_obj)]
        
        apply_vertices_around_vertex(minus, vertex_obj)
        dihedral_minus = [a.item() for a in get_new_angles(vertex_obj)]
        
        # Derivative of each angle wrt this variable
        grad_i = (np.array(dihedral_plus) - np.array(dihedral_minus)) / (2 * epsilon)
        
        jac[:, i] = -grad_i  # because constraint is angles[i] - theta_i(x)

    return jac


def vertex_slsq(vertex_obj, angles, maxiter=300, ftol=1e-8, eps=1e-8):
    num_edges = len(vertex_obj.surrounding_edges)
    constraints = [{
    'type': 'eq',
    'fun': lambda h: np.abs(check_dihedral(h, angles, vertex_obj))
    # 'jac': lambda h: jac_check_dihedral(h, angles, vertex_obj)
    }
                   , {
    'type': 'ineq',
    'fun': lambda h: 1e-5 - np.abs(objective_function_end_point_distances(h, vertex_obj))
    # 'jac': lambda h: jac_objective_function_end_point_distances(h, vertex_obj)
    } 
                   ]
    
    ##Since Uniform angles already staisfy the objective function, input the failed rotation t uniform folds as x_0 of the optimisation process
    start_vertices = get_starting_vertex_points(vertex_obj, angles)
    
    new_flat_vertices = minimize(
        objective_function,  # your objective function
        start_vertices,
        (vertex_obj,),
        method='SLSQP',
        # jac=jac,
        constraints=constraints,
        options={
                    'maxiter': maxiter,
                    'disp': True,
                    'ftol': ftol,
                    'eps':eps
                }
        )
    
    print(new_flat_vertices)
    apply_vertices_around_vertex(new_flat_vertices.x, vertex_obj)
    print('check', check_dihedral(new_flat_vertices.x, angles, vertex_obj))
    print('obj length', objective_function(new_flat_vertices.x, vertex_obj))
    print('sec size', objective_function_end_point_distances(new_flat_vertices.x, vertex_obj))
    print('Starting second')
    
    return( {
        'check': check_dihedral(new_flat_vertices.x, angles, vertex_obj),
        'obj_length': objective_function(new_flat_vertices.x, vertex_obj, final=True),
        'sec_size': objective_function_end_point_distances(new_flat_vertices.x, vertex_obj, final=True)
        }
    )


    
    # constraints_second = [{
    # 'type': 'ineq',
    # 'fun': lambda h: objective_function(h, vertex_obj) - objective_function(new_flat_vertices.x, vertex_obj)
    # }, {
    # 'type': 'ineq',
    # 'fun': lambda h: check_dihedral(h, angles, vertex_obj) - check_dihedral(new_flat_vertices.x, angles, vertex_obj) 
    # }]
    
    # newer_flat_vertices = minimize(
    #     objective_function_end_point_distances,  # your objective function
    #     start_vertices,
    #     (vertex_obj,),
    #     method='SLSQP',
    #     jac=jac_objective_function_end_point_distances,
    #     constraints=constraints_second,
    #     options={
    #                 'maxiter': 1000,
    #                 'disp': True,
    #                 'ftol': 1e-15,
    #                 'eps': 1e-14
    #             }
    # )
    
    # print(newer_flat_vertices)
    ##seems to solve for angles properly ... intended angles are good.
    ##what is visually folded differs drastically
    # apply_vertices_around_vertex(newer_flat_vertices.x, vertex_obj)
    # print('Computed:', [ang.item() for ang in get_new_angles(vertex_obj)])
    # print('Intended:', angles)
    # print('check', check_dihedral(newer_flat_vertices.x, angles, vertex_obj))
    # print('obj length', objective_function(newer_flat_vertices.x, vertex_obj))
    # print('sec size', objective_function_end_point_distances(newer_flat_vertices.x, vertex_obj))
    # print('second_constraint', objective_function(newer_flat_vertices.x, vertex_obj) - objective_function(new_flat_vertices.x, vertex_obj))

    # print('Intended Fold Angles @ src', angles)
    # print('!!!COMPUTED fold angles', [ang.item() for ang in get_new_angles(vertex_obj)])
    

    
    