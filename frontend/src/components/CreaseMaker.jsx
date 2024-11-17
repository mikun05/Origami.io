/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */
/* eslint-disable react/no-unknown-property */
import React, { useContext, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { fileContext } from '../contexts/fileContext';

const DrawMesh = (props) => {
  console.log('drawing mesh')

  const polyRef = useRef()

  const color = props.isPaper() ? "#4F4F4F" : "#333333"
          
  const shape = new THREE.Shape();
  shape.moveTo( props.entity.vertices[0][0],  props.entity.vertices[0][1]); //sets starting vertex of the polygon

  // Adds line segments of each polygon 
  for (let i = 1; i <  props.entity.vertices.length; i++) {
      const [x, y] =  props.entity.vertices[i];
      shape.lineTo(x, y);
  }

  return (
    <>
      <mesh
        // ref={polyRef}
        onClick={(e) => console.log(e)}
        >
          <shapeGeometry args={[shape]}/>
          <meshBasicMaterial color={color} side={THREE.DoubleSide} />
      </mesh>

    {!props.isPaper() && (

      <lineSegments
        // ref={polyRef}
        onClick={(e) => console.log('line', e)}
        >
          <edgesGeometry args={[new THREE.ShapeGeometry(shape)]}/>
          <lineBasicMaterial color="#FF0000"/>
      </lineSegments>

    ) 
    }
    </>
  )
}

const DrawLine = (props) => {
  console.log('drawing line')


  // Verify start and end points
  const { start, end, color } = props.entity;
  console.log(start, end, color)

  const points = [new THREE.Vector3(start[0], start[1], start[2]), new THREE.Vector3(end[0], end[1], end[2])];

  const geometry = new THREE.BufferGeometry().setFromPoints(points)

  return (
    <line 
      key={props.key}
      renderOrder={1} 
      geometry={geometry}
      onClick={(e) => console.log(props.creaseType, e)}>
      <lineBasicMaterial attach="material" color={color || 'yellow'} depthTest={false} linewidth={10}/>
    </line>
  );
}

const DrawCrease = (props) => {

  const dataCategories = Object.keys(props.dxfData)

  console.log('draw crease called', dataCategories)


  return(
    <>

       { dataCategories.map(category => {
        console.log(category)
          const loop = (category === 'Paper') ? [(props.dxfData[category])[1]] : props.dxfData[category] 
           if (['Polygon', 'Paper'].includes(category)) {
            console.log('loop', loop)

            return(
              loop.map((entity, index) => {
                console.log(entity)
                return(<DrawMesh entity={entity} key={index} isPaper={() => (category === 'Paper')}/>)
            }
            ))
           
      
          } else if (['Valley', 'Mountain', 'CrimpValley', 'CrimpMountain'].includes(category)) {
            
            return(
              loop.map((entity, index) => {
                console.log(entity)
                return(<DrawLine entity={entity} key={index} creaseType={category}/>)
              })  
            )
          } 
         })
       }
    </>
     
)
}
    


const CreaseMaker = (props) => {
 //aim, take in data from dxf file in data and use this to create a workable mesh in threeJS
  const [error, setError] = useState(null);

  const file = useContext(fileContext);

  const groupRef = useRef();
  const rotationSpeed = 0.5

  const [isDrag, setDrag] = useState(false)
  const [resetRotate, setResetRotate] = useState(false)
  const [prevPos, setPrevPos]  = useState(null)

  console.log('pls', file)


  const cameraPos = () => {
    return { position: [0, 0, 600]}
  }



  const handleMouseDown = () => {
    setDrag(true)
  }

  const handleMouseMove = (event) => {

    if (isDrag ) {
      let { clientX, clientY, currentTarget } = event;
      const { width, height } = currentTarget.getBoundingClientRect();
      console.log('bounding stuff', width, height)

      const rotationX = ((clientY / height) - 0.5) * Math.PI * 2 * rotationSpeed;
      const rotationY = ((clientX / width) - 0.5) * Math.PI * 2 * rotationSpeed;
      groupRef.current.rotation.x = rotationX;
      groupRef.current.rotation.y = rotationY;
    } 
  };

  const handleMouseUp = () => {
    setDrag(false)
  }

  useEffect(() => {
    if (resetRotate) {
      groupRef.current.rotation.x = 0;
      groupRef.current.rotation.y = 0;
    } 
  }, [resetRotate])


  


  return (
    <div  style={{display: 'flex', flexDirection: 'column', margin: 'auto', width:'1000px',  height:'800px'}}>
    
      <button onClick={() => setResetRotate(!resetRotate)}>Reset Crease Rotation</button>
      {file ? (
        <Canvas onMouseDown={handleMouseDown} onMouseMove={handleMouseMove} onMouseUp={handleMouseUp} camera={cameraPos()}>
          <group ref={groupRef}><DrawCrease dxfData={file} position={[0, 0, 0]} /></group>
        </Canvas>
      ) : <p>{'nop'}</p>}

      
    </div>
  );
};

export default CreaseMaker;