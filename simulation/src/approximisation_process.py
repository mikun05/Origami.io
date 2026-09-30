from angle_optimisation import *
from bar_and_hinge_folds import *
angleApprox = {}
vertexApprox = {}

def approx_process(model, angleApprox_info, vertexApprox_info, pattern_obj, vertex_index, vertices, uniform_angle):
    angleApprox = angleApprox_info
    vertexApprox = vertexApprox_info
    results = {}
    vertex_obj = vertices[vertex_index]
    
    edge_start_dict = {}
    pos = 0
    for (i, vert) in enumerate(vertices):        
        if not vert.isBoundary:
            edge_start_dict[i] = pos
            pos += len(vert.surrounding_edges)
            
            
            
    print('XXXXXXXXXXXXXedge start dict', edge_start_dict)
        
    vertex_points_start = pattern_obj.geom.new_vertices.copy()
    
    print('ANGLE APPROXIMATION WITH', angleApprox['angleApproxMeth'])
    print('model', model)
    if model == 'CRR':
        
        match angleApprox['angleApproxMeth']:
            case 'NA':
                new_angles = [uniform_angle] * len(vertex_obj.surrounding_edges)
            case 'GD':
                new_angles = gradient_descent(vertex_obj, uniform_angle, maxiter=angleApprox['angleMaxIt'])
            case 'LBFGS':
                new_angles = re_vamped_lbfg(vertex_index, vertices, edge_start_dict, uniform_angle, maxiter=angleApprox['angleMaxIt'], ftol=angleApprox['angleFTol'], eps=angleApprox['angleEps'])
                #new_angles = l_bfgs_b(vertex_obj, uniform_angle, maxiter=angleApprox['angleMaxIt'], ftol=angleApprox['angleFTol'], eps=angleApprox['angleEps'])
            case 'Pos_Anneal_LBFGS':
                new_angles = annealing_optimiser(vertex_obj, uniform_angle, maxiter=angleApprox['angleMaxIt'], ftol=angleApprox['angleFTol'], eps=angleApprox['angleEps'])
            case 'Neg_Anneal_LBFGS':
                new_angles = annealing_optimiser_dec(vertex_obj, uniform_angle, maxiter=angleApprox['angleMaxIt'], ftol=angleApprox['angleFTol'], eps=angleApprox['angleEps'])
            case 'SQP':
                new_angles = slsq(vertex_index, vertices, edge_start_dict, uniform_angle, maxiter=angleApprox['angleMaxIt'], ftol=angleApprox['angleFTol'], eps=angleApprox['angleEps'])
        print('COMPLETED ANGLE APPROXIMATION WITH', angleApprox['angleApproxMeth'])
        print('new_angles', new_angles)

        #if vertexApprox['vertexPointMeth'] == 'Rot':
        print('BEGIN FACE ROTATION')
        vertex_points = bend_around_vertex(vertices, vertex_index, edge_start_dict, np.array(new_angles, dtype=np.float64), final=True)
        print('COMPLETED FACE ROTATION')

        # elif vertexApprox['vertexPointMeth'] == 'SQP':
        #     print('VERTEX POIN APPROXIMATION WITH SQP FACE ROTATION')
        #     vertex_points = vertex_slsq(vertex_obj, np.array(new_angles, dtype=np.float64), maxiter=vertexApprox['vertexMaxIt'], ftol=vertexApprox['vertexFTol'], eps=vertexApprox['vertexEps'])
        #     print('COMPLETED VERTEX POIN APPROXIMATION WITH SQP FACE ROTATION')

        print(vertex_points)
        new_angles = []
        for vert in vertices:
            if not (vert.isBoundary):
                new_angles += [ang.item() for ang in get_new_angles(vert)]
                
        print('nrew', new_angles)
        
        results['vertex_points'] = vertex_points_start
        results['angle_approx_loop_closure'] = f"{float(norm_compute_transformations(vertex_index, vertices, edge_start_dict[vertex_index], new_angles, 0)[1]):.{8}g}"
        results['angle_approx_loop_closure_matrix'] = [[f"{float(item):.{3}g}" for item in row] for row in norm_compute_transformations(vertex_index, vertices, edge_start_dict[vertex_index], new_angles, 0)[0].tolist()]

        results['vertex_approx_new_angles'] = new_angles
        results['dist_from_angle_results'] =     f"{float(vertex_points['mean']):.{8}g}"
        results['total_edge_deviation'] =     f"{float(vertex_points['obj_length']):.{8}g}"
        results['total_sector_angle_deviation'] =     f"{float(vertex_points['sec_size']):.{8}g}"

        print(results)
    
    else:
        slsqp_bar_hinge(pattern_obj, uniform_angle)
        results['vertex_points'] = vertex_points_start

        results['angle_approx_loop_closure'] = 0
        results['angle_approx_loop_closure_matrix'] = [[0,0,0],[0,0,0],[0,0,0]]

        results['vertex_approx_new_angles'] = []
        results['dist_from_angle_results'] =    0
        results['total_edge_deviation'] =  0
        results['total_sector_angle_deviation'] =     0
    return results

def begin_approx(foldInfo):
    if angleApprox['angleApproxMeth'] == 'SQP':
        pass
    
    
def interp_anim_process(start_vertices, end_vertices, steps):
    all_steps = []
    n = len(start_vertices)
    
    start = [np.array(v) for v in start_vertices]
    end = [np.array(v) for v in end_vertices]

    for i in range(steps+1):
        frac = i / steps
        step_vertices = []
        for j in range(n):
            interp_v = (((end[j] - start[j]) * frac) 
                        + start[j]).tolist()
            step_vertices.append(interp_v)
        all_steps.append(step_vertices)
        
    return all_steps