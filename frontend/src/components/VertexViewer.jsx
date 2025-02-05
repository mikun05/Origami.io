/* eslint-disable no-unused-vars */
 /* eslint-disable react/prop-types */
/* eslint-disable react/no-unknown-property */
import * as THREE from 'three';
import { useContext, useEffect, useRef, useState } from 'react';
import { VertexColor, VertexSizes } from './PatternViewerStates';
import { PointMaterial } from '@react-three/drei'
import { useThree } from '@react-three/fiber';
import { PatternContext } from '../contexts/patternContext';
import axios from 'axios';
import { backendLink } from './PatternLoader';



const VertexViewer = (props) => {
    const { focusedVertexIndex } = useContext(PatternContext);
    const [focusedVertex, setFocusedVertex] = useState(null);

    useEffect(() => {
        if (focusedVertexIndex !== null){
            console.log('refecth vertec info')
            fetchFoldVertex(focusedVertexIndex)
        } 
    }, [focusedVertexIndex, props.pattern])


    const fetchFoldVertex = (vertexIndex) => {
        console.log('getting', vertexIndex)
        axios.get(`${backendLink}/get-vertex-info`, { params: {vertexIndex} })
            .then(response => {
                setFocusedVertex(response.data);
            })
            .catch(error => console.error("Error fetching vertex data:", error));
    };

    const vertexInfo = () => {
        const [x, y, z] = props.pattern['fold_format'][0]['vertices'][focusedVertexIndex]
        const surround_edges = []
        const surround_edge_objs = props.pattern['vertex_objects'][focusedVertexIndex]['surrounding_edges']

        for (let edge_obj of surround_edge_objs) {
            surround_edges.push(edge_obj['edge_pointer'])
        }
  
        
        return(
            <div>
                <p>{`Vertex ${focusedVertexIndex}:  (${Math.round(x)}, ${Math.round(y)}, ${Math.round(z)})`}</p>
                <br></br>
                <p>Surrounding Edges <br></br>
                    </p>
                    {surround_edges.map((edge, index) => {
                        return <p key={`${edge[0]}-${edge[1]}-${index}`}>{`Vtx ${edge[0]} to Vtx ${edge[1]}`}</p>;
                    })}
            </div>
           
        )
    }

    return(
        focusedVertex ? vertexInfo() : <></>
    )
}

export default VertexViewer