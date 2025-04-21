import numpy as np
from scipy.optimize import fmin_cg
from scipy.spatial.transform import Rotation as R
from smooth_fold_gens import SmoothFoldPattern, SmoothFoldGeometry, SmoothFoldPatternEdge, SmoothFoldPatternVertex
from constraints import *

def get_new_angles(vertex_obj):
    new_angles = []
    
    for edge_obj in vertex_obj.surrounding_edges:
        new_angles.append(edge_obj.curve_angle)
    
    return new_angles

def get_direction_vector(edge_obj):
    """
    This gives the axis of rotation to be used in the Rodrigues Formula
    Need to use flat format ALWAYS
    """
    flat_vertices = edge_obj.parent_vertex.parent_crease.flat_vertices
    new_source_vertex = edge_obj.parent_vertex.parent_crease.new_vertices[edge_obj.id[0]]
    new_end_vertex = edge_obj.parent_vertex.parent_crease.new_vertices[edge_obj.end_vertex_position]

    
    [p_1, p_2] = [flat_vertices[edge_obj.edge_pointer[0]], flat_vertices[edge_obj.edge_pointer[1]]]
    
    non_source_vertex = p_2 if p_1 == edge_obj.original_source_vertex else p_1
    
    d =  np.array(non_source_vertex) -  np.array(edge_obj.original_source_vertex) 
    d_norm = d / np.linalg.norm(d)
    
    ##print('d_norm', d_norm)
    return d_norm


def rodrigues_rotation_matrix(edge_obj, angle):
    [k1, k2, k3] = get_direction_vector(edge_obj)
    
    K = np.array([[0,-k3, k2],
                  [k3, 0, -k1],
                  [-k2, k1, 0]])
    
    sin = np.sin(angle)
    cos = np.cos(angle)

    R = np.eye(3) + (sin * K) + ((1-cos) * np.dot(K, K))    
    
    return R

def compute_transformations(T_start, vertex_obj, vertex_zero, angle, start_edge, final=False):
    """
    Sequential folding is almost.
    But the start edge has the wrong dihedral angle due to interference from folding the last edge.
    Due to this, 
    even when we have a valid fold configuration from gradient_descent or lbfgs,
    we can not visualise the fold configuration, we can instead only simulate one which is close except for two angles
    """

    surrounding_faces = vertex_obj.surrounding_faces
    n = len(surrounding_faces)
    
    
    transforms = {} #these are transformations as applied to faces, since sym is 0.5, I need to consider the edge that affects this face as its right face, and the other that does so as its left face
    #transforms[start_edge] = np.eye(3)  #face 0 remains unrotated.
    print('!!!INTENDED fold angles', angle)
    transforms[start_edge] = T_start if final == True else np.eye(3) 
    right_edge_obj = vertex_obj.surrounding_edges[start_edge]
    print('fold_angle_1', angle)
    fold_angle = angle[start_edge] if isinstance(angle,(list, tuple, np.ndarray)) else angle
    print('fold_angle', fold_angle)
    ang = fold_angle + np.pi if  right_edge_obj.fold_type == "V" else np.pi - fold_angle
    prod = rodrigues_rotation_matrix(right_edge_obj, ang)
    
    for i_count in range(1,n):
        i = (start_edge + i_count) % (n)
        right_edge_obj = vertex_obj.surrounding_edges[i]
        ##for each face, we move according to the angle assigned to the edge on its right.
        
        # left_edge_obj = surrounding_edges[0] if i == n-1 else surrounding_edges[i+1]
        current_fold_angle = right_edge_obj.curve_angle

        fold_angle = angle[i] if isinstance(angle,(list, tuple, np.ndarray)) else angle
        change_in_angle = fold_angle #- (0 if current_fold_angle == np.deg2rad(180) else current_fold_angle)#if current_fold_angle == np.deg2rad(180)  else fold_angle - current_fold_angle

        ang = change_in_angle + np.pi if right_edge_obj.fold_type == "M" else np.pi - change_in_angle
        #ang =  (2 * np.pi) - fold_angle if  right_edge_obj.fold_type == "V" else fold_angle
        
        #crease between face (i-1) and face i:
        # R1 = rodrigues_rotation_matrix(left_edge_obj, angle_from_left_edge)
        
        R = rodrigues_rotation_matrix(right_edge_obj, ang)
        
        #transforms[i] = T.copy()
        
        transforms[i] =  transforms[(i-1 )% n] @ R
        prod = prod @ R
    print(prod)
    print('norm', np.linalg.matrix_norm(np.eye(3) - prod))
    return transforms

def compute_transformations_Q(vertex_obj, angle, start_edge):
    surrounding_faces = vertex_obj.surrounding_faces
    n = len(surrounding_faces)
    
    
    transforms = {} 
    
    transforms[0] = R.identity()
    
    for i in range(1,n):
        right_edge_obj = vertex_obj.surrounding_edges[i]
        fold_angle = angle[i] if isinstance(angle,(list, tuple, np.ndarray)) else angle
        ang = fold_angle + np.pi if  right_edge_obj.fold_type == "V" else np.pi - fold_angle
    
        r = R.from_rotvec(get_direction_vector(right_edge_obj) * ang)

        r_total = transforms[i-1] * r

        transforms[i] = r_total
    return(transforms)


def get_edges_of_face(face, edge_vertices):
    face_vertex_pairs = [[a, b] for i, a in enumerate(face) for b in face[i + 1:]]
    # ##print('face_vertex_pairs', face_vertex_pairs)
    edges_of_face = []
    
    for [a,b] in face_vertex_pairs:
        if [a,b] in edge_vertices:
            edges_of_face.append([a,b])
        elif [b,a] in edge_vertices:
            edges_of_face.append([b,a])
    # ##print('edges_of_face', edges_of_face)
    return(edges_of_face)

def get_adjacent_faces(face, edge_vertices, face_vertices, edge_assignment):
    
    """
    This returns all faces adjacent to the given face.
    This odes so by get a list of all non-boundary egdes of the face
    It then loops through these and all faces, checking if this edges are in it
    """
    face_vertex_pairs = [[a, b] for i, a in enumerate(face) for b in face[i + 1:]]
    edges_of_face = []
    for [a,b] in face_vertex_pairs:
        if [a,b] in edge_vertices:
            i =  edge_vertices.index([a,b])
            if edge_assignment[i] != "B":
                edges_of_face.append([a,b])
        elif [b,a] in edge_vertices:
            i =  edge_vertices.index([b,a])
            if edge_assignment[i] != "B":
                edges_of_face.append([b,a])
                
                
    adjacent_faces = []
    for edge in edges_of_face:
        for face in face_vertices:
            if all(x in face for x in edge):
                adjacent_faces.append(face)
                
    return(adjacent_faces)                   
 
def update_edges_around_vertex(vertex_obj):
    for edge_obj in vertex_obj.surrounding_edges:
        edge_obj.update_edge()
        #print('length', edge_obj.length)
        ##print(edge_obj.curve_angle)

def check_dihedral(post_fold_dihedrals, prefered_dihedrals, vertex_obj):
    totsss = 0
    for i in range(len(vertex_obj.surrounding_edges)):

        diff = (post_fold_dihedrals[i] - prefered_dihedrals[i]) **2
        # print('currc',curr_dihedral[i], new_angle)
        totsss += np.sqrt(diff) if diff != 0 else 0

    return totsss

def check_edge_lengths(vertex_obj):
    """
    Written to minimise stretching of edges.
    So minimise change is length of edge vectors 
    Could also minimise over edges joining edge vectors
    """
    tots = 0

    for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
        flat_length = edge_obj.flat_length
   
        new_length = np.linalg.norm(edge_obj.edge_vector)
        
        tots += np.abs(flat_length - new_length)

    return tots

def check_sector_size(vertex_obj):
    """
    This aims to fix the distance between end points (could also be done by fixing sector angle)
    For waterbomb base, this aims to fix the length of the boundary edges for example.
    """
    totss = 0
    
    num_edges = len(vertex_obj.surrounding_edges)
    
    for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
        sector_angle = get_sector_angle(edge_obj)
        new_edge_vector_i = np.array(edge_obj.edge_vector)
        new_edge_vector_prev_i = vertex_obj.surrounding_edges[(edge_obj.id[1] + 1) % num_edges].edge_vector
        
        cos_theta = np.dot(new_edge_vector_i, new_edge_vector_prev_i) / ((np.linalg.norm(new_edge_vector_i) * np.linalg.norm(new_edge_vector_prev_i)) + 1e-8)
        curr_sector = np.arccos(np.clip(cos_theta, -1, 1))
        
        # print('secs', np.rad2deg(sector_angle), np.rad2deg(curr_sector))
        totss += (sector_angle - curr_sector) ** 2
        
    if np.isnan(totss):
        print('SECTOR ANG CAUSES NAN')
        
    return totss
      
        
def bend_around_vertex(vertices, vertex_index, edge_start_dict, p_angle, update=True, start_edge=0, final=False):
    """
    For a given edge, andle and sym, 
    Bend the edge accordingly whilst ensuring that other edges aro source vertex are validly bent
    This should work perfectly for single vertex patterns like the water bomb base, but not for those with multiple internal vertices
    Currently this version works for a singular crease, past this previous folds are tampered with when folding others around the vertex
    """
    vertex_obj = vertices[vertex_index]
    ##ACTUALLY FOLDS RODRIGUES ALMOST ACCURATELY p_angle = [np.deg2rad(116.8), np.deg2rad(98), np.deg2rad(98), np.deg2rad(116.8), np.deg2rad(98), np.deg2rad(98)]

    # transforms = compute_transformations(vertex_obj, p_angle, start_edge)
    # n = len(current_crease.new_vertices)
    # new_vertices = [None] * n
    # source = vertex_obj.vertex
    # faces = vertex_obj.surrounding_faces
    
    prefered_angles_around_vertex = p_angle[edge_start_dict[vertex_index]: edge_start_dict[vertex_index] + len(vertex_obj.surrounding_edges)]

    
    prefered_angles = []
    for (i, vert) in enumerate(vertices):
        if not (vert.isBoundary):
            if i == vertex_index:
                prefered_angles += [ang.item() for ang in get_new_angles(vert)]  
            else:     
                prefered_angles += p_angle[edge_start_dict[i]: edge_start_dict[i] + len(vert.surrounding_edges) ].tolist() if isinstance(p_angle,(tuple, np.ndarray)) else p_angle[edge_start_dict[i]: edge_start_dict[i] + len(vert.surrounding_edges) ]

    print('p', prefered_angles_around_vertex)

    
    T_start = np.eye(3) ##this why only face 0 of the 0th vertex is fixed in the xy-plane
    vertex_zero = [vert for vert in vertices if not vert.isBoundary][0]
    
    for (i, vert) in enumerate(vertices):
        current_crease = vert.parent_crease  
        temp_vertex_point_dict = {}

        if not vert.isBoundary:
           
            start = edge_start_dict[i]
            end =  start + len(vert.surrounding_edges) 
            relevant_angles = p_angle[start:end]
            print('rel', i, relevant_angles)
            transforms = compute_transformations(T_start, vert, vertex_zero, relevant_angles, start_edge, final)
            source = vert.vertex #vert.parent_crease.new_vertices[i]
            faces = vert.surrounding_faces
            
            for (i, face) in enumerate(faces):
                
                T = transforms.get(i)#.as_matrix()
                adjacent_faces = face + get_adjacent_faces(face, current_crease.edges, current_crease.faces, current_crease.edges_assignments)
                print(adjacent_faces, adjacent_faces)
                for v in face:
                    ##should we instead be rotating the edge vector and then adding it to our source to replace v??
                    
                    ##Could instead solve for rotations about all other vertices whilst keeping the already rotated angles fixed (subject to the new vertices)
                    rotated_edge_vector = np.dot(T, np.array(current_crease.flat_vertices[v] - np.array(source)))
                    temp_vertex_point_dict[v] = (rotated_edge_vector + source).tolist()
                    #current_crease.new_vertices[v] = (rotated_edge_vector + source).tolist()#np.dot(T, np.array(current_crease.flat_vertices[v])).tolist()

            T_start = np.eye(3)

    #current_crease.new_vertices = new_vertices ##issue for when we move on to multivertexed folds. .. i only want to change affeted vertices not replace th whole vertex list
        for v in list(temp_vertex_point_dict.keys()):
            current_crease.new_vertices[v] = temp_vertex_point_dict[v]
        
    if update:
        for vert in vertices:
            update_edges_around_vertex(vert)
        
    
    new_angles_around_vertex = [ang.item() for ang in get_new_angles(vertex_obj)]
    new_angles = []
    for (i, vert) in enumerate(vertices):
        if not (vert.isBoundary):
                new_angles += [ang.item() for ang in get_new_angles(vert)]  
           
    
    
    
    print('n', new_angles_around_vertex)
    print('alln', new_angles)
    
    return(
        {
        'check': check_dihedral(new_angles_around_vertex, prefered_angles_around_vertex, vertex_obj),
        'obj_length': check_edge_lengths(vertex_obj),
        'sec_size': check_sector_size(vertex_obj),
        'mean': np.rad2deg(np.sum(new_angles_around_vertex) / len(new_angles_around_vertex))
        }
    )
   
