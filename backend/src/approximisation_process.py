from angle_optimisation import *
angleApprox = {}
vertexApprox = {}

def approx_process(angleApprox_info, vertexApprox_info, vertex_obj, uniform_angle):
    angleApprox = angleApprox_info
    vertexApprox = vertexApprox_info
    results = {}
    
    print('ANGLE APPROXIMATION WITH', angleApprox['angleApproxMeth'])
    match angleApprox['angleApproxMeth']:
        case 'GD':
            new_angles = gradient_descent(vertex_obj, uniform_angle, maxiter=angleApprox['angleMaxIt'])
        case 'LBFGS':
            new_angles = l_bfgs_b(vertex_obj, uniform_angle, maxiter=angleApprox['angleMaxIt'], ftol=angleApprox['angleFTol'], eps=angleApprox['angleEps'])
        case 'Pos_Anneal_LBFGS':
            new_angles = annealing_optimiser(vertex_obj, uniform_angle, maxiter=angleApprox['angleMaxIt'], ftol=angleApprox['angleFTol'], eps=angleApprox['angleEps'])
        case 'Neg_Anneal_LBFGS':
            new_angles = annealing_optimiser_dec(vertex_obj, uniform_angle, maxiter=angleApprox['angleMaxIt'], ftol=angleApprox['angleFTol'], eps=angleApprox['angleEps'])
        case 'SQP':
            new_angles = slsq(vertex_obj, uniform_angle, maxiter=angleApprox['angleMaxIt'], ftol=angleApprox['angleFTol'], eps=angleApprox['angleEps'])
    print('COMPLETED ANGLE APPROXIMATION WITH', angleApprox['angleApproxMeth'])
    results['angle_approx_loop_closure'] = f"{float(tachi_constraints_vertex_level_inputted(vertex_obj, new_angles)[1]):.{8}g}"
    results['angle_approx_loop_closure_matrix'] = [[f"{float(item):.{3}g}" for item in row] for row in tachi_constraints_vertex_level_inputted(vertex_obj, new_angles)[0].tolist()]
    # results['angle_approx_new_angles'] = new_angles.tolist()

    if vertexApprox['vertexPointMeth'] == 'Rot':
        print('BEGIN FACE ROTATION')
        vertex_points = bend_around_vertex(vertex_obj, np.array(new_angles, dtype=np.float64))
        print('COMPLETED FACE ROTATION')

    elif vertexApprox['vertexPointMeth'] == 'SQP':
        print('VERTEX POIN APPROXIMATION WITH SQP FACE ROTATION')
        vertex_points = vertex_slsq(vertex_obj, np.array(new_angles, dtype=np.float64), maxiter=vertexApprox['vertexMaxIt'], ftol=vertexApprox['vertexFTol'], eps=vertexApprox['vertexEps'])
        print('COMPLETED VERTEX POIN APPROXIMATION WITH SQP FACE ROTATION')

    print(vertex_points)
    new_angles = [ang.item() for ang in get_new_angles(vertex_obj)]
    results['vertex_approx_new_angles'] = new_angles
    results['dist_from_angle_results'] =     f"{float(vertex_points['check']):.{8}g}"
    results['total_edge_deviation'] =     f"{float(vertex_points['obj_length']):.{8}g}"
    results['total_sector_angle_deviation'] =     f"{float(vertex_points['sec_size']):.{8}g}"

    print(results)
    return results
def begin_approx(foldInfo):
    if angleApprox['angleApproxMeth'] == 'LBFGS':
        pass