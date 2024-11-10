/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */
/* eslint-disable react/no-unknown-property */
import React, { useEffect, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { DXFLoader } from 'three-dxf-loader'


const Box = (props) => {
  const meshRef = useRef(null)
  const [hovered, setHover] = useState(false)
  const [active, setActive] = useState(false)
  useFrame((state, delta) => (meshRef.current.rotation.x += delta))

  return (
    <mesh
      {...props}
      ref={meshRef}
      scale={active ? 1.5 : 1}
      onClick={(event) => setActive(!active)}
      onPointerOver={(event) => setHover(true)}
      onPointerOut={(event) => setHover(false)}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={hovered ? 'hotpink' : '#2f74c0'} />
    </mesh>
  )
  }

  const DrawCrease = (props) => {
    const groupRef = useRef();
  
    useEffect(() => {
      if (!props.dxfData) return;
  
      // const loader = new DXFLoader();
      // const parsedData = loader.parse(props.dxfData);
      const parsedData = props.dxfData
      console.log('pp', Object.keys(parsedData))
      
      Object.keys(parsedData).forEach(key => {
        console.log(key)
        if (['Polygon', 'Paper'].includes(key)) {
          const loop = (key === 'Paper') ? [(parsedData[key])[1]] : parsedData[key] 
          loop.forEach((entity) => {

            const color = (key === 'Paper') ? "#4F4F4F" : "#333333"

            
            const shape = new THREE.Shape();
            shape.moveTo( entity.vertices[0][0],  entity.vertices[0][1]);


            // Add line segments
            for (let i = 1; i <  entity.vertices.length; i++) {
                const [x, y] =  entity.vertices[i];
                shape.lineTo(x, y);
            }

            // Create geometry and mesh
            const geometry = new THREE.ShapeGeometry(shape);
            const material = new THREE.MeshBasicMaterial({ color: color, side: THREE.DoubleSide });
            const mesh = new THREE.Mesh(geometry, material);

            groupRef.current.add(mesh);
          })
        }  else if (['Valley', 'Mountain', 'CrimpValley', 'CrimpMountain'].includes(key)) {
          parsedData[key].forEach((entity) => {
            const start = new THREE.Vector3(entity.start[0], entity.start[1], entity.start[2]);
            const end = new THREE.Vector3(entity.end[0], entity.end[1], entity.end[2]);

            const geometry = new THREE.BufferGeometry().setFromPoints([start, end]);
          
            const material = new THREE.LineBasicMaterial({ color: entity.color, depthTest: false});
            const line = new THREE.Line(geometry, material);
            line.renderOrder = 1

            groupRef.current.add(line);
          })
        }
     
  
      
      // parsedData.dxf.entities.forEach((entity) => {
      //   if (entity.type === 'LWPOLYLINE' || entity.type === 'POLYLINE') {
      //     const points = entity.vertices.map((vertex) => new THREE.Vector3(vertex.x, vertex.y, 0));
      //     const geometry = new THREE.BufferGeometry().setFromPoints(points);
      //     const line = new THREE.Line(geometry, material);
      //     groupRef.current.add(line);
      //   }
      // });
    
      
      
      return () => groupRef.current.clear();
    }, [props.dxfData]);
    })
    return <group ref={groupRef} />;
  };



const CreaseMaker = () => {
 //aim, take in data from dxf file in data and use this to create a workable mesh in threeJS
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [info, setInfo] = useState(null);

  const fetchCrease = async () => {
    try {
      const response = await fetch('/data/data.json');
      if (!response.ok) throw new Error('Failed to fetch data');
      const data = await response.json();
      console.log('Fetched Data:', data);
      setFile(data); 
    } catch (err) {
      console.error('Error fetching JSON:', err);
      setError('No data found');
    }
  };


  const onRebuildCrease = () => {
    fetchCrease();
    setInfo(
      <Canvas camera={{ position: [0, 0, 800], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <spotLight position={[500, 500, 500]} angle={0.3} penumbra={1} intensity={1} />
        <pointLight position={[-500, -500, 500]} intensity={0.7} />
        {/* <ambientLight intensity={Math.PI / 2} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} decay={0} intensity={Math.PI} />
        <pointLight position={[-10, -10, -10]} decay={0} intensity={Math.PI} /> */}
        {file && <DrawCrease dxfData={file} position={[0, 0, 0]} />}
        {/* <Box position={[1.2, 0, 0]} /> */}
      </Canvas>
    )
  }


  useEffect(() => {
    fetchCrease();
  }, []);




  return (
    <div>
      <button onClick={onRebuildCrease}>ReBuild Crease</button>
      <div style={{width:800+'px', height:800+'px', margin:20+'px'}}>
        {info}
      </div>
      
    </div>
  );
};

export default CreaseMaker;