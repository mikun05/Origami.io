from flask import Flask, redirect, render_template, request, jsonify, url_for
from flask_cors import CORS, cross_origin

import numpy as np


from smooth_fold_gens import *
from edge_fold import *
from angle_optimisation import *
from approximisation_process import *
import time


app = Flask(__name__)
CORS(app)


three_square_fold_data = { 
            "vertices_coords": [
                [0, 0, 0], [10, 0, 0], [20, 0, 0], [30, 0, 0], [0, 10, 0], [10, 10, 0], [20, 10, 0], [30, 10, 0], [10,5,0], [20,5,0]
            ],
            "edges_vertices": [
                [0, 4], [0, 1], [4, 5], [1, 8],[8,5], [1,2], [5,6], [2,9], [9,6], [2,3], [6,7], [3,7]
            ],
            "faces_vertices": [
                [0,1,8,5,4], [1,2,9,6,5,8], [2,3,7,6,9]
            ],
            "edges_assignment": [
                "B", "B", "B", "V", "V", "B", "B", "M", "M", "B", "B", "B"
            ]
        }

four_square_fold_data = { 
            "vertices_coords": [
                [0, 0, 0], [10, 0, 0], [20, 0, 0], [30, 0, 0], [0, 10, 0], [10, 10, 0], [20, 10, 0], [30, 10, 0], [10,5,0], [20,5,0], [40,0,0], [40,10,0], [40,5,0], [30,5,0]
            ],
            "edges_vertices": [
                [0, 4], [0, 1], [4, 5], [1, 8],[8,5], [1,2], [5,6], [2,9], [9,6], [2,3], [6,7], [3,13],[13,7], [7,10],[3,11], [10,12], [12,11]
            ],
            "faces_vertices": [
                [0,1,8,5,4], [1,2,9,6,5,8], [2,3,13,7,6,9], [3,11,12,10,7,13]
            ],
            "edges_assignment": [
                "B", "B", "B", "V", "V", "B", "B", "M", "M", "B", "B", "V","V", "B", "B", "B", "B"
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

#Single Vertexed

# Generate 11 outer vertices on a circle of radius 10
radius = 10
n = 16
angle_step = 2 * np.pi / n

ico_star = {
    "vertices_coords": [[0, 0, 0]],  # center vertex (0)
    "edges_vertices": [],
    "faces_vertices": [],
    "edges_assignment": []
}

# Add outer vertices (1 to 11)
for i in range(n):
    angle = i * angle_step
    x = round(radius * np.cos(angle), 5)
    y = round(radius * np.sin(angle), 5)
    ico_star["vertices_coords"].append([x, y, 0])

# Add radial creases (center to outer vertices)
for i in range(1, n + 1):
    ico_star["edges_vertices"].append([0, i])
    assignment = "M" if i % 2 == 1 else "V"
    ico_star["edges_assignment"].append(assignment)

# Add outer ring edges and boundary assignments
for i in range(1, n + 1):
    next_i = i + 1 if i < n else 1
    ico_star["edges_vertices"].append([i, next_i])
    ico_star["edges_assignment"].append("B")

# Add triangular faces (center, vertex i, vertex i+1)
for i in range(1, n + 1):
    next_i = i + 1 if i < n else 1
    ico_star["faces_vertices"].append([0, i, next_i])


wbb = { #waterbomb base
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
                "B", "V", "V", "B", "B", "M", "M", "B", "V", "V", "B", "B",
            ]
        }

other_traingle = {
            "vertices_coords": [
                [-10, 10, 0], [10, 10, 0], [10, 0, 0], [10, -10, 0], [-10, -10, 0], [-10, 0, 0], [0, 0, 0], [0, 10, 0], [0, -10, 0]
            ],
            "edges_vertices": [
                [0, 1], [0, 6], [1, 6], [0, 5], [1,2], [5,6], [6,2], [5,4], [6,4], [6,3], [2,3], [4,3], [6,7], [6,8]
            ],
            "faces_vertices": [
                [6,7,0], [6,1,7], [6,2,1], [6,3,2], [6,8,3], [6,4,8], [6,5,4], [6,0,5]
            ],
            "edges_assignment": [
                "B", "V", "V", "B", "B", "M", "M", "B", "V", "V", "B", "B", "M", "M"
            ]
        }

bf = { 
    "vertices_coords": [
        [0, 20, 0], [20, 20, 0], [20, 10, 0], [20, 0, 0], [0, 0, 0], [0, 10, 0], [10, 10, 0]
       # [-10, 10, 0], [10, 10, 0], [10, 0, 0], [10, -10, 0], [-10, -10, 0], [-10, 0, 0], [0, 0, 0]
    ],
    "edges_vertices": [
        [0, 1], [0, 5], [1, 2], [5, 6], [5, 4], [6, 2], [2, 3], [4, 3]
    ],
    "faces_vertices": [
        [6, 2, 1, 0, 5], [6, 5, 4, 3, 2]
    ],
    "edges_assignment": [
        "B", "B", "B", "M", "B", "M", "B", "B"
    ]
}

mo_single = { #muira ori fold single vertex
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


#Multi Vertexed
two_miura_ori_fold = {
    "vertices_coords": [
        [-10,-4,0], [-4,-4,0], [2,-4,0], [-6,0,0], [0,0,0], [6,0,0], [-10,4,0], [-4,4,0], [2,4,0], [8,4,0], [12,0,0], [8,-4,0]
    ],
    "edges_vertices": [
        [6, 7], [7, 8], [3,4], [4,5], [0,1], [1,2], [6, 3], [7, 4], [8,5], [3,0], [4,1], [5,2], [5,10], [8,9], [9,10], [10,11], [2,11]
    ],
    "faces_vertices": [
        [4,7,6,3], [4,5,8,7], [4,3,0,1], [4,1,2,5],[5,2,11,10], [5,10,9,8]
    ],
    "edges_assignment": [
        "B", "B", "M", "V", "B", "B", "B", "V", "M", "B", "V", "M", "M", "B", "B", "B", "B"
    ]
}

belcastro_fig_2 = {
    "vertices_coords": [
        [0,0,0], [10,0,0], [10,10,0], [0,10,0], [-10,10,0], [-10,0,0], [-10,-10,0], [0,-10,0], [10,-10,0]
    ],
    "edges_vertices": [
        [0,1],[0,3],[0,5],[0,6],[0,7],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,8],[8,1]
    ],
    "faces_vertices": [
        [0,3,4,5],[0,5,6],[0,6,7],[0,7,8,1],[0,1,2,3]
    ],
    "edges_assignment": [
        "V", "V", "V", "M", "V", "B", "B", "B", "B", "B", "B", "B", "B"
    ]
}

belcastro_fig_2_a = {
    "vertices_coords": [
        [0,0,0], [10,0,0], [10,10,0], [0,10,0], [-10,10,0], [-10,0,0], [-10,-10,0], [10,-10,0]
    ],
    "edges_vertices": [
        [0,1],[0,3],[0,5],[0,6],[0,7],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,1]
    ],
    "faces_vertices": [
        [0,1,2,3], [0,3,4,5], [0,5,6], [0,6,7], [0,7,1]
    ],
    "edges_assignment": [
        "M", "M", "M", "V", "M", "B", "B", "B", "B", "B", "B", "B"
    ]
}


all_patterns = {
    'wbb': wbb,
    'bf': bf,
    'mo_single': mo_single,
    'bel_fig_2': belcastro_fig_2,
    'mo_double': two_miura_ori_fold,
    'three_sq': three_square_fold_data,
    'four_sq': four_square_fold_data,
    'ico_star': ico_star,
    'bel_fig_2_A': belcastro_fig_2_a,

}



global pattern, patternId
patternId = 'wbb'
pattern = SmoothFoldPattern(wbb)

@app.route('/get-fold-pattern', methods=['POST'])
def get_fold_pattern():
    """API route to get the current fold pattern."""
    global pattern, patternId
    data = request.json
    patternId = data.get("patternId")
    
    print('patternid')
    print('patternId', patternId)
    if patternId is None:
        patternId = 'wbb'
        pattern = SmoothFoldPattern(wbb)
        
    pattern = SmoothFoldPattern(all_patterns[patternId])

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
    
    print('app',data.get("angleApproxMeth"), "SQP" )
    angleApprox_info = {
        'angleApproxMeth': data.get("angleApproxMeth", "SQP"),
        'angleMaxIt': data.get("angleMaxIt", 200),
        'angleFTol': data.get("angleFTol", 1e-10),
        'angleEps': data.get("angleEps", 1e-14),
    }
   

    vertexApprox_info = {
        'vertexPointMeth': data.get("vertexPointMeth", "Rot"),
        'vertexMaxIt': data.get("vertexMaxIt", 300),
        'vertexFTol': data.get("vertexFTol", 1e-8),
        'vertexEps': data.get("vertexEps", 1e-8),
    }


    if edge_index is None or angle is None or vertex_index is None or sym is None:
        return jsonify({"error": "Missing parameters"}), 400

    converted_angle = np.deg2rad(angle)
    vertex_obj = pattern.vertex_objects[vertex_index]

    results = slsq_specific_edge(pattern.vertex_objects, vertex_index, converted_angle, edge_obj_rel_vertex.id[1], maxiter=200, ftol=1e-10, eps=1e-15) #bend_edge(edge_obj_rel_vertex, converted_angle, sym)
    
    # for vertex_obj in pattern.vertex_objects:
    #     for edge_obj in vertex_obj.surrounding_edges:
    #         edge_obj.update_edge()
    
    pattern_dict = pattern.to_dict()
    print('fold', pattern_dict['fold_format'][0]['vertices'])
    fold_output = {
        'pattern': pattern_dict,
        'approx_results': results
    }
    return jsonify(fold_output)


@app.route('/fold-edge-around-vertex', methods=['POST'])
def fold_edges_around_vertex():
    """API route to fold an edge by a given angle and according to a given symmetry"""
    data = request.json
    vertex_index = data.get("vertexIndex")
    angle = data.get("angle")
    sym = data.get("sym")
    slider = data.get("slider")
    model = data.get('origamiModel')
    
    print('slkide', slider)
    
    #print('app',data.get("angleApproxMeth"), "SQP" )
    angleApprox_info = {
        'angleApproxMeth': data.get("angleApproxMeth", "SQP"),
        'angleMaxIt': data.get("angleMaxIt", 200) if not slider else 0,
        'angleFTol': data.get("angleFTol", 1e-10),
        'angleEps': data.get("angleEps", 1e-14),
    }
   

    vertexApprox_info = {
        'vertexPointMeth': data.get("vertexPointMeth", "Rot"),
        'vertexMaxIt': data.get("vertexMaxIt", 300),
        'vertexFTol': data.get("vertexFTol", 1e-8),
        'vertexEps': data.get("vertexEps", 1e-8),
    }


    if angle is None or vertex_index is None or sym is None:
        return jsonify({"error": "Missing parameters"}), 400

    converted_angle = np.deg2rad(angle)
    
    tic = time.perf_counter()
    results = approx_process(model, angleApprox_info, vertexApprox_info, pattern, vertex_index, pattern.vertex_objects, converted_angle)
    toc = time.perf_counter()

    #l_bfgs_b(pattern.vertex_objects[vertex_index], converted_angle)

    #bend_around_vertex(pattern.vertex_objects[vertex_index], converted_angle)
        
 
    
    
    pattern_dict = pattern.to_dict()
    print('fold', pattern_dict['fold_format'][0]['vertices'])
    fold_output = {
        'pattern': pattern_dict,
        'approx_results': results,
        'duration': toc-tic
    }
    return jsonify(fold_output)

    
    
@app.route('/reset-pattern', methods=['GET'])
def reset_pattern():
    """API route to fold an edge by a given angle and according to a given symmetry"""
    global pattern, patternId
    pattern = SmoothFoldPattern(all_patterns[patternId])
    pattern_dict = pattern.to_dict()
    print('reset', pattern_dict['fold_format'][0]['vertices'])

    return jsonify(pattern_dict)
     


if __name__ == '__main__':
    app.run(debug=True)