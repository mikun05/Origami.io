import unittest
import numpy as np
from .smooth_fold_gens import SmoothFoldGeometry 

class TestSmoothFoldGeometry(unittest.TestCase):
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
                [0, 1], [0, 6], [1, 6], [0, 5], [1,2], [5,6], [6,2], [5,4], [6,4], [6,3], [2,3], [4,3]
            ],
            "faces_vertices": [
                [6,0,1], [6,1,2], [6,2,3], [6,3,4], [6,4,5], [6,5,0]
            ],
            "edges_assignment": [
                "B", "M", "M", "B", "B", "V", "V", "B", "M", "M", "B", "B",
            ]
        }
        self.geometry = SmoothFoldGeometry(self.fold_data)        
        

    def test_compute_face_normal(self):
        """
        Test the computation of face normals.
        """
        face = [6,0,1]  # Triangular face
        expected_normal = np.array([0,0,-1])  # Plane lies on z-axis Since face vertex are listed counter clockwise
        computed_normal = self.geometry.compute_face_normal(face)

        # Normalize to compare direction
        normalized_computed_normal = computed_normal / np.linalg.norm(computed_normal)
        normalized_expected_normal = expected_normal / np.linalg.norm(expected_normal)

        np.testing.assert_almost_equal(
            normalized_computed_normal, normalized_expected_normal,
            decimal=5, err_msg="Face normal computation failed."
        )

    def test_calculate_fold_angles(self):
        """
        Test calculating the fold angles (should be 0 for flat crease patterns).
        """
        faceA = [6,2,3]
        faceB = [6,4,3]
        expected_fold_angle = 0
        result_fold_angle = self.geometry.calculate_fold_angles(faceA, faceB)
        self.assertEqual(result_fold_angle, expected_fold_angle)

   
   
      
if __name__ == "__main__":
    unittest.main()