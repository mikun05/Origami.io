import unittest
import numpy as np
from .smooth_fold_gens import SmoothFoldPattern
from ..data_extractors.crease_pattern import CreasePattern

class TestSmoothFoldPattern(unittest.TestCase):
    def setUp(self):
        """
        Set up the test with mock fold data.
        Waterbomb Base
        """
        self.crease_pattern = {
            "vertices_coords": [
                [0, 2, 0], [2, 2, 0], [2, 1, 0], [2, 0, 0], [0, 0, 0], [0, 1, 0], [1, 1, 0]
            ],
            "edges_vertices": [
                [0, 1], [0, 6], [1, 6], [0, 5], [1,2], [5,6], [6,2], [5,4], [6,4], [6,3], [2,3], [4,3]
            ],
            "faces_vertices": [
                [6,1,0], [6,2,1], [6,3,2], [6,4,3], [6,5,4], [6,0,5]
            ],
            "edges_assignment": [
                "B", "M", "M", "B", "B", "V", "V", "B", "M", "M", "B", "B",
            ]
        }
        
        self.simple_valley = {
            "vertices_coords": [
                [0,0,0], [0,1,0], [1,0,0], [0.5,0.5,1]
            ],
            "edges_vertices": [
               [0,1], [0, 2], [1,2], [2,3], [1,3]
            ],
            "faces_vertices": [
                [2,0,1], [3,2,1]
            ],
            "edges_assignment": [
                "B","B","V","B","B"
            ]
        }
        
        self.simple_mountain = {
            "vertices_coords": [
                [0,0,0], [0,1,0], [1,0,0], [0.5,0.5,-1]
            ],
            "edges_vertices": [
               [0,1], [0, 2], [1,2], [2,3], [1,3]
            ],
            "faces_vertices": [
                [2,0,1], [3,2,1]
            ],
            "edges_assignment": [
                "B","B","M","B","B"
            ]
        }
        
        self.water = SmoothFoldPattern(self.crease_pattern)  
        # self.valley = SmoothFoldPattern(self.simple_valley)   
        # self.mountain = SmoothFoldPattern(self.simple_mountain)        
     
      

    # def test_format_vertices_boundary(self):
    #     """
    #     Test the formatting of vertices and its edges as a numbered collection of smooth folds.
    #     Test for boundary vertex. surrounding edge objects should be empty
    #     The 6th vertex of this pattern is the only none boundary vertex
    #     """
    #     expected_vertex_objs = []
    #     result_vertex_objs = self.water.vertex_objects[0].surrounding_edges
    #     self.assertEqual(result_vertex_objs, expected_vertex_objs)
        
    # def test_format_vertices_non_boundary(self):
    #     """
    #     Test the formatting of vertices and its edges as a numbered collection of smooth folds.
    #     Test for boundary vertex. surrounding edge objects should be empty
    #     The 6th vertex of this pattern is the only none boundary vertex
    #     """
    #     expected_vertex_objs = []
    #     result_vertex_objs = self.water.vertex_objects[6].surrounding_edges
    #     self.assertNotEqual(result_vertex_objs, expected_vertex_objs)
        
    def test_format_vertices_enclosing_path(self):
        """
        Test the formatting of vertices and its edges as a numbered collection of smooth folds.
        Test the path around a vertex
        The 6th vertex of this pattern is the only none boundary vertex
        """
        expected_vertex_objs = []
        result_vertex_objs = self.water.vertex_objects[6].enclosing_path
        self.assertNotEqual(result_vertex_objs, expected_vertex_objs)
        
    # def test_vertex_edge_information(self):
    #     vob = self.water.vertex_objects[6].surrounding_edges[0]
    #     huh = ("id:", vob.id,
    #           "source", vob.source_vertex, 
    #           "co", vob.edge_coords,
    #           "pointer", vob.edge_pointer,
    #           "edge_vector",vob.edge_vector ,
    #           "curve_strength", vob.curve_strength,
    #           "flat_width",vob.flat_width ,
    #           "width",vob.width,
    #           "fold_type", vob.fold_type,
    #           "curve_angle", vob.curve_angle,
    #           "angle_from_vertex", vob.angle_from_vertex
    #     )        
    #     self.assertEqual(huh, '')

              


        

   
   
if __name__ == "__main__":
    unittest.main()