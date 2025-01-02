import numpy as np
from src.data_extractors.crease_pattern import CreasePattern

#global plane's normal vector ... should be 0,0,1
class SmoothFoldGeometry(CreasePattern):
    def __init__(self, fold_data):
        """
        Initialize the crease pattern with the FOLD format data.
        """
        super().__init__(fold_data)  # Initialize parent class
        self.fold_width = 0.05
        self.curve_strength = 0.5 #set to symmetric folds
        #self.fold_angles = fold_data.get('edges_foldAngle', [])
        
    def compute_face_normal(self, face):
        """
        Compute the normals for a face.
        The cross product of two non-parallel edges of the face
        """
        
        face_edges = self.get_face_edges(face) ##edges are given in counter clockwise order
        
        
        non_parallel_edges = [face_edges[0], face_edges[1]]
        
        [edge1, edge2] = self.convert_to_actual_coords(non_parallel_edges)
        
        v1 = np.array(edge1[1]) - np.array(edge1[0])
        v2 = np.array(edge2[1]) - np.array(edge2[0])

        
        return np.cross(v1, v2)
    
    def compute_local_basis(self, face):
        """
        Each face has its own local basis as it may not have the same orientation as the whole pattern
        """
        
        [v1, v2, v3] = self.convert_to_actual_coords(face)
        e1 = np.array(v2) - np.array(v1)  # Edge vector 1
        e2 = np.array(v3) - np.array(v1)  # Edge vector 2

        # Normalize ruling direction (local x-axis)
        e1_unit = e1 / np.linalg.norm(e1)

        # Compute local normal (z-axis)
        e3_unit = np.cross(e1, e2)
        e3_unit /= np.linalg.norm(e3_unit)

        # Compute local tangent vector (y-axis)
        e2_unit = np.cross(e3_unit, e1_unit)

        return e1_unit, e2_unit, e3_unit
              
    def calculate_fold_angles(self, faceA, faceB, foldType="V"):
        """
        Compute the dihedral angle between two faces
        This is called by another function which takes an edge as parameter, and finds the two faces which share that edge
        (implement later) If the edge is a valley, this is positive, if it is a mountain, this is negative
        """
        scale = -1 if foldType == "M" else 1
        n1 = self.compute_face_normal(faceA)
        n2 = self.compute_face_normal(faceB)
        
        normalized_1 = n1 / np.linalg.norm(n1)
        normalized_2 = n2 / np.linalg.norm(n2)
        
        dot_product = np.dot(normalized_1, normalized_2)
        
        angle = np.arccos(dot_product)
        
        fold_angle = scale * angle ##scale * (np.pi - angle) -> result from book assuming normla in flat crease pattern is [0,0,-1] but I have now made it so that it is [0, 0, 1] 

        return fold_angle
    
    def cubic_hermitan_interpolation_polys(l_1):
        h_30 = (l_1 ^ 3)/4 - (3 * l_1)/4 + 1/2
        
        h_31 = (l_1 ^ 3)/4 - (l_1 ^ 2)/4 - (l_1)/4 + 1/4
        
        h_32 =  (l_1 ^ 3)/4 + (l_1 ^ 2)/4 - (l_1)/4 - 1/4
        
        h_33 = (-(l_1)^3)/4 + (3*l_1)/4 + 1/2
        
        return [h_30, h_31, h_32, h_33]
    
    def define_normalised_parametric_curve(self, edge):
        """
        This function returns the function c^i_{t} which will take in l_1 as input.
        Implementing paramteric curves as described in 3.1 - Geometry of Smooth Folds
        """
        w_i = self.compute_smooth_fold_width(edge) 
        [faceA, faceB] = self.get_edges_surrounding_edge(edge)
        theta_i = self.calculate_fold_angles(faceA, faceB, self.edges_assignments[self.edges.index(edge)])
        alpha_i = self.compute_curve_strength(edge)
        
        beta_L1 = beta_R1 = 1 ##free parameters but for not set to 1. 
        
        ##All results belowe are normalised
        c_L0 = np.array([[0],
                          [-(w_i) / 2],
                          [0]]) #c^i(-1)
        
        c_R0 = np.array([[0],
                          [(w_i) / 2],
                          [0]]) #c^i(1)
        
        c_L1 = beta_L1 * np.array([[0],
                                   [np.cos(alpha_i * theta_i)],
                                   [-np.sin(alpha_i * theta_i)]]) 
        c_R1 = beta_R1 * np.array([[0],
                                   [np.cos((1 - alpha_i) * theta_i)],
                                   [np.sin((1 - alpha_i) * theta_i)]])
        
        
        def c(l_1):
            h = self.cubic_hermitan_interpolation_polys
            return (h[0] * c_L0) + (h[1] * c_R0) + (h[2] * c_L1) + (h[3] * c_R1)
        
        
        return c
    
    def compute_direction_vector(self, edge):
        """
        This function returns the direction vector h^i_{t} for edge numbered i.
        It is based on the orientation of the faces adjacent to the given edge
        """
        
        [faceA, faceB] = self.get_faces_surrounding_edge(edge)
        
        n1 = self.compute_face_normal(faceA)
        n2 = self.compute_face_normal(faceB)
        
        normalized_1 = n1 / np.linalg.norm(n1)
        normalized_2 = n2 / np.linalg.norm(n2)
        
        dot_product = np.dot(normalized_1, normalized_2)
        
        
        return dot_product
    
    def compute_smooth_fold_width(self, edge):
        """
        This function returns the distance between position vectors c^i(-1) and c^i(1) 
        Denoted in the text w_i
        """
        ###Seems I might have to initialise / choose the width of each fold myself, otherwise the definition ends up being circular. 
        #####Develop further later to optimise the fold-width perhaps proportional to the length of the edge or to the angles / could also make this a user editable metric. 
        # I.e., the fold width of a give edge can be selected and changed by the user. 
        ##For now, simply return universal fold_width (same for all edges)
        return self.fold_width
    
    def compute_curve_strength(self, edge):
        """
        This function returns the angle the left side of the smooth fold makes with the face adjacent to it. That is the extent of the curve
        Denoted in the text a_i
        """
        ###Same as for the fold_width, this value need not be fixed, and should be optimised to have the fold match real life as much as possible.
        ##For now, it is set to 0.5 to ensure that the curve/fold is symmetric. The angle the left side makes with the adjacent face on the left is equal to that of the right side with its adjacent face
        return self.curve_strength
    
    def smooth_fold_representation(self, edge):
        """
        Smooth folds are ruled surfaces (Def 3).
        This function returns a given edge as a smooth fold
        """
        
        parametric_curve = self.compute_smooth_fold_width * self.define_normalised_parametric_curve(edge)
        direction_vector = self.compute_direction_vector(edge)
        
        def F(l_1, l_2):
            return parametric_curve(l_1) + (l_2 * direction_vector)
        
        return F
        
        
class SmoothFoldPattern():
    def __init__(self, vertices):
        """
        Set up smooth fold pattern as a set of smoothFoldPatternVertex
        """
        self.vertices = [SmoothFoldPatternVertex(vertex) for vertex in vertices]
        
        ##later number the vertices and push this number down to the functions of that vertex. So if on vertec n, prepend n to all values i.e., angle_jk, edge_mk
    
    
class SmoothFoldPatternVertex(SmoothFoldGeometry):
    def __init__(self, vertex):
        """
        Set up smooth fold pattern as a set of smoothFoldPatternVertex
        """
        self.surrounding_edges = self.order_edges_counterclockwise(vertex) ##returns edges numbered m1, to mk, in counterclockwise order
        self.surrounding_faces = self.get_faces_surrounding_vertex(vertex) ##self.surrounding_faces[(i,j)] gives face_ij between edges m_i and m_j
        self.surrounding_angles = self.get_angles_surrounding_vertex(vertex) ##self.surrounding_angles[(i,j)] gives angle_ij between edges m_i and m_j
        
    def order_edges_counterclockwise(self, vertex):
        """
        Order the edges around vertx v counter clockwise
        This returns the actual vertices of the edges also, not the pointers to the vertex set
        """
        ##Take vertex v as origin and compute e_x and e_y from v, using arctan to calculate angle where vertex v is the origin. Then order based on increase in angle
        ##Note, would also neeed to keep track if which folds are mountain and valley and reoarder edge assignment accordingly. 
        ##New structure, {edge: coords, type: M/B/V}
        edges = self.convert_to_actual_coords(self.get_edges_surrounding_vertex(vertex)) #each edge in the from (u,v)
        
        unordered_edge = []
        
        for (i, edge) in enumerate(edges):
            edge_vector = np.array(edge[1]) - np.array(edge[0]) #edge vector = v - u
            [e_x, e_y, e_z] = np.array(edge_vector) - np.array(vertex)
            
            angle_from_vertex = np.arctan2(e_y, e_x)
            
            unordered_edge.append({'edge': edge,
                                   'angle': angle_from_vertex,
                                   'type': self.edges_assignments[i]})
            
        def sort_according_to_angle(edge):
            return edge.angle
        ##now reorder according to increase in angle to obtain counterclockwise order of edges.
        sorted_edges = unordered_edge.sort(key=sort_according_to_angle)
        
        #edge_vector = np.array(edges[1]) - np.array(edges[0]) #edge vector = v - u
        ##next STEP HERE
        return sorted_edges
                
    def get_face_between_edges(self, edge_1, edge_2):
        (adj, shared) = self.check_adjacent_edges(edge_1, edge_2)
        if adj:
            return(shared)
            
    def get_faces_surrounding_vertex(self):
        """
        Gets the faces surrounding vertex where face_ij is the face between self.surrounding_edges[i] and self.surrounding_edges[j] if they do share an edge
        Done by iterating through the edges surrounding the vertex (that are now ordered counterclockwise)
        So we know that adjacent edges on the graph are adjacent in the list, with edges 1 to k then, 
        Faces around the vertex are F_{i, i+1} until i = k, then we have the final face F_{i=k,0}
        This gives me the faces in counter clockwise order
        """
        
        number_of_edges = len(self.surrounding_edges)
        
        faces = {} #a dict where key (i,j) has face f_ij between edges e_i, e_j, which are self.surrounding_edges[i].edges,  self.surrounding_edges[j].edges resp.
        
        for i in range(number_of_edges-1):
            faces.update({(i, i+1): self.get_face_between_edges(self.surrounding_edges[i].edges, self.surrounding_edges[i+1].edges )})
            
        faces.update({(number_of_edges-1, 0): self.get_face_between_edges(self.surrounding_edges[-1].edges, self.surrounding_edges[0].edges )})
        
        return faces
    
    def get_angles_surrounding_vertex(self):
        """
        Gets the angles surrounding vertex where angle_ij is the angle between self.surrounding_edges[i] and self.surrounding_edges[j] if the two edges are adjacent
        Could do a running total type thing. 
        So F_0,1 is the angle of edge 1 from vertex - angle of edge 0 from vertex
        F_1,2 is the angle of edge 2 from vertex - 9angle of edge 1 from vertex
        F_k,0 is 360 or 2pi - the sum of all other angles
        """
        number_of_edges = len(self.surrounding_edges)
        
        angles = {} #a dict where key (i,j) has face f_ij between edges e_i, e_j, which are self.surrounding_edges[i].edges,  self.surrounding_edges[j].edges resp.
        sum_of_angles = 0
        
        for i in range(number_of_edges-1):
            angle = self.surrounding_edges[i+1].angles - self.surrounding_edges[i].angles
            angles.update({(i, i+1): angle})
            sum_of_angles += angle
            
        angles.update({(number_of_edges-1, 0): np.pi - sum_of_angles})
        
        return angles
    
    