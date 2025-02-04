/* eslint-disable no-unused-vars */
 /* eslint-disable react/prop-types */
/* eslint-disable react/no-unknown-property */
import * as THREE from 'three';
import { Canvas } from '@react-three/fiber';



const PatternViewer = (props) => {

    //const geometry = new THREE.BufferGeometry();
    console.log(props.pattern['vertices'])

    const vertices = new Float32Array(props.pattern['vertices'].flat()) //only thing subject to change after foldings
    //geometry.setAttribute( 'position', new THREE.BufferAttribute(vertices, 3));
    console.log(vertices)
    //const material = new THREE.MeshBasicMaterial({color: 0xFF00FF})

    

    const cameraPos = () => {
        return { position: [2, 2, 5]}
      }

    // return(
    //     <Canvas camera={cameraPos()}>
    //       <mesh
    //         >
    //         <bufferGeometry>
    //             <bufferAttribute attachObject={["attributes", "position"]} array={vertices} itemSize={3} />
    //         </bufferGeometry>
            
    //         {/* <boxGeometry args={[10, 10, 10]} /> */}
    //         <meshStandardMaterial attach="material" color="hotpink"   />

    //         </mesh>
    //     </Canvas>
      

    // )

    return (
        <Canvas camera={{ position: [0, -1, 1] }}>
           

            {/* <mesh>
                <boxGeometry args={[1, 1, 1]} />
                <meshStandardMaterial color="blue" />
            </mesh> */}
            
            {/* Render points */}
            <points>
                <bufferGeometry>
                    <bufferAttribute attach="attributes-position" array={vertices} count={vertices.length / 3} itemSize={3} />
                </bufferGeometry>
                <pointsMaterial attach="material" color="red" size={0.1} />
            </points>
        </Canvas>
    );

}

export default PatternViewer;
