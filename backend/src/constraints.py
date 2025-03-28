import numpy as np
from smooth_fold_gens import SmoothFoldPattern, SmoothFoldGeometry, SmoothFoldPatternEdge, SmoothFoldPatternVertex


def get_sector_angle(edge_obj):
    """
    if edge obj is i, then I want the sector angle between this and edge i-1
    if the edge obj is edge 0, then the angle between this and the last edge
    In counterclockwise
    """
    edges = edge_obj.parent_vertex.surrounding_edges

    i = edge_obj.id[1]
    prev_i = i+1 if i != len(edges)-1 else 0
    
    angle_i = edge_obj.angle_from_vertex
    angle_prev = edges[prev_i].angle_from_vertex

    sector_angle = (angle_i - angle_prev) % (2 * np.pi)

    
    return (2 * np.pi) - sector_angle 
    
    
def tachi_constraints_vertex_level(vertex_obj, pangles):
    ident = np.eye(3)
    prod = ident
    
    for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
        p_angle = pangles[i] if isinstance(pangles, (list, np.ndarray)) else pangles
        prod = np.matmul(prod, tachi_constraints_edge_level(edge_obj, p_angle))
   
    print(prod)
    # print(np.allclose(prod, ident, atol=1e-15))
    diff_norm = np.linalg.norm(prod - ident, ord="fro")
    # print('plse print', diff_norm)
    return diff_norm <= 1e-05#np.allclose(prod, ident, atol=1e-05) #(prod == ident).all()
    

def tachi_constraints_edge_level(edge_obj, p_angle):
    # print(edge_obj.fold_type)
        
    sector_angle = get_sector_angle(edge_obj)
    
    dihedral_angle = p_angle if edge_obj.fold_type == 'V' else (np.pi * 2) - p_angle


    # print(np.degrees(sector_angle))
    sin_theta = np.sin(sector_angle)
    cos_theta = np.cos(sector_angle)
    
    # print(np.degrees(dihedral_angle))
    sin_rho = np.sin(dihedral_angle)
    cos_rho = np.cos(dihedral_angle)
    
    sector_angle_matrix = np.array([[cos_theta, -sin_theta, 0],
                                    [sin_theta, cos_theta,  0],
                                    [0,   0,    1]])

    fold_angle_matrix = np.array([[1, 0,       0],
                                  [0, cos_rho, -sin_rho],
                                  [0, sin_rho, cos_rho]])
    
    # print(sector_angle_matrix)
    # print(fold_angle_matrix)
    
    return np.matmul(sector_angle_matrix, fold_angle_matrix)


    
def tachi_constraints_edge_level_computed(edge_obj):
    """This differs from the other version as it checks the constraints for
    The angles resultant from the actual folding. 
    This can not always be uniform all around
    A check (mainly out of curiosity) to see if the resultant folds (non-uniform)
    satisfy the constraints
    """
    
        
    sector_angle = get_sector_angle(edge_obj)
    
    dihedral_angle = edge_obj.curve_angle if edge_obj.fold_type == 'V' else (np.pi * 2) - edge_obj.curve_angle


    sin_theta = np.sin(sector_angle)
    cos_theta = np.cos(sector_angle)
    
    sin_rho = np.sin(dihedral_angle)
    cos_rho = np.cos(dihedral_angle)
    
    sector_angle_matrix = np.array([[cos_theta, -sin_theta, 0],
                                    [sin_theta, cos_theta,  0],
                                    [0,   0,    1]])

    fold_angle_matrix = np.array([[1, 0,       0],
                                  [0, cos_rho, -sin_rho],
                                  [0, sin_rho, cos_rho]])
    
    # print(sector_angle_matrix)
    # print(fold_angle_matrix)
    
    return np.matmul(sector_angle_matrix, fold_angle_matrix)
    

    
def tachi_constraints_vertex_level_computed(vertex_obj):
    ident = np.eye(3)
    prod = ident
    
    for edge_obj in vertex_obj.surrounding_edges:
        prod = np.matmul(prod, tachi_constraints_edge_level_computed(edge_obj))
   
    # print(prod)
    # print(ident)
    diff_norm = np.linalg.norm(prod - ident, ord="fro")
    # print('diff_norm,ac', diff_norm)
    return diff_norm <= 1e-05 #np.allclose(prod, ident, atol=1e-05) #(prod == ident).all()




    
# def tachi_constraints_edge_level_inputted(edge_obj, p_angle):
#     """This differs from the other version as it checks the constraints for
#     non_uniform inputted angles
#     This can not always be uniform all around
#     A check (mainly out of curiosity) to see if the resultant folds (non-uniform)
#     satisfy the constraints
#     """
    
#     print(edge_obj.fold_type)
        
#     sector_angle = get_sector_angle(edge_obj)
    
#     dihedral_angle = p_angle if edge_obj.fold_type == 'V' else (np.pi * 2) - p_angle


#     print(np.degrees(sector_angle))
#     sin_theta = np.sin(sector_angle)
#     cos_theta = np.cos(sector_angle)
    
#     print(np.degrees(dihedral_angle))
#     sin_rho = np.sin(dihedral_angle)
#     cos_rho = np.cos(dihedral_angle)
    
#     sector_angle_matrix = np.array([[cos_theta, -sin_theta, 0],
#                                     [sin_theta, cos_theta,  0],
#                                     [0,   0,    1]])

#     fold_angle_matrix = np.array([[1, 0,       0],
#                                   [0, cos_rho, -sin_rho],
#                                   [0, sin_rho, cos_rho]])
    
#     # print(sector_angle_matrix)
#     # print(fold_angle_matrix)
    
#     return np.matmul(sector_angle_matrix, fold_angle_matrix)
    

    
# def tachi_constraints_vertex_level_inputted(vertex_obj, p_angles):
#     ident = np.eye(3)
#     prod = ident
    
#     for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
#         prod = np.dot(prod, tachi_constraints_edge_level_inputted(edge_obj, p_angles[i]))
   
#     #compute frobenius norm of the difference
#     closeness_val = torch.norm(prod-ident, ord="fro")
    
#     return closeness_val #this return a number indicating the closeness of both matrices