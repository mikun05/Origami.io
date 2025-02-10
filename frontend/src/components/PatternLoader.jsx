/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */

import { useState, useEffect, useContext } from "react";
import { Canvas } from '@react-three/fiber';
import axios from "axios";
import PatternViewer from "./PatternViewer";
import { PatternContext } from "../contexts/patternContext";
import VertexViewer from "./VertexViewer";

export const backendLink = 'http://127.0.0.1:5000';


const FoldVertexDialogue = (props) => {
    const { focusedVertexIndex, setFoldPattern } = useContext(PatternContext);
    const [vertexPoint, setVertexPoint] = useState([0,0,0])
    const pattern = props.pattern

    useEffect(() => {
        if (!pattern) return
        setVertexPoint(pattern['fold_format'][0]['vertices'][focusedVertexIndex])
    }, [pattern, focusedVertexIndex])

    const handleFoldEdge = (e) => {
        if (focusedVertexIndex === undefined || focusedVertexIndex === null) return;
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const vertexIndex = focusedVertexIndex
        const angle = Number(formData.get('uniformFoldEdgesAroundVertexAngle'))
        const sym = Number(formData.get('uniformFoldEdgesAroundVertexSym'))
        
        axios.post(`${backendLink}/fold-edge-around-vertex`, { vertexIndex, angle, sym})
            .then(response => {
                setFoldPattern(response.data);  
            })
            .catch(error => console.error("Error folding around vertex:", error));
    };

    const resetPattern = () => {
        axios.get(`${backendLink}/reset-pattern`)
        .then(response => {
            setFoldPattern(response.data);  // Reset to pre-fold configuraton
        })
        .catch(error => console.error("Error resetting pattern:", error));
    }


    return(
        <form method="post" onSubmit={handleFoldEdge} onReset={resetPattern}>
            <label>
            Uniform Fold around <br></br><br></br>
            x: {vertexPoint[0]} <br></br>
            y: {vertexPoint[1]} <br></br>
            z:  {vertexPoint[2]}
            <br></br><br></br> by: <br></br>
            Angle: <input name="uniformFoldEdgesAroundVertexAngle" type="number" defaultValue={180} min="0" max="180" required style={{width: '3rem'}}/>°
            <br></br>
            Sym: <input name="uniformFoldEdgesAroundVertexSym" type="number" defaultValue={0.5} step="0.1" min="0" max="1" required style={{width: '2.5rem'}}/>
            {/* <br></br>
            <hr />
                <label>
                    Fix Edges around vertex: <input type="checkbox" name="fixEdgesAroundVertex" />
                </label>
            <hr /> */}
            </label>
            <br></br> <br></br>
            <div style={{display:'flex', flexDirection: 'row', gap:'0.5rem'}}>
                <button type="submit" style={{height: '2.2rem', width:'5rem', padding:'auto', fontSize: '0.8rem'}}>Fold</button>
                <button type="reset" style={{height: '2.2rem', width:'5rem', padding:'auto', fontSize: '0.8rem'}}>Reset</button>
            </div>
        </form>
    )
}

const FoldEdgeDialogue = (props) => {
    const { focusedEdgeIndex, focusedVertexIndex, setFoldPattern } = useContext(PatternContext)

    const handleFoldEdge = (e) => {
        if (focusedVertexIndex === undefined || focusedVertexIndex === null || focusedEdgeIndex === undefined || focusedEdgeIndex === null) return;
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const vertexIndex = focusedVertexIndex
        const edgeIndex = focusedEdgeIndex / 2
        const angle = Number(formData.get('foldEdge'))
        const sym = 1
        
        axios.post(`${backendLink}/fold-edge`, { vertexIndex, edgeIndex, angle, sym})
            .then(response => {
                setFoldPattern(response.data);
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

    return(
        <form method="post" onSubmit={handleFoldEdge} onReset={resetPattern}>
            <label>
            Fold around edge by: <br></br>
            <input name="foldEdge" type="number" defaultValue={180} required style={{width: '4rem'}}/>°
            </label>
            <div style={{display:'flex', flexDirection: 'row', gap:'0.5rem'}}>
                <button type="submit" style={{height: '2.2rem', width:'5rem', padding:'auto', fontSize: '0.8rem'}}>Fold</button>
                <button type="reset" style={{height: '2.2rem', width:'5rem', padding:'auto', fontSize: '0.8rem'}}>Reset</button>
            </div>
        </form>
    )
}

const PatternLoader = () => {
    const { focusedVertexIndex, foldPattern, setFoldPattern, setFocusedEdgeIndex, focusedEdgeIndex} = useContext(PatternContext);

    useEffect(() => {
        fetchFoldPattern();
    }, []);

    const fetchFoldPattern = () => {
        axios.get(`${backendLink}/get-fold-pattern`)
            .then(response => {
                setFoldPattern(response.data);
            })
            .catch(error => console.error("Error fetching pattern data:", error));
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

                    <div style={{display: 'flex', flexDirection: 'row', margin:'auto', gap:'1rem'}}> 

                        <div style={{ width:'15rem'}}>
                            <h2 style={{margin: 'auto'}}>Fold Pattern Viewer</h2>
                            <br></br>
                            {(focusedVertexIndex !== null) ? <FoldVertexDialogue pattern={foldPattern} /> : <></>}
                            <br></br><br></br>
                            {(focusedEdgeIndex !== null) ? <FoldEdgeDialogue  /> : <></>}
                            <VertexViewer vertexIndex={focusedVertexIndex} pattern={foldPattern}/>
                        </div>


                        <div  style={{ width: '50rem', height: '30rem', backgroundColor: '#fc6c8530', margin:'auto'}}>
                            <Canvas >
                                <PatternViewer pattern={foldPattern} />
                            </Canvas>
                        </div>

                        
                    </div>

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
