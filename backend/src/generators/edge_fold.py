import numpy as np
from .smooth_fold_gens import SmoothFoldPattern, SmoothFoldGeometry, SmoothFoldPatternEdge, SmoothFoldPatternVertex

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
                faceR_edge_vectors.append(np.array(crease_data.vertices[u]) - np.array(crease_data.vertices[j]))
                
                
        edges_left = get_edges_of_face(left_face, crease_data.edges)
        faceL_edge_vectors = [] #these give teo edge vectors of the face with the source vector as root
        
        for edge in edges_left:
            if j in edge:
                u = [x for x in edge if x != j][0]
                faceL_edge_vectors.append(np.array(crease_data.vertices[u]) - np.array(crease_data.vertices[j]))
                
        
        

        
        
        
        # vertex_source_obj = edge_obj.parent_vertex
        
        # edge_cp = edge_obj.edge_pointer #this is the edge as presented in crease
        
        e2 = edge_obj.edge_vector
        
        # right_face = edge_obj.faceR
        # arbitrary_vertex_R_index = [x for x in right_face if x not in edge_cp][0] 
        # arbitrary_vertex_R = vertex_source_obj.parent_crease.vertices[arbitrary_vertex_R_index] #get random vertex from right face that is not an edge vertex
        # parallel_vector_to_e2_R = arbitrary_vertex_R + e2
        
        er3 = np.cross(faceR_edge_vectors[0], faceR_edge_vectors[1]) #the vector orthogonal to both of these is e1
        
        # left_face = edge_obj.faceL
        # arbitrary_vertex_L_index = [x for x in left_face if x not in edge_cp][0] 
        # arbitrary_vertex_L = vertex_source_obj.parent_crease.vertices[arbitrary_vertex_L_index] #get random vertex from right face that is not an edge vertex
        # parallel_vector_to_e2_L = arbitrary_vertex_L + e2
        
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

        # Compute local tangent vector (y-axis)

        ##this returns the local basis for the right and left side of the fold
        print( [[el1_unit, e2_unit, el3_unit], [er1_unit, e2_unit, er3_unit]])

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

def rotate_about_axis(v, axis_unit, theta):
    
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    one_minus_cos = 1 - cos_theta

    # Skew-symmetric matrix of the axis
    x, y, z = axis_unit
    skew_symmetric = np.array([
        [0, -z, y],
        [z, 0, -x],
        [-y, x, 0]
    ])

    # Outer product of the axis with itself
    outer_product = np.outer(axis_unit, axis_unit)

    # Rotation matrix
    rotation_matrix = (
        cos_theta * np.eye(3) +
        sin_theta * skew_symmetric +
        one_minus_cos * outer_product
    )
    
    ##this does not seem to change the z axis for any of the vertex points 
    # Rotate the vector
    return np.dot(rotation_matrix, v)
    

def get_edges_of_face(face, edge_vertices):
    face_vertex_pairs = [[a, b] for i, a in enumerate(face) for b in face[i + 1:]]
    # print('face_vertex_pairs', face_vertex_pairs)
    edges_of_face = []
    
    for [a,b] in face_vertex_pairs:
        if [a,b] in edge_vertices:
            edges_of_face.append([a,b])
        elif [b,a] in edge_vertices:
            edges_of_face.append([b,a])
    # print('edges_of_face', edges_of_face)
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
                    
                    
def turn_face(face, visited_vertices, original_crease, current_crease):
    """
    Method:
    pull out vertices of face
    Identify vertices not already visited
    For each unvisited vertex g, identitfy vertices h which have been visited and have an edge with vertek g
    Get original edge vector of vertex h to g before fold
    modify vertex g such that the edge vector persists with the new vertex h' obtained after folding
    """
    
    for vertex in face:
        if vertex not in visited_vertices:
            for edge in current_crease.edges:
                if vertex in edge:
                    #print('the edge', edge, vertex, edge.remove(vertex), edge)
                    other_vertex = [x for x in edge if x != vertex][0]
                    if other_vertex in visited_vertices: #other vertex refers to already altered vertices on the face
                        #I care about the edge vector between edge instances of other_vertex and veretx???
                        original_edge_vector = np.array(original_crease.vertices[vertex]) - np.array(original_crease.vertices[other_vertex])
                        
                        new_vertex_coords = np.array(current_crease.vertices[other_vertex]) + original_edge_vector
                        print('v,change', vertex, new_vertex_coords )
                        current_crease.vertices[vertex] = new_vertex_coords
                                        

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
    # print(face)
    source = face 
    queue = queue
    visited_faces = visited_faces
    visited_edges = visited_edges
    
    crease_data = edge_obj.parent_vertex.parent_crease #this is the default flat format
    original_crease_data = edge_obj.parent_vertex.original_crease #this is the default flat format
      
    
                    
    visited_faces = visited_faces + [source]
    # print('v', visited_faces)
    visited_vertices = [vertex for face in visited_faces for vertex in face]
    # print('h', crease_data.edges)
    visited_edges = visited_edges + get_edges_of_face(face, crease_data.edges)
    
    
    adjacent_faces = get_adjacent_faces(source, crease_data.edges, crease_data.faces, crease_data.edges_assignments)

    queue += adjacent_faces #we do not want to turn the source face as thsi face is directly opposite the edge. 
    
    
    while queue:
        #print('quq', queue)

        face = queue.pop(0)
        crease_data = edge_obj.parent_vertex.parent_crease
        adjacent_faces = get_adjacent_faces(face, crease_data.edges, crease_data.faces, crease_data.edges_assignments)
        turn_face(face, visited_vertices, crease_data, original_crease_data)
        
        visited_faces.append(face)
        visited_vertices = [vertex for face in visited_faces for vertex in face]
        visited_edges = visited_edges + get_edges_of_face(face, crease_data.edges)

        for neighbour_face in adjacent_faces:
            if neighbour_face != face_opposite_fold and neighbour_face not in visited_faces:
                #to turn the face, we need the edges and vertices shared by the source 
                ##and we want the same relative edge vectors to hold
                # print('turning an adjacent face')
               
                queue.append(neighbour_face)

                
                
         
            
def bend_edge(edge_obj, angle_between_faces):
    """
    Convention chosen, bend and push through right first then the left
    We are given the angle between the faces, these angles are altered before input  
    depending on if the fold is a valley or a mountain. 
    """
    
    [[el1_unit, e2_unit, el3_unit], [er1_unit, e2_unit, er3_unit]] = get_local_bases(edge_obj)
    
    
    scale = 1 if edge_obj.fold_type == "V" else -1
    angle = angle_between_faces * scale
    
    [left_angle, right_angle] = compute_bend_angle(0.5, angle)
    
    current_crease = edge_obj.parent_vertex.parent_crease
    
    ##rotate the vertices of the faces (that are not the edge ones) by the relevant angle
    ##about the e2 axis (local y axis basically to lift it out into the z (e3)plane)
    
    for vertex in edge_obj.faceR:
        if current_crease.vertices[vertex] not in edge_obj.edge_coords:
            new_vector = rotate_about_axis(edge_obj.edge_vector, e2_unit, right_angle) #we rotate all vertices of the face (that are not the edge vertices) by the required right angle along the local y axis 
            new_vertex = edge_obj.source_vertex + new_vector
            
            current_crease.vertices[vertex] = new_vertex #updates the crease pattern
            queue = []             
            visited_faces = []
            visited_edges = []
            
            #now bfs to update everything else to match
            bfs_on_face(edge_obj.faceR, edge_obj.faceL, edge_obj, queue, visited_faces, visited_edges)
            
    for vertex in edge_obj.faceL:
        if vertex not in edge_obj.edge_pointer: #current_crease.vertices[vertex] not in edge_obj.edge_coords:
            new_vector = rotate_about_axis(edge_obj.edge_vector, e2_unit, left_angle) #we rotate all vertices of the face (that are not the edge vertices) by the required right angle along the local y axis 
            new_vertex = edge_obj.source_vertex + new_vector
            
            current_crease.vertices[vertex] = new_vertex #updates the crease pattern
            queue = []             
            visited_faces = []
            visited_edges = []
            #now bfs to update everything else to match
            bfs_on_face(edge_obj.faceL, edge_obj.faceR, edge_obj, queue, visited_faces, visited_edges)
            
    return edge_obj.parent_vertex.parent_crease
            
            
        
    
    
    
    
        
