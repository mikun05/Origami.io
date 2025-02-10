/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */
import { useContext, useEffect, useState } from 'react';
import { PatternContext } from '../contexts/patternContext';

const VertexViewer = (props) => {
    const { focusedVertexIndex, setFocusedVertexEdges, focusedVertexEdges } = useContext(PatternContext);
    const [surroundEdges, setSurroundingEdges] = useState(null)

    const pattern = props.pattern

    useEffect(() => {
        if (focusedVertexIndex !== null){
            updateSurroundingEdgeObjs(focusedVertexIndex)
        } 
    }, [focusedVertexIndex])

    const updateFocusedEdges = (edges) => {
        const focused_edge_index = edges.map(edge_obj => edge_obj['index']); 
        setFocusedVertexEdges(focused_edge_index)
    }

    const updateSurroundingEdgeObjs = (vertex) => {
            setSurroundingEdges(pattern['vertex_objects'][vertex]['surrounding_edges']);
    }

    useEffect(() => {
        console.log('Updated FOCUSED:', focusedVertexEdges);
    }, [focusedVertexEdges])


    // const fetchFoldVertex = (vertexIndex) => {
    //     console.log('getting', vertexIndex)
    //     axios.get(`${backendLink}/get-vertex-info`, { params: {vertexIndex} })
    //         .then(response => {
    //             setFocusedVertex(response.data);
    //         })
    //         .catch(error => console.error("Error fetching vertex data:", error));
    // };

    const vertexInfo = () => {
        const [x, y, z] = pattern['fold_format'][0]['vertices'][focusedVertexIndex]

        const surround_edges = surroundEdges ? surroundEdges.map(edge_obj => edge_obj['edge_pointer']) : []

        
        return(
            <div>
                <p>{`Vertex ${focusedVertexIndex}:  (${Math.round(x)}, ${Math.round(y)}, ${Math.round(z)})`}</p>
                <br></br>
                <p>Surrounding Edges <br></br>
                    </p>
                    {surround_edges.map((edge, index) => {
                        return <p key={`${edge[0]}-${edge[1]}-${index}`}>{`${index}: Vtx ${edge[0]} to Vtx ${edge[1]}`}</p>;
                    })}
            </div>
           
        )
    }

    return(
        // (focusedVertexIndex !== null) ? vertexInfo() : <h4>Select A Vertex</h4>
        <></>
    )
}

export default VertexViewer