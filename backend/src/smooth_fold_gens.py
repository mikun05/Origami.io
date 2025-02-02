import numpy as np

from crease_pattern import CreasePattern
#from src.data_extractors.crease_pattern import CreasePattern

def R_1(theta):
    cos = np.cos(theta)
    sin = np.sin(theta)
    
    return np.matrix([1, 0, 0],
                    [0, cos, -sin],
                    [0, sin, cos])
def R_3(theta):
    cos = np.cos(theta)
    sin = np.sin(theta)
    
    return np.matrix([cos, -sin, 0],
                    [sin, cos, 0],
                    [0, 0, 1])
def Q_1(theta):
        cos = np.cos(theta)
        sin = np.sin(theta)
                
        return np.matrix([1, 0, 0, 0],
                        [0, cos, -sin, 0],
                        [0, sin, cos, 0],
                        [0, 0, 0, 1]) 
def Q_3(theta):
    cos = np.cos(theta)
    sin = np.sin(theta)
    
    return np.matrix([cos, -sin, 0, 0],
                    [sin, cos, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1])
def T(b):
    """
        b is a 3 elem vector
    """
    
    return np.matrix([1, 0, 0, b[0]],
                    [0, 1, 0, b[1]],
                    [0, 0, 1, b[2]],
                    [0, 0, 0, 1])
    

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
    
    
    def define_normalised_parametric_curve(self, edge_obj):
        """
        ON HOLD
        This function returns the function c^i_{t} which will take in l_1 as input.
        Implementing paramteric curves as described in 3.1 - Geometry of Smooth Folds
        
        edge is an instance of SmoothFoldPatternEdge
        """
        
        w_i = edge_obj.width #width is w_i, self.compute_smooth_fold_width(edge) 
        [faceA, faceB] = self.get_faces_surrounding_edge(edge_obj.edge_pointer) ##change to retrieve faces from source vertex numbering. Face retrieval shouldne always be based on vertex points since these change
        theta_i = self.calculate_fold_angles(faceA, faceB, self.edges_assignments[self.edges.index(edge_obj.edge_pointer)])
        alpha_i = edge_obj.curve_strength
        
        #print('thetai', theta_i)
        
        beta_L1 = beta_R1 = 1 ##free parameters but for not set to 1. 
        
        ##All results belowe are normalised
        c_L0 = np.array([0,
                        -(w_i) / 2,
                        0]) #c^i(-1)
        
        c_R0 = np.array([0,
                        (w_i) / 2,
                         0]) #c^i(1)
        
        c_L1 = beta_L1 * np.array([0,
                                   np.cos(alpha_i * theta_i),
                                   -np.sin(alpha_i * theta_i)]) 
        c_R1 = beta_R1 * np.array([0,
                                   np.cos((1 - alpha_i) * theta_i),
                                   np.sin((1 - alpha_i) * theta_i)])
        
        def cubic_hermitan_interpolation_polys(l_1):
            h_30 = (l_1 ^ 3)/4 - (3 * l_1)/4 + 1/2
            
            h_32 = (l_1 ^ 3)/4 - (l_1 ^ 2)/4 - (l_1)/4 + 1/4
            
            h_33 =  (l_1 ^ 3)/4 + (l_1 ^ 2)/4 - (l_1)/4 - 1/4
            
            h_31 = (-(l_1)^3)/4 + (3*l_1)/4 + 1/2
            
            return [h_30, h_31, h_32, h_33]
        
        
        def c(l_1):
            h = cubic_hermitan_interpolation_polys(l_1)
            return (h[0] * c_L0) + (h[1] * c_R0) + (h[2] * c_L1) + (h[3] * c_R1)
        
        return c
    
    def compute_direction_vector(self, width, edge_pointer, edge_vector):
        """
        This function returns the direction vector h^i_{t} for edge numbered i.
        It is based on the orientation of the faces adjacent to the given edge
        """
        w_i = width #width is w_i, self.compute_smooth_fold_width(edge) 

        [faceA, faceB] = self.get_faces_surrounding_edge(edge_pointer)
        
        n1 = self.compute_face_normal(faceA)
        n2 = self.compute_face_normal(faceB)
        
        normalized_1 = n1 / np.linalg.norm(n1)
        normalized_2 = n2 / np.linalg.norm(n2)
        
        dot_product = np.dot(normalized_1, normalized_2)
        
        actual_direction_vector = edge_vector / np.linalg.norm(edge_vector)

        # print('edge', edge_vector)
        # print('direction vector', actual_direction_vector)
        return actual_direction_vector 
    

    # def smooth_fold_representation(self, edge_obj):
    #     """
    #     ON HOLD
    #     Smooth folds are ruled surfaces (Def 3).
    #     This function returns a given edge as a smooth fold
    #     """
        
    #     # print('check:', self.define_normalised_parametric_curve(edge_obj))
        
    #     c = self.define_normalised_parametric_curve(edge_obj)
        
    #     #parametric_curve = edge_obj.width * c()
    #     e1 = self.compute_direction_vector(edge_obj.width, edge_obj.edge_pointer, edge_obj.edge_vector)
    #     e1_unit = e1 / np.linalg.norm(e1)
    #     e2 = np.cross(np.array([0,0,1]), e1)
    #     e2_unit = e2 / np.linalg.norm(e2)
        
    #     local_x = np.array([1, 0, 0])

    #     # Compute the rotation axis and angle
    #     axis = np.cross(local_x, e2_unit)
    #     axis_norm = np.linalg.norm(axis)
    
    #     axis_unit = axis / axis_norm
    #     angle = np.arccos(np.dot(local_x, e2_unit))
       
        
    #     def rotation_matrix(axis, angle):
    #         cos_theta = np.cos(angle)
    #         sin_theta = np.sin(angle)
    #         one_minus_cos = 1 - cos_theta

    #         x, y, z = axis
    #         return np.array([
    #             [cos_theta + x * x * one_minus_cos, x * y * one_minus_cos - z * sin_theta, x * z * one_minus_cos + y * sin_theta],
    #             [y * x * one_minus_cos + z * sin_theta, cos_theta + y * y * one_minus_cos, y * z * one_minus_cos - x * sin_theta],
    #             [z * x * one_minus_cos - y * sin_theta, z * y * one_minus_cos + x * sin_theta, cos_theta + z * z * one_minus_cos]
    #         ])
        
    #     R = rotation_matrix(axis_unit, angle)
        
    #     def F(l_1, l_2):
    #         c_global = np.dot(c(l_1), R.T) # edge_obj.source_vertex
    #         return (c(l_1)) #keep + (l_2 * np.array(e2_unit))
        
    #     return F
        
        
class SmoothFoldPattern():
    def __init__(self, fold_data):
        """
        Set up smooth fold pattern as a set of smoothFoldPatternVertex
        """
        self.geom = SmoothFoldGeometry(fold_data)
        self.vertex_objects = self.format_vertices(self.geom.new_vertices) #[SmoothFoldPatternVertex(vertex) for vertex in vertices]
        
    def format_vertices(self, vertices):
        smooth_fold_vertex = []
        for (j, vertex) in enumerate(vertices):
            vertex_obj = SmoothFoldPatternVertex(self.geom, vertex, j)
            smooth_fold_vertex.append(vertex_obj)
            
        return smooth_fold_vertex
    
    def to_dict(self):
        return {
            "vertex_objects": [vertex_obj.to_dict() for vertex_obj in self.vertex_objects]
        }
                
        ##later number the vertices and push this number down to the functions of that vertex. So if on vertec n, prepend n to all values i.e., angle_jk, edge_mk
    
    
class SmoothFoldPatternVertex:
    def __init__(self, parent_crease, vertex, index):
        """
        Set up smooth fold pattern as a set of smoothFoldPatternVertex
        """
        self.index = index
        self.parent_crease = parent_crease
        self.original_vertex = vertex
        self.vertex = vertex
        self.surrounding_edges = self.order_edges_counterclockwise(vertex, index) ##returns edges numbered m1, to mk, in counterclockwise order
        # self.surrounding_faces = self.get_faces_surrounding_vertex(vertex, index) ##self.surrounding_faces[(i,j)] gives face_ij between edges m_i and m_j
        self.surrounding_angles = self.get_angles_surrounding_vertex(vertex) ##self.surrounding_angles[(i,j)] gives angle_ij between edges m_i and m_j
        #self.enclosing_path = self.compute_simple_closed_path()
        
    def to_dict(self):
        return {
            "index": self.index,
            "vertex": self.vertex,
            "flat_vertex": self.original_vertex,
            "surrounding_edges": [edge_obj.to_dict() for edge_obj in self.surrounding_edges],
            "surrounding_angles": [float(angle) for angle in self.surrounding_angles]
        }
        
    def order_edges_counterclockwise(self, vertex, index):
        """
        Order the edges around vertx v counter clockwise
        This returns the actual vertices of the edges also, not the pointers to the vertex set
        """
        ##Take vertex v as origin and compute e_x and e_y from v, using arctan to calculate angle where vertex v is the origin. Then order based on increase in angle
        ##Note, would also neeed to keep track if which folds are mountain and valley and reoarder edge assignment accordingly. 
        ##New structure, {edge: coords, type: M/B/V}
        edge_pointers = self.parent_crease.get_edges_surrounding_vertex(vertex) #each edge in the from (u,v)
        # print(edge_pointers)
        unordered_edge = []
        
        
        ##make it a dict with key j,k
        
        for (k, edge_pointer) in enumerate(edge_pointers): #edge pointers
            i = self.parent_crease.edges.index(edge_pointer) ##to get correct edge assignment


            if self.parent_crease.edges_assignments[i] != 'B': ##excludes boundary edges and vertices
            
                # print(edge_pointer, 'not boundary')

            

                [faceA, faceB] = self.parent_crease.get_faces_surrounding_edge(edge_pointer)

                theta_jk = self.parent_crease.calculate_fold_angles(faceA, faceB, self.parent_crease.edges_assignments[i]) ##might have to be pi - this value
                ##if input is a flat crease pattern, theta is ALWAYS 0
                edge = self.parent_crease.convert_to_actual_coords(edge_pointer)
                
                edge_vector = np.array(edge[1]) - np.array(edge[0]) #edge vector = v - u
                [e_x, e_y, e_z] = np.array(edge_vector) - np.array(vertex)
                
                angle_from_vertex = np.arctan2(e_y, e_x)
                
                
                edge_obj = SmoothFoldPatternEdge(self, index, k, edge, edge_pointer, vertex, edge_vector, 
                                                self.parent_crease.fold_width, 
                                                self.parent_crease.curve_strength, 
                                                self.parent_crease.edges_assignments[i], 
                                                theta_jk, angle_from_vertex, faceA, faceB)
                ##Things that will be subject to change when bending are fold_width, curve strength, theta angle .. by intervention
                ##edge_vector and edge will also change as a consquence of the above
                
                unordered_edge.append({'edge_obj': edge_obj,
                                    'angle': angle_from_vertex ##this is phi(mjk). It is the cummulative angle
                                    })
            
        def sort_according_to_angle(edge):
            #print(edge['angle'])
            return edge['angle']
        ##now reorder according to increase in angle to obtain counterclockwise order of edges.
       # print(sorted(unordered_edge, key=lambda x: sort_according_to_angle(x)))

        sorted_edges = [x['edge_obj'] for x in sorted(unordered_edge, key=lambda x: sort_according_to_angle(x))]
        ##should return a list of edge_objects. in order of k
        return(sorted_edges)
                
    def get_face_between_edges(self, edge_1, edge_2):
        (adj, shared) = self.check_adjacent_edges(edge_1, edge_2)
        if adj:
            return(shared)
            
    # def get_faces_surrounding_vertex(self):
    #     """
    #     Gets the faces surrounding vertex where face_ij is the face between self.surrounding_edges[i] and self.surrounding_edges[j] if they do share an edge
    #     Done by iterating through the edges surrounding the vertex (that are now ordered counterclockwise)
    #     So we know that adjacent edges on the graph are adjacent in the list, with edges 1 to k then, 
    #     Faces around the vertex are F_{i, i+1} until i = k, then we have the final face F_{i=k,0}
    #     This gives me the faces in counter clockwise order
    #     """
        
    #     number_of_edges = len(self.surrounding_edges)
        
    #     faces = {} #a dict where key (i,j) has face f_ij between edges e_i, e_j, which are self.surrounding_edges[i].edges,  self.surrounding_edges[j].edges resp.
        
    #     for i in range(number_of_edges-1):
    #         faces.update({(i, i+1): self.get_face_between_edges(self.surrounding_edges[i].edge, self.surrounding_edges[i+1].edge )})
            
    #     faces.update({(number_of_edges-1, 0): self.get_face_between_edges(self.surrounding_edges[-1].edge, self.surrounding_edges[0].edge )})
        
    #     return faces
    
    def get_angles_surrounding_vertex(self, vertex):
        """
        Gets the angles surrounding vertex where angle_ij is the angle between self.surrounding_edges[i] and self.surrounding_edges[j] if the two edges are adjacent
        Could do a running total type thing. 
        So F_0,1 is the angle of edge 1 from vertex - angle of edge 0 from vertex
        F_1,2 is the angle of edge 2 from vertex - 9angle of edge 1 from vertex
        F_k,0 is 360 or 2pi - the sum of all other angles
        """
        number_of_edges = len(self.surrounding_edges)
        
        if number_of_edges == 0:
            return []
        else:
        
            angles = []
            sum_of_angles = 0
            
            for i in range(number_of_edges-1):
                angle = self.surrounding_edges[i+1].angle_from_vertex - self.surrounding_edges[i].angle_from_vertex
                angles.append(angle)
                sum_of_angles += angle
                
            angles.append(np.pi - sum_of_angles) #so angles[-1] is the angle between the last and first edge
            
            return angles ##this is alpha_jk for vertex ja nd edge k
    
    # def compute_simple_closed_path(self):
    #     """
    #     ON HOLD
    #     Return (j,k): [b_L, b_R] for the vertex j and each edge k around the vertex. 
    #     For simplicity,we specifiy (allow for the alteration of) the distance this path is to the vertex 
    #     (keeping the distance equal along each edge). The only constraint is that the path does not cover some other intersection.
    #     So check that no other vertices exist in the closed path
    #     This will be useful for computing the roatation matrices. 
    #     """
        
    #     gamma_closed_path = []
        
    #     for (i, edge_obj) in enumerate(self.surrounding_edges):

    #         ##rotate anticlockwise for b_L
    #         F = self.parent_crease.smooth_fold_representation(edge_obj)
    #         b_L = F(-1, 1) #+ np.array(edge_obj.source_vertex)
    #         b_R = F(1, 1) #+ np.array(edge_obj.source_vertex)
    #         other_end = F(0, 1) #+ np.array(edge_obj.source_vertex)
            
    #         # b_L = np.matmul(np.matrix([
    #         #             [np.cos(angle_displaced_from_center), -np.sin(angle_displaced_from_center)],
    #         #             [np.sin(angle_displaced_from_center),  np.cos(angle_displaced_from_center)]
    #         #         ]), edge_vector) + vertex ##since b_L is in the span of e_1, e_2 not just relative to vertex
            
    #         # ##rotate clockwise for b_R
    #         # b_R = np.matmul(np.matrix([
    #         #             [np.cos(-angle_displaced_from_center), -np.sin(-angle_displaced_from_center)],
    #         #             [np.sin(-angle_displaced_from_center),  np.cos(-angle_displaced_from_center)]
    #         #         ]), edge_vector) + vertex
            
    #         # print('bL', np.array(b_L), 'bR', np.array(b_R), 'middle', other_end, edge_obj.source_vertex)
            
    #         ##calculate the normal to the edge_vector at the point 10% away from the vertex. 
    #         ##and take the point that is w/2 away in one direcion and w/2 away in the other. 
            
    #         gamma_closed_path.append([b_L, b_R]) ##ordering will match edge set
            
    #         #calculate distance from verte
            
    #     return gamma_closed_path
            
        
    def check_R_constraint(self):
        """
        The product over all edges of vertex j of R_1(theta_jk) * R_3(alpha_jk) should be I_3
        (24 in paper)
        """
        identity = np.matrix([1,0,0],
                            [0,1,0],
                            [0,0,1])
        
        
        prod = identity
        
        for edge_obj in self.surrounding_edges:
            theta_jk = edge_obj.curve_angle
            alpha_jk = self.surrounding_angles[edge_obj.k]
            prod = np.matmul(prod, np.matmul(R_1(theta_jk), R_3(alpha_jk)))
            
        return identity == prod
    
    def check_d_constraint(self):
        zero_vec = np.array([[0],[0],[0]])
        
        identity = np.matrix([1,0,0],
                            [0,1,0],
                            [0,0,1])
        
        summ = zero_vec
        
        def g(k): ##test / rewrite
            edge_obj = self.surrounding_edges[k]
            if k == 0:
                return np.array([0, 0, 0])
            else:
                return g(k-1) + ((edge_obj.flat_width - edge_obj.width) * np.cross(np.array([0,0,1]), (edge_obj.edge_vector / np.linalg.norm(edge_obj.edge_vector))))
        
        
        
        for edge_obj in self.surrounding_edges:
            prod = identity
            [b_L, b_R] = self.gamma_closed_path(self.vertex)[edge_obj.k]

            w_vec = b_R - g(edge_obj.k) - b_L + g(edge_obj.k-1)
            i_vec = self.gamma_closed_path(self.vertex)[0][0] - b_R if edge_obj.k == len(self.surrounding_edges) - 1 else self.gamma_closed_path(self.vertex)[edge_obj.k+1][0] - b_R
            
            rel_w_vec = np.matmul(np.linalg.inv(R_3(edge_obj.angle_from_vertex)), w_vec)
            rel_i_vec = np.matmul(np.linalg.inv(R_3(edge_obj.angle_from_vertex)), i_vec) ## relative to the edge vector
            
            for l in range(edge_obj.k):
                theta = self.surrounding_edges[l].edge_obj.theta
                alpha = self.surrounding_angles[l]
                prod = np.matmul(prod, np.matmul(R_1(theta), R_3(alpha)))
                
            summ += np.matmul(prod, np.matmul(R_1(self.surrounding_edges[edge_obj.k].edge_obj.theta * self.surrounding_angles[edge_obj.k]), rel_w_vec) + 
                                    np.matmul(R_1(self.surrounding_edges[edge_obj.k].edge_obj.theta), rel_i_vec))
            
        return summ == zero_vec
        

        
##Simplified such that the simple closed path corssing each edge surrounding a vertx only once without containing other edge intersctions
##as defined in section 6, is here simplified to be the path which intersects with the edges precisely 0.01 away from the origin

class SmoothFoldPatternEdge:
    def __init__(self, parent_vertex, j, k, edge_coords, edge_pointer, source_vertex, edge_vector, flat_w, curve_strength, fold_type, curve_angle, angle_from_vertex, faceA, faceB):
        """
        Set up smooth fold pattern as a set of smoothFoldPatternVertex
        """
        self.parent_vertex = parent_vertex
        self.id = (j,k) #meaning edge k of vertex j
        self.original_source_vertex = source_vertex
        self.source_vertex = source_vertex
        self.edge_coords = edge_coords
        self.original_edge_coords = edge_coords

        self.edge_pointer = edge_pointer #identifies the edge position in the edges_vertices set in the crease pattern
        self.edge_vector = edge_vector #m_jk
        self.curve_strength = curve_strength
        self.flat_width = flat_w ##initalised width across edge when flat but this can change as adjacent faces move 
        self.width = self.width_after_curve(curve_angle) #wjk at any time other than 0
        self.fold_type = fold_type
        self.curve_angle = curve_angle
        self.angle_from_vertex = angle_from_vertex #cummulative angle, later used to calculate alpha
        [self.faceL, self.faceR] = [faceA, faceB]
        
        
    def to_dict(self):
        return {
            "index": self.id,
            "edge_vector": self.edge_vector.tolist(),
            "edge_pointer": self.edge_pointer,
            "source_vertex": self.source_vertex,
            "edge_coords": self.edge_coords,
            "symmetry": self.curve_strength,
            "angle": float(self.curve_angle),
            "faceL": self.faceL,
            "faceR": self.faceR,
            "fold_type": self.fold_type
        }
        
    def width_after_curve(self, theta):
        curve_segment_1 = (1 - self.curve_strength) * self.flat_width
        curve_segment_2 = self.curve_strength * self.flat_width

        return float(np.sqrt((curve_segment_1**2 * curve_segment_2**2 - (2*curve_segment_1*curve_segment_2) / np.cos(np.pi - theta))))
        
    def set_curve_angle(self, angle):
        self.curve_angle = angle
        self.update_width(angle)
        
    def update_edge(self):
        angle = self.parent_vertex.parent_crease.calculate_fold_angles(self, self.faceL, self.faceR, self.foldType)
        self.set_curve_angle(angle)

        ##update the rest
        #moev the edge and edeg vector accordingly 
        ##constraints and validty checks will be done before calling this function
        
        
        
    
        
    
    
        # def fold_edge(self, num): #so num is k
#     """
#        This implements L^{jk} for current vertex j and edge numbered k. num == k
#     """
    
#     edge_vector, edge, phi_jk, edge_type = self.surrounding_edges[num].edge_vector, self.surrounding_edges[num].edge, self.surrounding_edges[num].angle, self.surrounding_edges[num].type
#     edge_obj = self.surrounding_edges[num].edge_obj
#     [faceA, faceB] = self.get_faces_surrounding_edge(edge_obj.edge)
#     theta_jk = self.calculate_fold_angles(faceA, faceB, self.edges_assignments[self.edges.index(edge)]) ##might have to be pi - this value
#     alpha_jk = self.surrounding_angles[num]
    
#     current_width = 0.5 #place holder this will mean the inal config is such that all faces are 0.5 away
    
#     [b_L, b_R] = self.gamma_closed_path(self.vertex)[num] ##this will be a point on the entry line 0.01 away from the vertex j
    
#     def g(k): ##test / rewrite
#         if k == 0:
#             return np.array([0, 0, 0])
#         else:
#             return g(k-1) + ((edge_obj.flat_width - edge_obj.width) * np.cross(np.array([0,0,1]), (edge_vector / np.linalg.norm(edge_vector))))

    
#     L = np.cross(T(b_L - g(num-1)) * Q_3(phi_jk) * Q_1(alpha_jk * theta_jk),
#                  np.linalg.inv(Q_3(phi_jk)) * np.linalg.inv(T(b_L - g(num-1))), 
#                  T(b_R - g(num)) * Q_3(phi_jk) * Q_1((1 - alpha_jk) * theta_jk),
#                  np.linalg.inv(Q_3(phi_jk)) * np.linalg.inv(T(b_R - g(num)))
#                 )
    