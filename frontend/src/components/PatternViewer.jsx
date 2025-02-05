/* eslint-disable no-unused-vars */
 /* eslint-disable react/prop-types */
/* eslint-disable react/no-unknown-property */
import * as THREE from 'three';
import { useContext, useEffect, useRef, useState } from 'react';
import { VertexColor, VertexSizes } from './PatternViewerStates';
import { PointMaterial } from '@react-three/drei'
import { useThree } from '@react-three/fiber';
import { PatternContext } from '../contexts/patternContext';



const PatternViewer = (props) => {
    const { focusedVertexIndex, setFocusedVertexIndex, focusedEdgeIndex, setFocusedEdgeIndex } = useContext(PatternContext);
    const [vertexMetadata, setVertexMetaData] = useState(props.pattern['vertex_objects'])

    useEffect(() => {
        if (focusedVertexIndex !== null) {
            updateListState('color', focusedVertexIndex, VertexColor.Clicked, VertexSizes.Clicked);
        }
    }, [focusedVertexIndex, props.pattern]); 

    useEffect(() => {
        console.log('changing metadata')
        setVertexMetaData(props.pattern['vertex_objects'])
    }, [props.pattern])
    
    const pointsRef = useRef();


    const vertices = new Float32Array(props.pattern['fold_format'][0]['vertices'].flat()) //only thing subject to change after foldings

    const edges = new Uint16Array(props.pattern['fold_format'][0]['edges'].flat())
    console.log(edges)
    console.log('from view', focusedVertexIndex)

    const faces = new Uint16Array(props.pattern['fold_format'][0]['faces'].flat())
    

    const vertex_colors = new Float32Array(vertices.length );
    for (let i = 0; i < vertices.length; i++) {
        vertex_colors[i * 3] = VertexColor.Default[0];   // Red
        vertex_colors[i * 3 + 1] = VertexColor.Default[1]; // Green
        vertex_colors[i * 3 + 2] = VertexColor.Default[2]; // Blue
    }

    const vertex_sizes = new Float32Array(vertices.length/3);
    for (let i = 0; i < vertices.length; i++) {
        vertex_sizes[i] = VertexSizes.Default;   
    }


    const raycastVertex = (event) => {
        if (!pointsRef.current) return;
        return event.index
      };

    
    const updateListState = (attribute, index, newColor, newSize) => {
        if (!pointsRef.current) return;
        console.log('changing')
        const colorArray = pointsRef.current.geometry.attributes.color.array;
        const sizeArray = pointsRef.current.geometry.attributes.size.array;



        // Update color for the clicked vertex (RGB)
        colorArray[index * 3] = newColor[0];   // Red
        colorArray[index * 3 + 1] = newColor[1]; // Green
        colorArray[index * 3 + 2] = newColor[2]; // Blue

        sizeArray[index] = newSize; 
    
        pointsRef.current.geometry.attributes.color.needsUpdate = true; // Mark for update
        pointsRef.current.geometry.attributes.size.needsUpdate = true; // Mark for update

        console.log(colorArray)
    };
    

    

    const handlePointerDown = (event) => {
        if (!pointsRef.current) return;
        console.log(event)
        const index = raycastVertex(event); // Retrieve vertex index
        setFocusedVertexIndex(focusedVertexIndex === index ? null : index);

        // updateListState(vertexColors, setVertexColors, focusedVertex*3 ,VertexColor.Clicked )
        // updateListState(vertexSizes, setVertexSizes, focusedVertex*3, VertexSizes.Clicked )

        // updateListState('color', index, VertexColor.Clicked, VertexSizes.Clicked)

        console.log("Hovered Vertex:", index, vertexMetadata[index]); // Retain metadata
    } 
    
    const handlePointerOver = (event) => {
        if (!pointsRef.current) return;

        console.log(event)
        const index = raycastVertex(event); // Retrieve vertex index
        setFocusedVertexIndex(focusedVertexIndex === index ? null : index);
    
        console.log("Hovered Vertex:", index, vertexMetadata[index]); // Retain metadata
    };

    const { camera } = useThree(); // Get camera from Canvas
    useEffect(() => {
        if (!pointsRef.current) return;

        // Compute bounding box of the pattern
        const geometry = pointsRef.current.geometry;
        geometry.computeBoundingBox();
        const bbox = geometry.boundingBox;

        // Compute center and size
        const center = new THREE.Vector3();
        bbox.getCenter(center);
        const size = new THREE.Vector3();
        bbox.getSize(size);

        // Adjust camera to fit the bounding box
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
       
            <points ref={pointsRef} onClick={handlePointerDown} >
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[vertices, 3]} />
                    <bufferAttribute attach="attributes-color" args={[vertex_colors, 3]} />
                    <bufferAttribute attach="attributes-size" args={[vertex_sizes, 1]} />
                </bufferGeometry>
                <PointMaterial transparent vertexColors vertexSizes depthWrite={false} toneMapped={false} />
            </points>

            <lineSegments>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" args={[vertices, 3]} />
                    <bufferAttribute attach="index" args={[edges, 1]} />
                </bufferGeometry>
                <lineBasicMaterial attach="material" color="black" linewidth={2} />
            </lineSegments>

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


