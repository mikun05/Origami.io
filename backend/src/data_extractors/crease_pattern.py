import numpy as np
class CreasePattern:
    def __init__(self, fold_data):
        """
        Initialize the crease pattern with the FOLD format data.
        """
        self.vertices = fold_data.get('vertices_coords', [])
        self.edges = fold_data.get('edges_vertices', [])
        self.faces = fold_data.get('faces_vertices', [])
        self.edges_assignments = fold_data.get('edges_assignment', [])
        #self.fold_angles = fold_data.get('edges_foldAngle', [])
        
    def is_equal(self, arr1, arr2):
        return np.all(np.sort(np.array(arr1)) == np.sort(np.array(arr2)))
    
    def is_in(self, elem, arr):
        for i in arr:
            if self.is_equal(elem, i):
                return True
        return False
          
    def get_faces_surrounding_edge(self, edge):
        """
        Find the faces sharing an edge
        """
        pos = self.edges.index(edge)
        adj_faces = []
        
        if (pos == -1):
            print('This edge does not exist')
        elif (self.edges_assignments[pos] == 'B'):
            print('This edge is at the boundary')
        else:
            for face in self.faces:
                face_edges = self.get_face_edges(face)
                if self.is_in(edge, face_edges):
                    adj_faces.append(face)
                    
        return adj_faces            
                
    def get_edges_surrounding_vertex(self, vertex):
        """
        Find the edges around a vertex
        """
        pos = self.vertices.index(vertex)
        adj_edges = []
        
        if (pos == -1):
            print('This vertex does not exist')
        else:
            for edge in self.edges:
                if pos in edge:
                    adj_edges.append(edge) ##improve later to group edges next to each other
                    
        return adj_edges    
    
    def get_face_edges(self, face):
        """
        Obtain all edges of a face.
        Vertices of face patterns are given in counterclockwise order from .fold format. So to get all edges, we can loop through adjacent pairs of vertices
        On the face, and then connect the last to the first as the final edge.
        Output as pointers to vertex set
        """
        
        number_of_vertices = len(face)
        face_edges = []

        
        for i in range(number_of_vertices - 1):
            face_edges.append([face[i], face[i+1]])
        
        face_edges.append([face[-1], face[0]])
          
        return face_edges
    
    def convert_to_actual_coords(self, list_rep):
        """
        faces, and edges are represented according to the indices of the vertices. 
        This function converts the representation list to the list using the actual coordintes of each vertex
        """
        
        ## [[a]] -> [[[v1, v2, v3]]]
        actual = []
        if (list_rep == []):
            return actual
        elif (isinstance(list_rep[0], list)):
            actual = [[self.vertices[ind] for ind in ls] for ls in list_rep]
        else:
            actual = [self.vertices[ind] for ind in list_rep]
        
        return actual
    
    def check_adjacent_edges(self, edgeA, edgeB):
        if edgeA == edgeB:
            return (False, [])
        
        faces_shared = list(set( self.get_faces_surrounding_edge(edgeA)).intersection( self.get_faces_surrounding_edge(edgeB)))
        
        #it is possible to have two distinct faces_i,j for edges m_i, m_j but this would not be a valid crease pattern (or at least it would then have curved edges which we are not ehre concerend with)
        if faces_shared != []:
            return (True, faces_shared)
        
        return (False, [])
        
