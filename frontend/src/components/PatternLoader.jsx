/* eslint-disable no-unused-vars */
import { useState, useEffect, useContext } from "react";
import { Canvas } from '@react-three/fiber';
import axios from "axios";
import PatternViewer from "./PatternViewer";
import { PatternContext } from "../contexts/patternContext";
import VertexViewer from "./VertexViewer";

export const backendLink = 'http://127.0.0.1:5000';


const PatternLoader = () => {
    const [foldPattern, setFoldPattern] = useState(null);

    const { focusedVertexIndex } = useContext(PatternContext);
   

    const [focusedEdge, setFocusedEdge] = useState(null);


    useEffect(() => {
        console.log('fetching')
        fetchFoldPattern();
    }, []);

    

    const fetchFoldPattern = () => {
        axios.get(`${backendLink}/get-fold-pattern`)
            .then(response => {
                setFoldPattern(response.data);
            })
            .catch(error => console.error("Error fetching pattern data:", error));
    };


    const fetchFoldEdge = (vertexIndex, edgeIndex) => {
        axios.get(`${backendLink}/get-edge-info`, { vertexIndex, edgeIndex })
            .then(response => {
                setFocusedEdge(response.data);
            })
            .catch(error => console.error("Error fetching edge data:", error));
    };

    const handleFoldEdge = (vertexIndex, edgeIndex, angle, sym) => {
        axios.post(`${backendLink}/fold-edge`, { vertexIndex, edgeIndex, angle, sym })
            .then(response => {
                setFoldPattern(response.data);  // Update with new fold state
            })
            .catch(error => console.error("Error folding edge:", error));
    };

    const resetPattern = () => {
        axios.get(`${backendLink}/reset-pattern`)
        .then(response => {
            setFoldPattern(response.data);  // Reset to pre-fold configuraton
        })
        .catch(error => console.error("Error resetting pattern:", error));
    }



    return (
        <div>
            
            {foldPattern ? (
                <div style={{display: 'flex', flexDirection: 'column', width: '80rem', height: '50rem', margin: 'auto', gap: '1rem' }}>
                    <br></br>
                    <br></br>

                    <h2>Fold Pattern Viewer</h2>
                    <div style={{display: 'flex', flexDirection: 'row', margin:'auto', gap:'1rem'}}> 

                        <div style={{display: 'flex', flexDirection: 'column', width:'15rem'}}>
                            <VertexViewer vertexIndex={focusedVertexIndex} pattern={foldPattern}/>
                        </div>


                        <div  style={{ width: '50rem', height: '30rem', backgroundColor: '#fc6c8530', margin:'auto'}}>
                            <Canvas 
                                camera={{ position: [0, 0, 5], fov: 50 }} resize={{ debounce: 0 }}>
                                    {/* <OrbitControls enablePan={true} enableRotate={true} /> */}
                                    <axesHelper size={5} />
                                    <PatternViewer pattern={foldPattern} />

                            </Canvas>
                        </div>

                        
                    </div>

                    
                    

                    {/* <pre>{JSON.stringify(foldPattern, null, 2)}</pre> */}
                    <div style={{display: 'flex', flexDirection: 'row', width:'60rem', gap: '1rem', margin:'auto' }}> 
                        <div style={{display: 'flex', flexDirection: 'column', width:'15rem', gap: '1rem' }}>
                            <p>Test Cases: <br></br>Fold first valley fold from left by 90 degrees:</p>
                            <button onClick={() => handleFoldEdge(1, 0, 90, 0.5)}>
                                evenly (0.5)
                            </button>

                            <button onClick={() => handleFoldEdge(1, 0, 90, 1)}>
                                right face fold (1)
                            </button>

                            <button onClick={() => handleFoldEdge(1, 0, 90, 0)}>
                                left face fold (0)
                            </button>
                        </div>

                        <div style={{display: 'flex', flexDirection: 'column', width:'15rem', gap: '1rem' }}>
                            <p>Test Cases: <br></br>Fold second mountain fold from left by 45 degrees:</p>
                            <button onClick={() => handleFoldEdge(2, 0, 45, 0.5)}>
                                evenly (0.5)
                            </button>

                            <button onClick={() => handleFoldEdge(2, 0, -45, 0.7)}>
                                right:0.7, left:0.3
                            </button>

                            <button onClick={() => handleFoldEdge(2, 0, -45, 0.2)}>
                                right:0.2, left:0.8
                            </button>
                        </div>

                        <button onClick={resetPattern} style={{height: '4rem', margin: 'auto'}}>Reset Fold Pattern</button>
                    </div>
                </div>
            ) : (
                <p>Loading...</p>
            )}

        </div>
    );
};

export default PatternLoader;
