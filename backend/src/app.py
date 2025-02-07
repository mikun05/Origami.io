from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_cors import CORS, cross_origin

import numpy as np


from smooth_fold_gens import *
from edge_fold import *

app = Flask(__name__)
CORS(app)


three_square_fold_data = { 
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

water_bomb_base_fold_data = {
            "vertices_coords": [
                [0, 20, 0], [20, 20, 0], [20, 10, 0], [20, 0, 0], [0, 0, 0], [0, 10, 0], [10, 10, 0]
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

example_fold_data = water_bomb_base_fold_data


pattern = SmoothFoldPattern(example_fold_data)

@app.route('/get-fold-pattern', methods=['GET'])
def get_fold_pattern():
    """API route to get the current fold pattern."""
    pattern_dict = pattern.to_dict()
    print('p', pattern_dict['fold_format'][0]['vertices'])
    return jsonify(pattern_dict)


@app.route('/get-vertex-info', methods=['GET'])
def get_vertex_info():
    """API route to get the current vertex info of the current fold pattern using vertex index."""
    data = request.args
    vertex_index = data.get("vertexIndex", type=int)

    if vertex_index is None:
        return jsonify({"error": "Missing vertexIndex parameter"}), 400

    vertex_obj = pattern.vertex_objects[vertex_index]

    return jsonify(vertex_obj.to_dict())




@app.route('/get-edge-info', methods=['GET'])
def get_edge_info():
    """API route to get the current vertex info of the current fold pattern using vertex index and edge index."""
    data = request.args
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

    if edge_index is None or angle is None or vertex_index is None or sym is None:
        return jsonify({"error": "Missing parameters"}), 400

    converted_angle = np.deg2rad(angle)
    bend_edge(pattern.vertex_objects[vertex_index].surrounding_edges[edge_index], converted_angle, sym)
    
    pattern_dict = pattern.to_dict()
    print('fold', pattern_dict['fold_format'][0]['vertices'])

    return jsonify(pattern_dict)
    
    
@app.route('/reset-pattern', methods=['GET'])
def reset_pattern():
    """API route to fold an edge by a given angle and according to a given symmetry"""
    global pattern
    pattern = SmoothFoldPattern(example_fold_data)
    pattern_dict = pattern.to_dict()
    print('reset', pattern_dict['fold_format'][0]['vertices'])

    return jsonify(pattern_dict)
     



if __name__ == '__main__':
    app.run(debug=True)