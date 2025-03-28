import numpy as np
from scipy.optimize import fmin_cg
from smooth_fold_gens import SmoothFoldPattern, SmoothFoldGeometry, SmoothFoldPatternEdge, SmoothFoldPatternVertex
from constraints import *

def get_direction_vector(edge_obj):
    """
    This gives the axis of rotation to be used in the Rodrigues Formula
    Need to use flat format ALWAYS
    """
    flat_vertices = edge_obj.parent_vertex.parent_crease.flat_vertices
    
    [p_1, p_2] = [flat_vertices[edge_obj.edge_pointer[0]], flat_vertices[edge_obj.edge_pointer[1]]]
    
    non_source_vertex = p_2 if p_1 == edge_obj.original_source_vertex else p_1
    
    d =  np.array(non_source_vertex) -  np.array(edge_obj.original_source_vertex) 
    d_norm = d / np.linalg.norm(d)
    
    ##print('d_norm', d_norm)
    return d_norm


def rodrigues_rot(vertex, edge_obj, angle):
    n = get_direction_vector(edge_obj)
    
    v =  np.array(vertex) - np.array(edge_obj.original_source_vertex) 
    
    sin = np.sin(angle)
    cos = np.cos(angle)

    v_rot = ((1-cos)*(np.dot(v,n))* n)  + (cos * v) + (sin * (np.cross(n,v)))
    
    ##print('v_rot',v_rot)
    
    return  np.array(edge_obj.original_source_vertex) + v_rot


def rodrigues_rotation_matrix(edge_obj, angle):
    [k1, k2, k3] = get_direction_vector(edge_obj)
    
    K = np.array([[0,-k3, k2],
                  [k3, 0, -k1],
                  [-k2, k1, 0]])
    
    sin = np.sin(angle)
    cos = np.cos(angle)

    R = np.eye(3) + (sin * K) + ((1-cos) * np.dot(K, K))    
    
    return R

def compute_transformations(vertex_obj, angle, start_edge):
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
    for i_count in range(0,n):
        i = (start_edge + i_count) % (n)
        right_edge_obj = vertex_obj.surrounding_edges[i]
        ##for each face, we move according to the angle assigned to the edge on its right.
        
        # left_edge_obj = surrounding_edges[0] if i == n-1 else surrounding_edges[i+1]
        fold_angle = angle[i] if isinstance(angle,(list, tuple, np.ndarray)) else angle
        ang = fold_angle + np.pi if  right_edge_obj.fold_type == "V" else np.pi - fold_angle

        #crease between face (i-1) and face i:
        # R1 = rodrigues_rotation_matrix(left_edge_obj, angle_from_left_edge)
        R = rodrigues_rotation_matrix(right_edge_obj, ang)

        transforms[i] = R if i_count == 0 else np.dot(transforms[i-1 % n], R)

    return transforms

def post_fold_vertices(vertex_obj, initial_edge_vectors, angles):
    
    if not isinstance(angles, (list, np.ndarray)):
        angles = [angles] * len(vertex_obj.surrounding_edges)

    def compute_curve_angle_between(edge_vector, left_edge_vector, right_edge_vector, edge_obj):
        """There is already a way of obtaining this svalue fro edge_obj, but this does not allow scipy to track grsdients.
        Here we do it again, explicityly linking the edge vectors to the curve angles
        The left edge vector is and edgevector of the left face, likewise for the right edge_vector
        
        I will use these as 'points' to calculate the face rotations"""
        
        # print('mid', edge_vector)
        # print('left', left_edge_vector)
        # print('right', right_edge_vector)
        
        
        n1 = np.cross(right_edge_vector, edge_vector )
        n2 = np.cross(edge_vector, left_edge_vector)
        
        normalized_1 = n1 / np.linalg.norm(n1)
        normalized_2 = n2 / np.linalg.norm(n2)
        
        dot_product = np.dot(normalized_1, normalized_2)
        
        angle = np.arccos(dot_product)
        
        #fold_angle = scale * angle ##scale * (np.pi - angle) -> result from book assuming normla in flat crease pattern is [0,0,-1] but I have now made it so that it is [0, 0, 1] 
        fold_angle = np.pi-angle

        # print('fold_angleOPT', np.rad2deg(fold_angle))
        
        ##adjust for type of fold
        return fold_angle #if edge_obj.fold_type == 'V' else (2*np.pi)-fold_angle
        
        
        
        
    def obj_function(edge_vectors):
        # print('all edge_vectors', edge_vectors)
        n = len(edge_vectors) // 3 ##since the list gets flattende to a 1d array
        E_i_list = [(compute_curve_angle_between(edge_vectors[i:i+3], edge_vectors[(((i-1) % n)*3) : (((i-1) % n)*3) + 3], edge_vectors[((i+1) % n)*3 : (((i+1) %n) *3)+3], vertex_obj.surrounding_edges[i]) - angles[i]) ** 2 for i in range(n)]
        return sum(E_i_list)

    
    res = fmin_cg(obj_function,
                  (initial_edge_vectors,),
                  maxiter=10)
    
    
    ##create linear constraints for all the angles such that we want the computed curve angle to equal the inputted one
    ##solve for edge_vectors and use to edit endpoints
    
    constraints = []
    n = len(initial_edge_vectors)
    for i in n:
        funct = lambda x: compute_curve_angle_between(x[i:i+3], x[(((i-1) % n)*3) : (((i-1) % n)*3) + 3], x[((i+1) % n)*3 : (((i+1) %n) *3)+3], vertex_obj.surrounding_edges[i]) 
        A = np.vectorize(funct)
        lb = ub = angles[i]
        
        ##A is the matrix which takes the edge_vector i from x (x is a flat vector of edge_vectors) and computes its dihedral angle.
        ##need to turn the constraint into a matrix basically
        ##lb is the angle we want it to be
        
        
    
    return res


def get_local_bases(edge_obj):
    
        """
        This takes in the edge_obj and the edge as a tuple of pointers to vertices (as in the CreasePattern)
        And calculates its local bases. 
        Each edge has its own local basis as it may not have the same orientation as the whole pattern
        This returns the bases according to the right face and according to the left
        """
        
        ##instead compute face normal of the opposite face.
        #So the local bases we are concerned with when we want to fold the right face is such
        ##that e3  is the face normal of the left face
        
        crease_data = edge_obj.parent_vertex.parent_crease
        (j,k) = edge_obj.id #where j is the index of the source vertex
        
        right_face = edge_obj.faceR
        left_face = edge_obj.faceL
        
        edges_right = get_edges_of_face(right_face, crease_data.edges)
        faceR_edge_vectors = [] #these give teo edge vectors of the face with the source vector as root
        
        for edge in edges_right:
            if j in edge:
                u = [x for x in edge if x != j][0]
                faceR_edge_vectors.append(np.array(crease_data.new_vertices[u]) - np.array(crease_data.new_vertices[j]))
                
                
        edges_left = get_edges_of_face(left_face, crease_data.edges)
        faceL_edge_vectors = [] #these give teo edge vectors of the face with the source vector as root
        
        for edge in edges_left:
            if j in edge:
                u = [x for x in edge if x != j][0]
                faceL_edge_vectors.append(np.array(crease_data.new_vertices[u]) - np.array(crease_data.new_vertices[j]))
                
        
        

        
        
        
        # vertex_source_obj = edge_obj.parent_vertex
        
        # edge_cp = edge_obj.edge_pointer #this is the edge as presented in crease
        
        e2 = edge_obj.edge_vector
        

        er3 = np.cross(faceR_edge_vectors[0], faceR_edge_vectors[1]) #the vector orthogonal to both of these is e1

        
        el3 = np.cross(faceL_edge_vectors[0], faceL_edge_vectors[1]) #the vector orthogonal to both of these is e1

        # Normalize ruling direction (local x-axis)
        er3_unit = er3 / np.linalg.norm(er3)
        el3_unit = el3 / np.linalg.norm(el3)

        
        # Normalize ruling direction (local y-axis)
        e2_unit = e2 / np.linalg.norm(e2)

        # Compute local normal (z-axis)
        er1 = np.cross(er3, e2)
        er1_unit = er1 / np.linalg.norm(er1)
        el1 = np.cross(el3, e2)
        el1_unit = el1 /np.linalg.norm(el1)
        
        
        ##this returns the local basis for the right and left side of the fold

        return [[el1_unit, e2_unit, el3_unit], [er1_unit, e2_unit, er3_unit]]
    

def compute_bend_angle(curve_strength, angle_between_faces):
    """
    This determines the elevation of the faces on either side of the fold
    We are given the angle between the faces, these angles are altered before input  
    depending on if the fold is a valley or a mountain. 
    Bases on the asymmetry required of the fold, we determine the elevation
    If curve_strength is 0.5, it bends boths sides equally (by the same angle)
    """
    
    #scale = 1 if fold_type == 'V' else -1
    
    right_angle =  (np.pi - angle_between_faces) * curve_strength
    left_angle = (np.pi - angle_between_faces) * (1 - curve_strength)
    
    return [left_angle, right_angle]

def alt_rotate_local_xy_to_xz(v, e1, e2, e3, theta):
    e1_x, e1_y, e1_z = e1
    e2_x, e2_y, e2_z = e2
    e3_x, e3_y, e3_z = e3

    W_new = np.array([
        [np.cos(theta), 0, np.sin(theta)],
        [0, 1, 0],
        [-np.sin(theta), 0, np.cos(theta)]
    ])
    
    E = np.array([
        [e1_x, e2_x, e3_x],
        [e1_y, e2_y, e3_y],
        [e1_z, e2_z, e3_z]
    ])
    
    v_local = np.dot(np.linalg.inv(E), v)
    
    rotated_v_local = np.dot(W_new, v_local)
    
    return np.dot(E,rotated_v_local)


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
                    
def turn_face(face, visited_vertices, current_crease):
    """
    Method:
    Identify visited vertex on face and use its original vertex coordingates to get edge vectors to each unvisited vertex point
    pull out vertices of face
    Identify vertices not already visited
    For each unvisited vertex g, calculate original edge vector to it from our chosen vertec point (step 1)
    modify vertex g such that the edge vector persists with the new vertex h' obtained after folding
    """
    
    visited_face_vertex = [x for x in face if x in visited_vertices][0]
    
    
    for vertex in face:
        if vertex not in visited_vertices:
            
            original_vector_from_vistied = np.array(current_crease.flat_vertices[vertex]) - np.array(current_crease.flat_vertices[visited_face_vertex])
            
            new_vertex = np.array(current_crease.new_vertices[visited_face_vertex]) + original_vector_from_vistied
            
            current_crease.new_vertices[vertex] = new_vertex.tolist()
            

def bfs_on_face(face, face_opposite_fold, edge_obj, queue, visited_faces, visited_edges):
    """
    This returns a list of lists that is essentially a bfs on the input face, 
    BFS search on faces using face as source, and stops when the face opposite the fold
    has been reached. 
    We do not want to alter any vertices on this face as it would amount to a change 
    in the angle between the faces
    
    Note the source face has already been rotated according to the angle specified by the fold,
    We just want to bring the other faces and vertices into agreement with this
    
    So apart from the vertices of the fold edge, the other edges have changed and we recalculate 
    the non-shared vertices of the faces we visit in bfs 
    """
    
    ##method
    ##for all pairs of vertices in face that are edges, but not boundary edges,
    ##collect all other faces that have those vertices (taking care to always exclude the face opposite the fold if it appears)
    ##also taking care to not revist faces
    # ##print(face)
    source = face 
    queue = queue
    visited_faces = visited_faces
    visited_edges = visited_edges
    
    crease_data = edge_obj.parent_vertex.parent_crease #this is the default flat format
      
    
                    
    visited_faces = visited_faces + [source]
    # ##print('v', visited_faces)
    visited_vertices = [vertex for face in visited_faces for vertex in face]
    # ##print('h', crease_data.edges)
    visited_edges = visited_edges + get_edges_of_face(face, crease_data.edges)
    
    
    adjacent_faces = get_adjacent_faces(source, crease_data.edges, crease_data.faces, crease_data.edges_assignments)
    queue += adjacent_faces #we do not want to turn the source face as thsi face is directly opposite the edge. 
    
    
    while queue:
        ###print('quq', queue)

        face = queue.pop(0)
        if face != face_opposite_fold and face not in visited_faces:


            crease_data = edge_obj.parent_vertex.parent_crease
            adjacent_faces = get_adjacent_faces(face, crease_data.edges, crease_data.faces, crease_data.edges_assignments)
            turn_face(face, visited_vertices, crease_data)
            
            visited_faces.append(face)
            visited_vertices = [vertex for face in visited_faces for vertex in face] ##things area added to vistited vertices to fast. 
            visited_edges = visited_edges + get_edges_of_face(face, crease_data.edges)
            
            

            for neighbour_face in adjacent_faces:
                # if neighbour_face != face_opposite_fold and neighbour_face not in visited_faces:
                    #to turn the face, we need the edges and vertices shared by the source 
                    ##and we want the same relative edge vectors to hold
                    # ##print('turning an adjacent face')
                
                    queue.append(neighbour_face)
                    
      
def bend_edge(edge_obj, angle_between_faces, sym):
    """
    Convention chosen, bend and push through right first then the left
    We are given the angle between the faces, these angles are altered before input  
    depending on if the fold is a valley or a mountain. 
    """
    
    [[el1_unit, e2_unit, el3_unit], [er1_unit, e2_unit, er3_unit]] = get_local_bases(edge_obj)
    
    
    scale = 1 if edge_obj.fold_type == "V" else -1
    angle = angle_between_faces if edge_obj.fold_type == "V" else (np.pi * 2) - angle_between_faces
    
    [left_angle, right_angle] = compute_bend_angle(sym, angle)
    
    current_crease = edge_obj.parent_vertex.parent_crease
    
    
    
    ##rotate the vertices of the faces (that are not the edge ones) by the relevant angle
    ##about the e2 axis (local y axis basically to lift it out into the z (e3)plane)
    
    faceR = [] if sym == 0 else edge_obj.faceR
    faceL = [] if sym == 1 else edge_obj.faceL
    
    
    for vertex in faceR + faceL:
        v = np.array(current_crease.new_vertices[vertex])
        if vertex not in edge_obj.edge_pointer:#not #in any(x != v for x in edge_obj.edge_coords):
            vertex_vector = np.array(current_crease.new_vertices[vertex]) - np.array(edge_obj.source_vertex) ##this calculates the original edge vector so that any changes in angles are relative to the flat state, not the current fold config
            ##if user has folded by 10, and then folds by 20, this should not ersult in a fold by 30. It should merely be a fold by 20. This makes it easier to track changes
     
            
            if vertex in faceL:
                new_vector = alt_rotate_local_xy_to_xz(vertex_vector, el1_unit, e2_unit, el3_unit, -left_angle) #we rotate all vertices of the face (that are not the edge vertices) by the required right angle along the local y axis 
            else:
                new_vector = alt_rotate_local_xy_to_xz(vertex_vector, er1_unit, e2_unit, er3_unit, right_angle)
                
            new_vertex = (edge_obj.source_vertex + new_vector).tolist()
            
            current_crease.new_vertices[vertex] = new_vertex #updates the crease pattern            

            current_angle_between_faces = current_crease.calculate_fold_angles(edge_obj.faceL, edge_obj.faceR, edge_obj.fold_type)
            edge_obj.update_edge()
            
            ##print('calc', current_angle_between_faces)
            ##print('updated', edge_obj.curve_angle)
            
            #now bfs to update everything else to match
                #now bfs to update everything else to match
            queue = []             
            visited_faces = []
            visited_edges = []
            bfs_on_face(faceR, edge_obj.faceL, edge_obj, queue, visited_faces, visited_edges)

            bfs_on_face(faceL, edge_obj.faceR, edge_obj, queue, visited_faces, visited_edges)

            #we rotate all vertices of the face (that are not the edge vertices) by the required right angle along the local y axis 
      
      
            
def update_edges_around_vertex(vertex_obj):
    for edge_obj in vertex_obj.surrounding_edges:
        edge_obj.update_edge()
        print('length', edge_obj.length)
        ##print(edge_obj.curve_angle)
        
        
def bend_around_vertex(vertex_obj, p_angle, update=True, start_edge=0):
    """
    For a given edge, andle and sym, 
    Bend the edge accordingly whilst ensuring that other edges aro source vertex are validly bent
    This should work perfectly for single vertex patterns like the water bomb base, but not for those with multiple internal vertices
    Currently this version works for a singular crease, past this previous folds are tampered with when folding others around the vertex
    """

    current_crease = vertex_obj.parent_crease  

    transforms = compute_transformations(vertex_obj, p_angle, start_edge)
    n = len(current_crease.new_vertices)
    new_vertices = [None] * n
    for (i, face) in enumerate(vertex_obj.surrounding_faces):
        T = transforms.get(i)

        for v in face:
            new_vertices[v] = np.dot(T, np.array(current_crease.flat_vertices[v])).tolist()
    
    current_crease.new_vertices = new_vertices ##issue for when we move on to multivertexed folds. .. i only want to change affeted vertices not replace th whole vertex list
    
    if update:
        update_edges_around_vertex(vertex_obj)
    
    
    #######OPTIMISER
    # edge_vectors = [edge_obj.edge_vector for edge_obj in vertex_obj.surrounding_edges]
    
    # newer_flat = post_fold_vertices(vertex_obj, edge_vectors, p_angle)
    # print(newer_flat)

    # new_edge_vectors = [newer_flat[(3*i) : (3*i + 3)] for i in range(n)]
    
    
    # for (i, edge_obj) in enumerate(vertex_obj.surrounding_edges):
    #     #newer_vertices = {}
    #     ##we want to use edge pointer to get the vertex of the endpoint of the edge_vector
    #     ##and then update these using the new edge vectors
    #     source_vertex_pos = edge_obj.id[0]
    #     end_vertex_pos = edge_obj.edge_pointer[0] if edge_obj.edge_pointer[1]==source_vertex_pos else edge_obj.edge_pointer[1]
    #     print('source vertex', current_crease.flat_vertices[source_vertex_pos])

    #     current_crease.new_vertices[end_vertex_pos] = (np.array(current_crease.flat_vertices[source_vertex_pos]) + np.array(new_edge_vectors[i])).tolist()

    # print('new vertices')
    # print(current_crease.new_vertices)
    # if update:
    #     update_edges_around_vertex(vertex_obj)
        
    #current_crease.new_vertices = newer_vertices


    
    if (tachi_constraints_vertex_level(vertex_obj, p_angle)):
        print("#####INTENDED IS A VALID FOLD CONFIG")
    else:
        print("XXXXXINTENDED IS NOT A VALID FOLD CONFIG")
        
    
    if (tachi_constraints_vertex_level_computed(vertex_obj)):
        print("#####COMPUTED IS A VALID FOLD CONFIG")
    else:
        print("XXXXXCOMPUTED IS NOT A VALID FOLD CONFIG")
        
        


