/* eslint-disable no-unused-vars */
 /* eslint-disable react/prop-types */
/* eslint-disable react/no-unknown-property */
import React, { useContext, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { fileContext } from '../contexts/fileContext';
import { LineColor, FaceColor } from './CreaseMakerStates.js';

const DrawMesh = (props) => {
  console.log('drawing mesh')

  const [color, setColor] = useState(FaceColor[props.faceType])
  const [clicked, setClicked] = useState(false)
  const [hovered, setHovered] = useState(false)


  useEffect(() => {

    if (props.faceType == 'Polygon') {
      (hovered ? setColor(FaceColor[props.faceType + 'Highlight']) : setColor(FaceColor[props.faceType]))
    }
    
    
  }, [props.faceType, hovered, color])

  useEffect(() => {
    if (props.faceType == 'Polygon') {
      clicked ? setColor("red") : setColor(color)
    }

  }, [props.faceType, clicked, color])

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
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        onPointerDown={() => setClicked(!clicked)}
        //onClick={() => setClicked(!clicked)}
        >
          <shapeGeometry args={[shape]}/>
          <meshBasicMaterial color={color} side={THREE.DoubleSide} />
      </mesh>

    {props.faceType == 'Polygon' && (

      <lineSegments
        // ref={polyRef}
        onClick={(e) => console.log('line', e)}
        >
          <edgesGeometry args={[new THREE.ShapeGeometry(shape)]}/>
          <lineBasicMaterial color={LineColor.Mountain}/>
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
      <lineBasicMaterial attach="material" color={LineColor[props.creaseType]} depthTest={false} linewidth={10}/>
    </line>
  );
}

const DrawCrease = (props) => {

  const dataCategories = Object.keys(props.dxfData)

  const drawMesh = (loop, category) => {
    if (['Polygon', 'Paper'].includes(category)) {

      return(
        loop.map((entity, index) => {
          console.log(entity)
          return(<DrawMesh entity={entity} key={index} faceType={category}/>)
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
  }

  return(
    <>

       { dataCategories.map(category => {
        console.log(category)
          const loop = (category === 'Paper') ? [(props.dxfData[category])[1]] : props.dxfData[category] 
           return drawMesh(loop, category)
         })
       }
    </>
     
)
}

    


const CreaseMaker = (props) => {
 //aim, take in data from dxf file in data and use this to create a workable mesh in threeJS
  const file = useContext(fileContext);

  const groupRef = useRef();
  const rotationSpeed = 0.5

  const [isDrag, setDrag] = useState(false)
  const [resetRotate, setResetRotate] = useState(false)
  const [prevPos, setPrevPos]  = useState(null)


  const [pressed, setPressed] = useState(false)

  console.log('pls', file)


  const cameraPos = () => {
    return { position: [0, 0, 600]}
  }




  // useFrame((event) => {

  //   if (isDrag && pressed) {
  //     let { clientX, clientY, currentTarget } = event;
  //     const { width, height } = currentTarget.getBoundingClientRect();
  //     console.log('bounding stuff', width, height)

  //     const rotationX = ((clientY / height) - 0.5) * Math.PI * 2 * rotationSpeed;
  //     const rotationY = ((clientX / width) - 0.5) * Math.PI * 2 * rotationSpeed;
  //     groupRef.current.rotation.x = rotationX;
  //     groupRef.current.rotation.y = rotationY;
  //   } 
  // });

  //USE EFFECT TO ROTATE CAMERA AROUND OBJECT INSTEAD OF MOVING OBJECT
  //MOVING OBJECT CAUSES RE-RENDERING WHICH IS TOO EXPENSIVE


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
        <Canvas 
        // onMouseDown={setPressed(true)} onMouseMove={setDrag(true)} onMouseUp={setPressed(false)} 
        camera={cameraPos()}>
          <group ref={groupRef}><DrawCrease dxfData={file} position={[0, 0, 0]} /></group>
        </Canvas>
      ) : <p>{'nop'}</p>}

      
    </div>
  );
};

export default CreaseMaker;