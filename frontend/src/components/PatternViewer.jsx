/* eslint-disable no-unused-vars */
 /* eslint-disable react/prop-types */
/* eslint-disable react/no-unknown-property */
import * as THREE from 'three';
import { useContext, useEffect, useRef, useState } from 'react';
import { EdgeColor, VertexColor, VertexSizes } from './PatternViewerStates';
import { PointMaterial } from '@react-three/drei'
import { invalidate, useThree } from '@react-three/fiber';
import { PatternContext } from '../contexts/patternContext';
import VertexViewer from './VertexViewer';

//how much code, language, commits and so on


const PatternViewer = (props) => {
    const { focusedVertexIndex, setFocusedVertexIndex, focusedEdgeIndex, setFocusedEdgeIndex } = useContext(PatternContext);
    const [vertexMetadata, setVertexMetaData] = useState(props.pattern['vertex_objects'])

    const vertices = new Float32Array(props.pattern['fold_format'][0]['vertices'].flat()) //only thing subject to change after foldings
    const vertices_for_edges = new Float32Array(props.pattern['fold_format'][0]['vertices'].flat()) //only thing subject to change after foldings
    const edges = new Uint16Array(props.pattern['fold_format'][0]['edges'].flat())
    const edge_assignments = props.pattern['fold_format'][0]['edges_assignments']
    const faces = new Uint16Array(props.pattern['fold_format'][0]['faces'].flat())

    console.log('edge_assg', edge_assignments)

    const vertex_colors = new Float32Array(vertices.length);
    for (let i = 0; i < vertices.length; i++) {
        vertex_colors[i * 3] = VertexColor.Default[0];   // Red
        vertex_colors[i * 3 + 1] = VertexColor.Default[1]; // Green
        vertex_colors[i * 3 + 2] = VertexColor.Default[2]; // Blue
    }
    const [vertexColors, setVertexColors] = useState(vertex_colors)


    const edge_colors = new Float32Array(edges.length * 3 );
    const edge_vertices = new Float32Array(edges.length * 3);

    // for (let i = 0; i < edges.length/2; i++) {
    //     const start = (i * 6) //index*2 is where v_1 is, index*2 + 1 is where v_2 is

    //     const edge_type = EdgeColor[edge_assignments[Math.floor(i)]]

    //     const v_in = (i * 2) //index*2 is where v_1 is, index*2 + 1 is where v_2 is
    //     const v_out = (i * 2) + 1

    //     console.log(i, edge_type)

    //     //now I need the x,y,z coordinates v_1 and v_2 refer to in the vertex list. i need th eposition it points to
    //     //to get the positions in the vertex list, pos_1 = v_1 * 3, v_1*3+1, v_1*3+2 and so on

    //     // edge_colors[(v_in * 3)] = EdgeColor[edge_type][0]
    //     // edge_colors[(v_out * 3)] = EdgeColor[edge_type][0]
    //     // edge_colors[(v_in * 3 + 1)] = EdgeColor[edge_type][1]
    //     // edge_colors[(v_out * 3 + 1)] = EdgeColor[edge_type][1]
    //     // edge_colors[(v_in * 3 + 2)] = EdgeColor[edge_type][2]
    //     // edge_colors[(v_out * 3 + 2)] = EdgeColor[edge_type][2]
               

    //     edge_colors[start ] = edge_type[0]; 
    //     edge_colors[start + 3] = edge_type[0];    
    //     edge_colors[start + 1] = edge_type[1];    
    //     edge_colors[start + 4] = edge_type[1];    
    //     edge_colors[start + 2] = edge_type[2];   
    //     edge_colors[start + 5] = edge_type[2];    
       
    //     }

    for (let i = 0; i < edges.length / 2; i++) {
        const startIdx = i * 6; // 2 vertices per edge, each with 3 color components
    
        const v1 = edges[i * 2]; // Start vertex
        const v2 = edges[i * 2 + 1]; // End vertex
    
        // Copy the vertex positions (duplicating the shared vertices)
        edge_vertices[startIdx] = vertices[v1 * 3];
        edge_vertices[startIdx + 1] = vertices[v1 * 3 + 1];
        edge_vertices[startIdx + 2] = vertices[v1 * 3 + 2];
        edge_vertices[startIdx + 3] = vertices[v2 * 3];
        edge_vertices[startIdx + 4] = vertices[v2 * 3 + 1];
        edge_vertices[startIdx + 5] = vertices[v2 * 3 + 2];
    
        // Assign the same color to both duplicated vertices of the edge
        const edge_type = EdgeColor[edge_assignments[i]]; 
    
        edge_colors[startIdx] = edge_type[0];
        edge_colors[startIdx + 1] = edge_type[1];
        edge_colors[startIdx + 2] = edge_type[2];

        edge_colors[startIdx + 3] = edge_type[0];
        edge_colors[startIdx + 4] = edge_type[1];
        edge_colors[startIdx + 5] = edge_type[2];
    }
    
      
    console.log('ed',edge_colors)
    const [edgeColors, setEdgeColors] = useState(edge_colors)

    const new_edge_color = edge_assignments.map((c,i) => EdgeColor[edge_assignments[Math.floor(i)]])


    const pointsRef = useRef();
    const linesRef = useRef();


    useEffect(() => {
        if (focusedVertexIndex !== null) {
            const surrounding_edges = (props.pattern['vertex_objects'][focusedVertexIndex]['surrounding_edges']);
            const focused_edge_index = surrounding_edges.map(edge_obj => edge_obj['index']); 
            setFocusedEdgeIndex(focused_edge_index)

            updatePointsListState('vertex color', focusedVertexIndex, VertexColor.Clicked, VertexSizes.Clicked);
            updateLinesListState('edge color', focused_edge_index, EdgeColor.Clicked);
        } else {
            updatePointsListState('vertex color', focusedVertexIndex, VertexColor.Clicked, VertexSizes.Clicked);
            updateLinesListState('edge color', null, EdgeColor.Clicked);
        }
    }, [focusedVertexIndex]); 

    

    
    // useEffect(() => {
    //     if (focusedEdgeIndex !== null && focusedEdgeIndex.length !== 0) {

    //         updateLinesListState('edge color', focusedEdgeIndex, EdgeColor.Clicked);
            
    //     }

        
    //     invalidate();

    // }, [focusedVertexIndex]); 

    useEffect(() => {
        setVertexMetaData(props.pattern['vertex_objects'])
    }, [props.pattern])


    useEffect(() => {
        if (linesRef.current) {
            console.log('Updated line color buffer:', linesRef.current.geometry.attributes.color.array);
        }
    }, [focusedVertexIndex]);

    useEffect(() => {
        console.log(`Focused Vertex Index Updated: ${focusedVertexIndex}`);
    }, [focusedVertexIndex]);


    
    



   
    

    // const vertex_colors = new Float32Array(vertices.length );
    // for (let i = 0; i < vertices.length; i++) {
    //     vertex_colors[i * 3] = VertexColor.Default[0];   // Red
    //     vertex_colors[i * 3 + 1] = VertexColor.Default[1]; // Green
    //     vertex_colors[i * 3 + 2] = VertexColor.Default[2]; // Blue
    // }

    const vertex_sizes = new Float32Array(vertices.length/3);
    for (let i = 0; i < vertices.length; i++) {
        vertex_sizes[i] = VertexSizes.Default;   
    }


    const raycastVertex = (event) => {
        if (!pointsRef.current) return;
        return event.index
      };

    
    const updatePointsListState = (attribute, index, newColor, newSize,) => {
        if (!pointsRef.current) return;
        let nextVertexColors = edgeColors.map((c,i) => 1)

        if (index !== null){
            nextVertexColors = vertexColors.map((c,i) => {
                switch(i) {
                    case index*3:
                        return newColor[0];
                    case index*3 + 1:
                        return newColor[1];
                    case index*3 + 2:
                        return newColor[2];
                }
                return Math.floor(i/3) === focusedVertexIndex ? c : 1
            })
        }
        setVertexColors(nextVertexColors)

        pointsRef.current.geometry.attributes.color.array = vertexColors;

        pointsRef.current.geometry.attributes.color.needsUpdate = true; 
        pointsRef.current.material.needsUpdate = true;
    };

    const updateLinesListState = (attribute, indices, newColor) => {
        if (!linesRef.current) return;
        let nextEdgeColors = edgeColors.map((c,i) => edge_colors[i])


        if (indices !== null && indices.length !== 0 ){
            nextEdgeColors = edgeColors.map((c,i) => {
                //index is the position of the edge (v_1, v_2) in the edge list
                //This has been flattened so we do index * 2 to get to the position in the flat list.
                console.log('h', edge_vertices[indices[0]])
                for (let index of indices) {
                    const v_in = (index * 2) //index*2 is where v_1 is, index*2 + 1 is where v_2 is
                    const v_out = (index * 2) + 1

                    //now I need the x,y,z coordinates v_1 and v_2 refer to in the vertex list. i need th eposition it points to
                    //to get the positions in the vertex list, pos_1 = v_1 * 3, v_1*3+1, v_1*3+2 and so on

                    switch(i) {
                        case (v_in * 3):
                        case (v_out * 3):
                            console.log(i, 'change red')
                            return edge_colors[i] * 10;
                        case (v_in * 3 + 1):
                        case (v_out * 3 + 1):
                            console.log(i, 'change green')
                            return edge_colors[i] * 10;
                        case  (v_in * 3 + 2):
                        case (v_out * 3 + 2):
                            console.log(i, 'change blue')
                            return edge_colors[i] * 10;
                    }
                }
                return edge_colors[i]
            })
        }

        
        setEdgeColors(nextEdgeColors)

        linesRef.current.geometry.attributes.color.array = edgeColors

        linesRef.current.geometry.attributes.color.needsUpdate = true; 
        linesRef.current.material.needsUpdate = true

    };
    

    

    const handlePointerDown = (event) => {
        if (!pointsRef.current) return;
        const index = raycastVertex(event); 
        setFocusedVertexIndex((prevIndex) => prevIndex === index ? null : index);
    } 

    const handlePointerOver = (event) => {
        if (!pointsRef.current) return;
        const index = raycastVertex(event); 
        if (index !== focusedVertexIndex) {updatePointsListState('vertex hover color', index, VertexColor.Hovered, VertexSizes.Clicked);}

    } 

    const handleEdgePointerDown = (event) => {
        if (!linesRef.current) return;
        console.log(event.index)
    } 
    

    const { camera } = useThree(); //camera from Canvas
    useEffect(() => {
        if (!pointsRef.current) return;

        //bounding box of the pattern
        const geometry = pointsRef.current.geometry;
        geometry.computeBoundingBox();
        const bbox = geometry.boundingBox;

        //center and size
        const center = new THREE.Vector3();
        bbox.getCenter(center);
        const size = new THREE.Vector3();
        bbox.getSize(size);

        //adjust camera to fit the bounding box
        const maxDim = Math.max(size.x, size.y, size.z);
        const fitHeightDistance = maxDim / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))); 
        const fitWidthDistance = fitHeightDistance / camera.aspect;
        const distance = Math.max(fitHeightDistance, fitWidthDistance);//camera dist from pattern to fit pattern on canvas

        camera.position.set(center.x, center.y - distance * 0.5, center.z + distance);
        camera.lookAt(center);

        camera.updateProjectionMatrix();
    }, [camera]);



    

    return (
        <>
            <lineSegments ref={linesRef} onClick={handleEdgePointerDown} renderOrder={2}>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[edge_vertices, 3]} />
                    <bufferAttribute attach="attributes-color" args={[edgeColors, 3]} />
                </bufferGeometry>
                <lineBasicMaterial vertexColors={true} dashSize={5} gapSize={5} scale={5}/>

            </lineSegments>

            <points ref={pointsRef} onClick={handlePointerDown} onPointerOver={handlePointerOver} renderOrder={1}>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[vertices, 3]} />
                    <bufferAttribute attach="attributes-color" args={[vertexColors, 3]} />
                    <bufferAttribute attach="attributes-size" args={[vertex_sizes, 1]} />
                </bufferGeometry>
                <PointMaterial transparent vertexColors vertexSizes depthWrite={false} toneMapped={false} />
            </points>

            {/* <VertexViewer vertexIndex={focusedVertexIndex} pattern={props.pattern}/> */}


           

            {/* <mesh>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[vertices, 3]} />
                    <bufferAttribute attach="index" args={[faces, 1]} />
                </bufferGeometry>
                <meshBasicMaterial attach="material" color="pink" wireframe={false} />
            </mesh> */}
            


        </>
          
    );

}

export default PatternViewer;


