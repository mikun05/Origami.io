import unittest
from .crease_pattern import CreasePattern 

class TestCreasePattern(unittest.TestCase):
    def setUp(self):
        """
        Set up the test with mock fold data.
        Waterbomb Base
        """
        self.fold_data = {
            "vertices_coords": [
                [0, 2, 0], [2, 2, 0], [2, 1, 0], [2, 0, 0], [0, 0, 0], [0, 1, 0], [1, 1, 0]
            ],
            "edges_vertices": [
                [0, 1], [0, 6], [6,1], [5, 0], [2,1], [5,6], [6,2], [4,5], [4,6], [6,3], [3,2], [4,3]
            ],
            "faces_vertices": [
                [6,0,1], [6,1,2], [6,2,3], [6,3,4], [6,4,5], [6,5,0]
            ],
            "edges_assignment": [
                "B", "M", "M", "B", "B", "V", "V", "B", "M", "M", "B", "B",
            ]
        }
        self.cp = CreasePattern(self.fold_data)
        

    def test_get_faces_surrounding_edge(self):
        """
        Test finding faces surrounding a given edge.
        """
        edge = [6, 2]
        expected_faces = [[6, 1, 2], [6, 2, 3]]
        result_faces = self.cp.get_faces_surrounding_edge(edge)
        self.assertEqual(result_faces, expected_faces)

    def test_get_edges_surrounding_vertex(self):
        """
        Test finding edges surrounding a vertex.
        """
        vertex = [1, 1, 0]
        expected_edges = [[0, 6], [6, 1], [5 ,6], [6, 2], [4, 6], [6, 3]]
        result_edges = self.cp.get_edges_surrounding_vertex(vertex)
        self.assertEqual(result_edges, expected_edges)
        
        
    def test_convert_to_actual_coords_normal_case(self):
        """
        Test converting to actual coords
        """
        list_rep = [[6,0,1], [6,1,2], [6,2,3]]
        expected_edges = [[[1, 1, 0], [0, 2, 0], [2, 2, 0]], [[1, 1, 0], [2, 2, 0], [2, 1, 0]], [[1, 1, 0], [2, 1, 0], [2, 0, 0]]]
        result_edges = self.cp.convert_to_actual_coords(list_rep)
        self.assertEqual(result_edges, expected_edges)
        
    
    def test_convert_to_actual_coords_null_case(self):
        """
        Test converting to actual coords 
        """
        list_rep = []
        expected_edges = []
        result_edges = self.cp.convert_to_actual_coords(list_rep)
        self.assertEqual(result_edges, expected_edges)
        
        
    def test_convert_to_actual_coords_1d_case(self):
        """
        Test converting to actual coords 
        """
        list_rep = [6,0,1]
        expected_edges = [[1, 1, 0], [0, 2, 0], [2, 2, 0]]
        result_edges = self.cp.convert_to_actual_coords(list_rep)
        self.assertEqual(result_edges, expected_edges)

   
   
      
if __name__ == "__main__":
    unittest.main()