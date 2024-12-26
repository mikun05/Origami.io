import numpy as np
from src.data_extractors.crease_pattern import CreasePattern

class SmoothFoldGeometry(CreasePattern):
    def compute_face_normal(self, face):
        """
        Compute the normals for a face.
        The cross product of two non-parallel edges of the face
        """
        
        face_edges = self.get_face_edges(face)
        
        non_parallel_edges = [e for e in face_edges if face[0] in e] ##gets all edges that share a vertex in face ... necessarily non-parallel
        
        if len(non_parallel_edges) != 2:
            print('Calc Error: Number of edges meeting at face vertex should be 2')
        else:
            [edge1, edge2] = self.convert_to_actual_coords(non_parallel_edges)
            
        e1 = np.array(edge1[0] if edge1[1] == face[0] else edge1[1]) - np.array(self.vertices[face[0]])
        e2 = np.array(edge2[0] if edge2[1] == face[0] else edge2[1]) - np.array(self.vertices[face[0]])
        
        return np.cross(e1, e2)
              
    def calculate_fold_angles(self, faceA, faceB):
        """
        Compute the dihedral angle between two faces
        This is called by another function which takes an edge as parameter, and finds the two faces which share that edge
        (implement later) If the edge is a valley, this is positive, if it is a mountain, this is negative
        """
        
        n1 = self.compute_face_normal(faceA)
        n2 = self.compute_face_normal(faceB)
        
        normalized_1 = n1 / np.linalg.norm(n1)
        normalized_2 = n2 / np.linalg.norm(n2)
        
        dot_product = np.dot(normalized_1, normalized_2)
        
        angle = np.arccos(dot_product)
        
        fold_angle = np.pi - angle

        return fold_angle
    