from flask import Blueprint, Flask, jsonify, request
from flask_cors import CORS
import json

from smooth_fold_gens import *
from edge_fold import *

app = Flask(__name__)
CORS(app)

# fold_bp = Blueprint('fold', __name__)

example_fold_data = { #this is the 3 squares one
            "vertices_coords": [
                [0, 0, 0], [10, 0, 0], [20, 0, 0], [30, 0, 0], [0, 10, 0], [10, 10, 0], [20, 10, 0], [30, 10, 0]
            ],
            "edges_vertices": [
                [0, 4], [0, 1], [4, 5], [1, 5], [1,2], [5,6], [2,6], [2,3], [6,7], [3,7]
            ],
            "faces_vertices": [
                [0,1,5,4], [1,2,6,5], [2,3,7,6]
            ],
            "edges_assignment": [
                "B", "B", "B", "V", "B", "B", "M", "B", "B", "B"
            ]
        }


pattern = SmoothFoldPattern(example_fold_data)


@app.route('/get-fold-pattern', methods=['GET'])
def get_fold_pattern():
    """API route to get the current fold pattern."""
    pattern = SmoothFoldPattern(example_fold_data)
    pattern_dict = pattern.to_dict()
    #print('p', pattern_dict.fold_format.vertices)
    return jsonify(pattern_dict)


@app.route('/get-vertex-info', methods=['GET'])
def get_vertex_info():
    """API route to get the current vertex info of the current fold pattern using vertex index."""
    data = request.json
    vertex_index = data.get("vertexIndex")

    vertex_obj = pattern.vertex_objects[vertex_index]
    return jsonify(vertex_obj.to_dict())


@app.route('/get-edge-info', methods=['GET'])
def get_edge_info():
    """API route to get the current vertex info of the current fold pattern using vertex index and edge index."""
    data = request.json
    vertex_index = data.get("vertexIndex")
    edge_index = data.get("edgeIndex")

    if edge_index is None or vertex_index is None:
        return jsonify({"error": "Missing parameters"}), 400

    edge_obj = pattern.vertex_objects[vertex_index].surrounding_edges[edge_index]
    return jsonify(edge_obj.to_dict())

    
@app.route('/fold-edge', methods=['POST'])
def fold_edge():
    """API route to fold an edge by a given angle and according to a given symmetry"""
    data = request.json
    vertex_index = data.get("vertexIndex")
    edge_index = data.get("edgeIndex")
    angle = data.get("angle")
    sym = data.get("sym")

    if edge_index is None | angle is None | vertex_index is None | sym is None:
        return jsonify({"error": "Missing parameters"}), 400

    # Perform the fold in backend
    pattern.fold_edge(edge_index, angle)
    bend_edge(pattern.vertex_objects[vertex_index].surrounding_edges[edge_index], angle, sym)
    #bend_edge(pattern.vertex_objects[vertex_index].surrounding_edges[edge_index], np.pi/2, 1)

    # Return updated fold pattern
    return jsonify(pattern.to_dict())


if __name__ == '__main__':
    app.run(debug=True)