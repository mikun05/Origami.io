import numpy as np
from app import *
from scipy import optimize


stiffness = 1e-9
paper_thickness = 0.0001
length_scale_factor = 0.025

E = 1e-9
t = 0.0001
ν = 0.33
L_star = 0.025


def split_into_triangles(source, panel, vertices, flat_vertices, bar_data):
    """Splits panels into triangles in the anticlockwise direction.
    Assumes panels are given in counter clockwise direction already
    
    Take panels as pointers to vertex point for ease
    Takes source as pointer to vertex point for ease
    """
    
    triangles = []
    num_edges = len(panel)
    
        
    for (i, point) in enumerate(panel):
        if panel[(i+1) % (num_edges)] != source  and panel[i] != source:
            triangles.append([source, point, panel[(i+1) % num_edges]])
            bar_data.append({
                "id": (source, point),
                "vector": np.array(vertices[point]) - np.array(vertices[source]),
                "face": [source, point, panel[(i+1) % num_edges]],        
                "area_contributions":  0, 
                "flat_length": np.linalg.norm(np.array(flat_vertices[point]) - np.array(flat_vertices[source])),
                "length": np.linalg.norm(np.array(vertices[point]) - np.array(vertices[source]))
            })
            
            # bar_data.append({
            #     "id": (source, panel[(i+1) % num_edges]),
            #     "vector": vertices[panel[(i+1) % num_edges]] - vertices[source],
            #     "face": [source, point, panel[(i+1) % num_edges]],        
            #     "area_contributions":  0, 
            #     "w_or_h": False
            # })
    # print(triangles)
    return(triangles)
    
def bar_stiffness_woodruff(bar, vertices, edges, uniform_angle):
    """This calcultaes the force on all bars based on the bar stiffness. 
    K_s = (E * A_e)/ L_e 
    A_e is the bar area
    L_e is the bar length
    
    Using the Woodruff estimation of bar area as in A bar and hinge model formulation for structural analysis of curved-crease origami - Woddruf et al
    
    Input is the bar as an edge vector, and the triangle, as a set of vertices. 
    Supposing a face as 5 vertices, we divide this into 3 triangles from the source vertex. 
    This results in 4 bars from the source vertex. 
    
    The cross-sectional area of the bar orthogonal to the traction (that is, the cross-sectional area of the top bar) must capture the cross-sectional area of the entire triangular pane
    
    Take triangles as pointers to vertex points for ease
    
    Woodruff defines bar stifness as area of triangle / L^2 * E
    """
    triangle = bar['face']

    
    a = np.array(vertices[triangle[0]])
    b = np.array(vertices[triangle[1]])
    c = np.array(vertices[triangle[2]])
    
    tri_area = 1/2 * np.linalg.norm(np.cross(c-a, b-a))
    bar_width= tri_area / (bar['length'])
    stiffness_scale = 1 if (bar['id'] in edges or [bar['id'][1], bar['id'][0]] in edges) else 1
    ##could also scale by difference in length befor and after bar changes
    
    # print('areas', area, bar['flat_length'])
    
    K_s = stiffness_scale * (t * stiffness  * bar_width) / (bar['length'] )
    print('kls', K_s)
    return( 1/2 * K_s * ((bar['flat_length'] - bar['length']) ** 2))


def calculate_bar_stiffnesses(vertex_objs, bar_data, uniform_angle):
    edges = vertex_objs[0].parent_crease.edges
    total_bar_stiffness = 0
    for vertex_obj in vertex_objs:
        for edge_obj in vertex_obj.surrounding_edges:
            vertices = edge_obj.parent_vertex.parent_crease.new_vertices
            flat_vertices = edge_obj.parent_vertex.parent_crease.flat_vertices

            source = edge_obj.id[0]
            split_into_triangles(source, edge_obj.faceR, vertices, flat_vertices, bar_data)
            
    vertices = vertex_objs[0].parent_crease.new_vertices
    
    for bar in bar_data:
        stiff = bar_stiffness_woodruff(bar, vertices, edges, uniform_angle)
        bar['area_contributions'] += stiff
        total_bar_stiffness += stiff
    print(total_bar_stiffness, 'bar')
    return total_bar_stiffness
        
    
def bar_stiffness_filipov(source, bar, vertices, stiffness):
    pass






def face_area(face, vertices):
    """
    Compute area of a flat polygon in 3D using fan triangulation.
    vertices: list of 3D points [v0, v1, v2, ..., vn]
    """
    if len(face) < 3:
        return 0.0  # Not a valid polygon

    area = 0.0
    v0 = np.array(vertices[face[0]])

    for i in range(1, len(face) - 1):
        v1 = np.array(vertices[face[i]])
        v2 = np.array(vertices[face[i + 1]])
        edge1 = v1 - v0
        edge2 = v2 - v0
        triangle_area = 0.5 * np.linalg.norm(np.cross(edge1, edge2))
        area += triangle_area

    return area

# print(face_area([3,4,5,2,1,0]))
    
    
def bend_stiffness(edge_obj, uniform_angle):
    angle_deviation = edge_obj.get_curve_angle() - uniform_angle
    print(angle_deviation)

    vertices = edge_obj.parent_vertex.parent_crease.new_vertices
    areaA = face_area(edge_obj.faceR, vertices)
    areaB = face_area(edge_obj.faceL, vertices)

    K_b = (( E * (t**3)) / 6) * ((edge_obj.get_length())**2/areaA+areaB)
    print('kb', K_b)
    return( 1/2 * K_b * (angle_deviation**2))                 


def calculate_bend_stiffnesses(vertex_objs, uniform_angle):
    total_bend_stiffness = 0
    for vertex_obj in vertex_objs:
        for edge_obj in vertex_obj.surrounding_edges:
            total_bend_stiffness += bend_stiffness(edge_obj, uniform_angle)
    
    print(total_bend_stiffness, 'bend')

    return total_bend_stiffness
            
# def fold_stiffness(edge_obj):
#     return (edge_obj.flat_length/length_scale_factor) * (stiffness*(paper_thickness**3) / 12)

def fold_stiffness(edge_obj, uniform_angle):
    angle_deviation = edge_obj.get_curve_angle() - uniform_angle
    
    L_f = edge_obj.flat_length

    k = (E * t**3) / (12 * (1 - ν**2))                   # Bending modulus
    K_ell = (L_f / L_star) * k                           # Local fold stiffness
    K_m = k * (L_f / t)**(1/3)                           # Max panel stiffness
    K_f = 1 / (1 / K_ell + 1 / K_m)     
    
    return(  1/2 * K_f * (angle_deviation**2))                 

    return (edge_obj.flat_length/length_scale_factor) * (stiffness*(paper_thickness**3) / 12) #* (angle_deviation ** 2)


def calculate_fold_stiffnesses(vertex_objs, uniform_angle):
    total_fold_stiffness = 0
    for vertex_obj in vertex_objs:
        for edge_obj in vertex_obj.surrounding_edges:
            total_fold_stiffness += fold_stiffness(edge_obj, uniform_angle)
    print(total_fold_stiffness, 'fold')

    return total_fold_stiffness

def total_stiffness_energy(flat_vertex_array, pattern_obj, uniform_angle):
    flat_vertices = np.array([flat_vertex_array[i] + v for (i,v) in enumerate(np.array(pattern_obj.geom.new_vertices).flatten().tolist())])
    reshaped_vertices = flat_vertex_array.reshape((-1, 3))

    bar_data = []
    # pattern_obj = SmoothFoldPattern(curr_pattern) 
    
    pattern_obj.geom.new_vertices = reshaped_vertices
    
    

    
    bend =  calculate_bend_stiffnesses(pattern_obj.vertex_objects, uniform_angle)
    fold = calculate_fold_stiffnesses(pattern_obj.vertex_objects, uniform_angle)
    bar = calculate_bar_stiffnesses(pattern_obj.vertex_objects, bar_data, uniform_angle)
    
    # print('tot', bend, fold, bar)
    total = bend+fold+bar
    # print('tot', 1e-3 * total)
    # print(1000000000000000 * total )
    return 1000000000000000 * total 

###so like newton raphson on the vertex points minimnising total stiffness???



def angle_constraints(new_vertices, intended_angle, pattern_obj):
    ssd = 0
    reshaped_vertices = new_vertices.reshape((-1, 3))
    
    pattern_obj.geom.new_vertices = reshaped_vertices
    
    for vertex_obj in pattern_obj.vertex_objects:
        for edge_obj in vertex_obj.surrounding_edges:
            ssd += (edge_obj.get_curve_angle() - intended_angle) ** 2
    print('ssd',ssd)
    
    return ssd
            
def slsqp_bar_hinge(initial_pattern_obj, uniform_angle):
    initial_vertices = np.array(initial_pattern_obj.geom.flat_vertices).flatten()

    result = optimize.minimize(
        total_stiffness_energy,
        initial_vertices,
        (initial_pattern_obj, uniform_angle),
        method='L-BFGS-B',  # or 'CG', 'BFGS', 'trust-constr'
        options={'maxiter': 1000, 'disp': True, 'ftol':1e-12, 'eps':1e-15}
    )

        
    # constraints = [{
    # 'type': 'eq',
    # 'fun': lambda h: total_stiffness_energy(h, initial_pattern_obj, uniform_angle)
    # }]

    # result = optimize.minimize(
    #     angle_constraints,
    #     initial_vertices,
    #     (uniform_angle, initial_pattern_obj),
    #     constraints=constraints,
    #     method='SLSQP',  # or 'CG', 'BFGS', 'trust-constr'
    #     options={'maxiter': 100, 'disp': True}
    # )

    print(result)
    print(result.x)
    
    print(initial_pattern_obj.geom.new_vertices)
    initial_pattern_obj.geom.new_vertices = initial_pattern_obj.geom.new_vertices.tolist()

# def change_vertex_check(pattern_obj):
#     print('be',pattern_obj.vertex_objects[6].parent_crease.new_vertices)
#     pattern_obj.geom.new_vertices = [[a*10,b*10,c*10] for [a,b,c] in pattern_obj.geom.new_vertices]
    
#     print('dur', pattern_obj.geom.new_vertices)
    
#     print('af', pattern_obj.vertex_objects[6].parent_crease.new_vertices)
#     print('af flat', pattern_obj.vertex_objects[6].parent_crease.flat_vertices)
#     print('edges', pattern_obj.vertex_objects[6].surrounding_edges[0].length)
#     print('edges', pattern_obj.vertex_objects[6].surrounding_edges[0].get_length())



# change_vertex_check(initial_pattern_obj)