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
                if edge in face_edges:
                    adj_faces.append(face)
                    
        return adj_faces            
                
    def get_edges_surrounding_vertex(self, vertex):
        """
        Find the faces sharing a vertex
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
        Obtain all edges of a face
        """
        face_edges = []
        
        for (i,u) in enumerate(face):
            for v in face[i:]:
                if ([u,v] in self.edges) | ([v,u] in self.edges):
                    face_edges.append([u,v])
                    
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