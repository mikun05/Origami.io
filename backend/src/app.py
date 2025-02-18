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
                [-10, 10, 0], [10, 10, 0], [10, 0, 0], [10, -10, 0], [-10, -10, 0], [-10, 0, 0], [0, 0, 0]
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

book_fold = {
    "vertices_coords": [
                [-10, 10, 0], [10, 10, 0], [10, 0, 0], [10, -10, 0], [-10, -10, 0], [-10, 0, 0], [0, 0, 0]
    ],
    "edges_vertices": [
        [0, 1], [0, 5], [1,2], [5,6], [5,4], [6,2], [2,3], [4,3]
    ],
    "faces_vertices": [
        [6,2,1,0,5], [6,5,4,3,2]
    ],
    "edges_assignment": [
        "B", "B", "B", "V", "B", "V", "B", "B"
    ]
}

miura_ori_fold = {
    "vertices_coords": [
        [-10,-4,0], [-4,-4,0], [2,-4,0], [-6,0,0], [0,0,0], [6,0,0], [-10,4,0], [-4,4,0], [2,4,0]
    ],
    "edges_vertices": [
        [6, 7], [7, 8], [3,4], [4,5], [0,1], [1,2], [6, 3], [7, 4], [8,5], [3,0], [4,1], [5,2]
    ],
    "faces_vertices": [
        [4,7,6,3], [4,5,8,7], [4,3,0,1], [4,1,2,5]
    ],
    "edges_assignment": [
        "B", "B", "V", "M", "B", "B", "B", "M", "B", "B", "M", "B"
    ]
}

twist ={
    "file_spec": 1,
    "file_creator": "Mathematica",
    "file_author": "Thomas Hull",
    "file_classes": ["singleModel"],
    "frame_title": "Rigidly folded square twist",
    "frame_classes": ["foldedForm"],
    "frame_attributes": ["3D"],
    "vertices_coords": [
        [0, 0, 0],
        [10, 0, 0],
        [10, 20, 0],
        [0, 20, 0],
        [18.7, 0, -4.97],
        [38.7, 0, -4.97],
        [38.7, 10, -4.97],
        [18.7, 10, -4.97],
        [28.7, 14.16, 4.13],
        [38.7, 14.16, 4.13],
        [38.7, 34.16, 4.13],
        [28.7, 34.16, 4.13],
        [0, 34.16, 9.09],
        [0, 24.16, 9.09],
        [20, 24.16, 9.09],
        [20, 34.16, 9.09]
    ],
    "faces_vertices": [
        [0, 1, 2, 3],
        [1, 4, 7, 2],
        [4, 5, 6, 7],
        [7, 6, 9, 8],
        [8, 9, 10, 11],
        [15, 14, 8, 11],
        [12, 13, 14, 15],
        [3, 2, 14, 13],
        [2, 7, 8, 14]
    ],
    "edges_vertices": [
        [0, 1],
        [1, 2],
        [2, 3],
        [3, 0],
        [4, 5],
        [5, 6],
        [6, 7],
        [7, 4],
        [8, 9],
        [9, 10],
        [10, 11],
        [11, 8],
        [12, 13],
        [13, 14],
        [14, 15],
        [15, 12],
        [2, 7],
        [7, 8],
        [8, 14],
        [14, 2],
        [3, 13],
        [1, 4],
        [6, 9],
        [11, 15]
    ],
    "edges_assignment": [
        "B",
        "M",
        "V",
        "B",
        "B",
        "B",
        "V",
        "V",
        "M",
        "B",
        "B",
        "V",
        "B",
        "M",
        "M",
        "B",
        "V",
        "M",
        "M",
        "V",
        "B",
        "B",
        "B",
        "B"
    ]
}

example_fold_data = miura_ori_fold

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
    
    for edge_obj in vertex_obj.surrounding_edges:
        edge_obj.update_edge()

    return jsonify(vertex_obj.to_dict())



@app.route('/get-edge-info', methods=['GET'])
def get_edge_info():
    """API route to get the current vertex info of the current fold pattern using vertex index and edge index."""
    data = request.args
    vertex_index = int(data.get("vertexIndex"))
    edge_index = int(data.get("edgeIndex"))
    
    if edge_index is None or vertex_index is None:
        return jsonify({"error": "Missing parameters"}), 400
    
    vertex_obj = pattern.vertex_objects[vertex_index]
    
    for edge_obj in vertex_obj.surrounding_edges:
        edge_obj.update_edge()
    
    vertex_edge_objects = pattern.vertex_objects[vertex_index].surrounding_edges
    
    edge_obj_rel_vertex = next((item for item in vertex_edge_objects if item.edge_index == edge_index), None)#gets the edge index relative to the vertex

    # edge_obj = pattern.vertex_objects[vertex_index].surrounding_edges[edge_index_rel_vertex]
    
    return jsonify(edge_obj_rel_vertex.to_dict())

    
    
@app.route('/fold-edge', methods=['POST'])
def fold_edge():
    """API route to fold an edge by a given angle and according to a given symmetry"""
    data = request.json
    vertex_index = data.get("vertexIndex")
    edge_index = data.get("edgeIndex")
    angle = data.get("angle")
    sym = data.get("sym")
    
    vertex_edge_objects = pattern.vertex_objects[vertex_index].surrounding_edges
    
    edge_obj_rel_vertex = next((item for item in vertex_edge_objects if item.edge_index == edge_index), None)#gets the edge index relative to the vertex

    if edge_index is None or angle is None or vertex_index is None or sym is None:
        return jsonify({"error": "Missing parameters"}), 400

    converted_angle = np.deg2rad(angle)
    bend_edge(edge_obj_rel_vertex, converted_angle, sym)
    
    for vertex_obj in pattern.vertex_objects:
        for edge_obj in vertex_obj.surrounding_edges:
            edge_obj.update_edge()
    
    pattern_dict = pattern.to_dict()
    print('fold', pattern_dict['fold_format'][0]['vertices'])

    return jsonify(pattern_dict)



@app.route('/fold-edge-around-vertex', methods=['POST'])
def fold_edges_around_vertex():
    """API route to fold an edge by a given angle and according to a given symmetry"""
    data = request.json
    vertex_index = data.get("vertexIndex")
    angle = data.get("angle")
    sym = data.get("sym")

    if angle is None or vertex_index is None or sym is None:
        return jsonify({"error": "Missing parameters"}), 400

    converted_angle = np.deg2rad(angle)
    
    bend_around_vertex(pattern.vertex_objects[vertex_index], converted_angle)
        
 
    
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