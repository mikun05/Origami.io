/* eslint-disable no-unused-vars */
 /* eslint-disable react/prop-types */
/* eslint-disable react/no-unknown-property */
import * as THREE from 'three';
import { useContext, useEffect, useRef, useState } from 'react';
import { EdgeColor, VertexColor, VertexSizes } from './PatternViewerStates';
import { PointMaterial } from '@react-three/drei'
import { useThree } from '@react-three/fiber';
import { PatternContext } from '../contexts/patternContext';

//how much code, language, commits and so on
const CameraSetUp = (props) => {
    const pointsRef = props.pointsRef

    const { camera, gl } = useThree(); //camera from Canvas

    const [isDragging, setIsDragging] = useState(false);
    const lastPointer = useRef({ x: 0, y: 0, pressure: 0 });


    useEffect(() => {
        if (!pointsRef.current) return;

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
        camera.position.set(center.x, center.y - distance , (center.z + distance) * 1.5);


        // camera.position.set(center.x, center.y - distance * 0.5, center.z + distance);
        camera.lookAt(new THREE.Vector3(center.x, center.y , center.z ));

        camera.updateProjectionMatrix()

    }, [pointsRef])


    useEffect(() => {
        if (!pointsRef.current) return;
        
        const handleWheelDown = (event) => {
            if (event.button !== 1) return;
            console.log('downn')
            setIsDragging(true);
            lastPointer.current = {
                x: event.clientX,
                y: event.clientY,
                pressure: event.pressure, // Initial pressure
              }        };


        const handleWheelMove = (event) => {
            if (!isDragging || event.pressure === 0) return; // Prevent unwanted movements when pressure is 0            console.log('draggg')
        
            const deltaX = event.clientX - lastPointer.current.x;
            const deltaY = event.clientY - lastPointer.current.y;
            const pressureFactor = event.pressure || 1; // Default to 1 if no pressure sensor

            lastPointer.current = {
                x: event.clientX,
                y: event.clientY,
                pressure: event.pressure,
            };

            const speed = 0.05 * pressureFactor; // Adjust spee
        
            camera.position.x -= deltaX * speed;
            camera.position.y += deltaY * speed;
            // camera.lookAt(0, 0, 0)
        
        }

        const handleWheelUp = (event) => {
            if (event.button !== 1) return;
            console.log('uppp')
            setIsDragging(false);
        };

        const handleWheelScroll = (event) => {

            const deltaX = event.clientX - lastPointer.current.x;
            const deltaY = event.clientY - lastPointer.current.y;
           
            console.log('zoom')
            const zoomSpeed = 0.01;
            // camera.position.x = deltaX * zoomSpeed
            // camera.position.y = deltaY * zoomSpeed
            camera.position.z += event.deltaY * zoomSpeed;
        };
        
        gl.domElement.addEventListener("mousedown", handleWheelDown);
        gl.domElement.addEventListener("mousemove", handleWheelMove);
        gl.domElement.addEventListener("mouseup", handleWheelUp);
        gl.domElement.addEventListener("wheel", handleWheelScroll);
    
        return () => {
          gl.domElement.removeEventListener("mousedown", handleWheelDown);
          gl.domElement.removeEventListener("mousemove", handleWheelMove);
          gl.domElement.removeEventListener("mouseup", handleWheelUp);
          gl.domElement.removeEventListener("wheel", handleWheelScroll);
        };
      }, [camera, gl, isDragging]);



    // useEffect(() => {
    //     if (!pointsRef.current) return;
        
    //     const handleRightClickDown = (event) => {
    //         if (event.button !== 2) return;
    //         console.log('rot downn')
    //         setIsRotating(true);
    //         lastPointer.current = {
    //             x: event.clientX,
    //             y: event.clientY,
    //             pressure: event.pressure, // Initial pressure
    //           }        };


    //     const handleMouseMove = (event) => {
    //         if (!isRotating || event.pressure === 0) return; // Prevent unwanted movements when pressure is 0            console.log('draggg')
        
    //         const deltaX = event.clientX - lastPointer.current.x;
    //         const deltaY = event.clientY - lastPointer.current.y;
    //         const pressureFactor = event.pressure || 1; // Default to 1 if no pressure sensor

    //         lastPointer.current = {
    //             x: event.clientX,
    //             y: event.clientY,
    //             pressure: event.pressure,
    //         };

    //         const rotationSpeed = 0.005 ; // Adjust spee
        
    //         setYaw((prevYaw) => prevYaw - deltaX * rotationSpeed);
    //         setPitch((prevPitch) => Math.min(Math.max(prevPitch - deltaY * rotationSpeed, -Math.PI / 2), Math.PI / 2));
    //         // camera.lookAt(0, 0, 0)
        
    //     }

    //     const handleRightClickUp = (event) => {
    //         if (event.button !== 2) return;
    //         console.log('rot uppp')
    //         setIsRotating(false);
    //     };

    //     const x = 10 * Math.cos(pitch) * Math.sin(yaw);
    //     const y = 10 * Math.sin(pitch);
    //     const z = 10 * Math.cos(pitch) * Math.cos(yaw);

    //     camera.position.set(x, y, z);

        
    //     const disableContextMenu = (event) => event.preventDefault();

    //     gl.domElement.addEventListener("mousedown", handleRightClickDown);
    //     gl.domElement.addEventListener("mousemove", handleMouseMove);
    //     gl.domElement.addEventListener("mouseup", handleRightClickUp);
    //     gl.domElement.addEventListener("contextmenu", disableContextMenu);
    
    //     return () => {
    //       gl.domElement.removeEventListener("mousedown", handleRightClickDown);
    //       gl.domElement.removeEventListener("mousemove", handleMouseMove);
    //       gl.domElement.removeEventListener("mouseup", handleRightClickUp);
    //       gl.domElement.removeEventListener("contextmenu", disableContextMenu);
    //     };
    //   }, [camera, gl, isRotating, yaw, pitch]);
}

const RotateObject = ({pivot, children}) => {
    const groupRef = useRef();
    const lastPointer = useRef({ x: 0, y: 0 });
    const [isRotatingZ, setIsRotatingZ] = useState(false);
    const [isRotatingX, setIsRotatingX] = useState(false);


    useEffect(() => {
      const handlePointerDown = (event) => {
        switch (event.button) {
            case 0:
                setIsRotatingZ(true)
                break;
            case 2:
                setIsRotatingX(true)
                break;
            default:
                return;
        }
        lastPointer.current = { x: event.clientX, y: event.clientY };
      };
  
      const handlePointerMove = (event) => {
        if (!isRotatingZ && !isRotatingX) return;
  
        const deltaX = isRotatingZ ? event.clientX - lastPointer.current.x : 0
        const deltaY = isRotatingX ?  event.clientY - lastPointer.current.y : 0
        lastPointer.current = { x: event.clientX, y: event.clientY };
  
        // Apply rotation to the pivot group

        const rotationSpeed = 0.005;

        // Step 1: Create a transformation matrix

        if (groupRef.current) {
                groupRef.current.position.add(pivot);
                groupRef.current.rotation.x += deltaY * rotationSpeed ; // Rotate around X-axis
                groupRef.current.rotation.z += deltaX * rotationSpeed ; // Rotate around X-axis
                groupRef.current.position.sub(pivot);

                
        }
  
      };
  
      const handlePointerUp = (event) => {
        switch (event.button) {
            case 0:
                setIsRotatingZ(false)
                break;
            case 2:
                setIsRotatingX(false)
                break;
            default:
                return;
        }
      };
  
      window.addEventListener("pointerdown", handlePointerDown);
      window.addEventListener("pointermove", handlePointerMove);
      window.addEventListener("pointerup", handlePointerUp);
  
      return () => {
        window.removeEventListener("pointerdown", handlePointerDown);
        window.removeEventListener("pointermove", handlePointerMove);
        window.removeEventListener("pointerup", handlePointerUp);
      };
    }, [isRotatingX, isRotatingZ, groupRef]);

    return(
        <group ref={groupRef}>{children}</group>
                
                
    )
    
}

const PatternViewer = (props) => {
    const { focusedVertexIndex, setFocusedVertexIndex, focusedVertexEdges, setFocusedVertexEdges, focusedEdgeIndex, setFocusedEdgeIndex } = useContext(PatternContext);
    const [vertexMetadata, setVertexMetaData] = useState(props.pattern['vertex_objects'])
    const [canvasCenter, setCanvasCenter] = useState([0,0,0])

    const vertices = new Float32Array(props.pattern['fold_format'][0]['vertices'].flat()) //only thing subject to change after foldings
    const edges = new Uint16Array(props.pattern['fold_format'][0]['edges'].flat())
    const edge_assignments = props.pattern['fold_format'][0]['edges_assignments']
    const faces = new Uint16Array(props.pattern['fold_format'][0]['faces'].flat())

    const pointsRef = useRef();
    const linesRef = useRef();

    useEffect(() => {
        const geometry = pointsRef.current.geometry;
        geometry.computeBoundingBox();
        const bbox = geometry.boundingBox;
        const center = new THREE.Vector3();
        bbox.getCenter(center);
        setCanvasCenter(center)
    }, [])

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


    useEffect(() => {
        if (focusedVertexIndex !== null) {
            const surrounding_edges = (props.pattern['vertex_objects'][focusedVertexIndex]['surrounding_edges']);
            const focused_edge_index = surrounding_edges.map(edge_obj => edge_obj['index']); 
            setFocusedVertexEdges(focused_edge_index)

            updatePointsListState('vertex color', focusedVertexIndex, VertexColor.Clicked, VertexSizes.Clicked);
            updateLinesListState('edge color', focused_edge_index, EdgeColor.Clicked);
        } else {
            updatePointsListState('vertex color', focusedVertexIndex, VertexColor.Clicked, VertexSizes.Clicked);
            updateLinesListState('edge color', null, EdgeColor.Default);
            setFocusedEdgeIndex(null)
        }
    }, [focusedVertexIndex]); 


    useEffect(() => {
        if (focusedEdgeIndex !== null) {
            updateLinesListState('edge color', [focusedEdgeIndex], EdgeColor.Highlight);
        } else {
            (focusedVertexEdges !== null) ? updateLinesListState('edge color', focusedVertexEdges, EdgeColor.Clicked) : updateLinesListState('edge color', null, EdgeColor.Default);

        }
    }, [focusedEdgeIndex, focusedVertexEdges])

    // useEffect(() => {
    //     if (focusedVertexEdges !== null && focusedVertexEdges.length !== 0) {
    //         updateLinesListState('edge color', focusedVertexEdges, EdgeColor.Clicked);
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

                    // new_color = (index === focusedEdgeIndex) ? [0, 0, 1] : [0,0,0]

                    switch(i) {
                        case (v_in * 3):
                        case (v_out * 3):
                            console.log(i, 'change red')
                            return  edge_colors[i] * newColor[0];
                        case (v_in * 3 + 1):
                        case (v_out * 3 + 1):
                            console.log(i, 'change green')
                            return  edge_colors[i] * newColor[1];
                        case  (v_in * 3 + 2):
                        case (v_out * 3 + 2):
                            console.log(i, 'change blue')
                            return edge_colors[i] * newColor[2];
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
        setFocusedEdgeIndex(null)
    } 

    const handlePointerOver = (event) => {
        if (!pointsRef.current) return;
        const index = raycastVertex(event); 
        if (index !== focusedVertexIndex) {updatePointsListState('vertex hover color', index, VertexColor.Hovered, VertexSizes.Clicked);}

    } 

    const handleEdgePointerDown = (event) => {
        if (!linesRef.current) return;
        if (focusedVertexEdges) {
            console.log('gggg', event.index)

            if (focusedVertexEdges.includes(event.index/2)) {
                setFocusedEdgeIndex((prevIndex) => prevIndex === event.index/2 ? null : event.index/2);
            }
        }
    } 
    
    
    return (
        <>
            <CameraSetUp pointsRef={pointsRef}/>
            <RotateObject pivot={canvasCenter}>
                <axesHelper position={[0,0,0]} scale={15} />
                {/* <gridHelper position={canvasCenter} scale={5} rotation={new THREE.Euler( Math.PI / 2,0, 0)}/> */}

                <lineSegments ref={linesRef} onClick={handleEdgePointerDown} >
                    <bufferGeometry>
                        <bufferAttribute attach="attributes-position" args={[edge_vertices, 3]} />
                        <bufferAttribute attach="attributes-color" args={[edgeColors, 3]} />
                    </bufferGeometry>
                    <lineBasicMaterial vertexColors={true} linewidth={15} />
                </lineSegments>

                <points ref={pointsRef} onClick={handlePointerDown} onPointerOver={handlePointerOver} >
                    <bufferGeometry>
                        <bufferAttribute attach="attributes-position" args={[vertices, 3]} />
                        <bufferAttribute attach="attributes-color" args={[vertexColors, 3]} />
                        <bufferAttribute attach="attributes-size" args={[vertex_sizes, 1]} />
                    </bufferGeometry>
                    <PointMaterial transparent vertexColors size={0.75} depthWrite={false} toneMapped={false} />
                </points>

                {/* <mesh>
                    <bufferGeometry>
                        <bufferAttribute attach="attributes-position" args={[vertices, 3]} />
                        <bufferAttribute attach="index" args={[faces, 1]} />
                    </bufferGeometry>
                    <meshBasicMaterial color="white" wireframe={false} side={THREE.FrontSide} shadowSide={THREE.FrontSide} />
                </mesh>

                <mesh> 
                    <bufferGeometry>
                        <bufferAttribute attach="attributes-position" args={[vertices, 3]} />
                        <bufferAttribute attach="index" args={[faces, 1]} />
                    </bufferGeometry>
                    <meshBasicMaterial color="grey" wireframe={false} side={THREE.BackSide}/>
                </mesh> */}
            </RotateObject>
        </>
    );

}

export default PatternViewer;


