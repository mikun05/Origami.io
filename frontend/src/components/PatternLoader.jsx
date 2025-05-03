/* eslint-disable no-unused-vars */
/* eslint-disable react/prop-types */

import { useState, useEffect, useContext } from "react";
import { Canvas } from '@react-three/fiber';
import axios from "axios";
import PatternViewer from "./PatternViewer";
import { PatternContext } from "../contexts/patternContext";
import VertexViewer from "./VertexViewer";
import ApproxOptions from "./ApproxOptions";
import Options from "./Options";
import Results from "./Results";

export const backendLink = 'http://127.0.0.1:5000';


const FoldVertexDialogue = (props) => {
    const { focusedVertexIndex, setFoldPattern, foldOptions, setFoldOptions, uniformAngle, setUniformAngle, setFoldResults, foldResults, origamiModel} = useContext(PatternContext);
    const [vertexPoint, setVertexPoint] = useState([0,0,0])
    const pattern = props.pattern

    useEffect(() => {
        if (!pattern) return
        console.log('pattern')
        console.log(pattern['fold_format'])
        console.log(focusedVertexIndex)
        setVertexPoint(pattern['fold_format'][0]['vertices'][focusedVertexIndex] ?? [])
    }, [pattern, focusedVertexIndex])


    const handleFoldEdge = (inputAngle) => {
        if (focusedVertexIndex === undefined || focusedVertexIndex === null || inputAngle == null) return;
        // e.preventDefault();

        // const form = e.target;
        // const formData = new FormData(form);
        const vertexIndex = focusedVertexIndex
        const angle = Number(inputAngle)
        const sym = 0

        const angleApproxMeth = foldOptions.angleApproxMeth
        const angleMaxIt = Number(foldOptions.angleMaxIt)
        const angleFTol = Math.pow(10, -Number(foldOptions.angleFTol))
        const angleEps = Math.pow(10, -Number(foldOptions.angleEps));
        const vertexPointMeth = foldOptions.vertexPointMeth
        const vertexMaxIt = Number(foldOptions.vertexMaxIt)
        const vertexFTol = Math.pow(10, -Number(foldOptions.vertexFTol));
        const vertexEps = Math.pow(10, -Number(foldOptions.vertexEps));
        
        axios.post(`${backendLink}/fold-edge-around-vertex`, { vertexIndex, angle, sym, angleApproxMeth, angleMaxIt, angleFTol, angleEps, vertexPointMeth,vertexMaxIt, vertexFTol, vertexEps, origamiModel})
            .then(response => {
                props.changeSetUp(false)
                setFoldPattern(response.data.pattern); 
                setFoldResults(response.data.approx_results);  
            })
            .catch(error => console.error("Error folding around vertex:", error));
    };

    // useEffect(() => {
    //     handleFoldEdge(uniformAngle)
    // }, [uniformAngle])
      
      


    return(
        <div>
            <label>
           
            <div style={{display: 'flex', flexDirection: 'row', gap: '1rem'}}>
            <div><strong>Vertex {focusedVertexIndex}:</strong></div>
            <div><strong>{"("}{Math.round(vertexPoint[0] * 100) / 100} {","}</strong></div>
            <div><strong>{Math.round(vertexPoint[1] * 100) / 100} {","}</strong></div>
            <div><strong>{Math.round(vertexPoint[2] * 100) / 100}{")"}</strong></div>
            </div>
            Uniform(ish) Fold by: <br></br>
            <input onChange={(e) => {setUniformAngle(e.target.value)}} name="uniformFoldEdgesAroundVertexAngle" type="number" defaultValue={uniformAngle} value={uniformAngle} min="0" max="180" required style={{width: '1.5rem'}}/>°
            </label>
            <br></br><br></br>
            <div style={{display:'flex', flexDirection: 'row', gap:'0.5rem'}}>
                <button onClick={() => handleFoldEdge(uniformAngle)} style={{height: '2rem', width:'5rem', padding:'auto', fontSize: '0.8rem'}}>Fold</button>
            </div>
        </div>
    )
}

const FoldEdgeDialogue = (props) => {
    const { focusedEdgeIndex, focusedVertexIndex, setFoldPattern, foldPattern, setUniformAngle, foldOptions, setFoldResults } = useContext(PatternContext)
    const [currentAngle, setCurrentAngle] = useState(null)
    const [sectorAngle, setSectorAngle] = useState(null)
    const [flatSectorAngle, setflatSectorAngle] = useState(null)
    const [length, setLength] = useState(null)
    const [flatLength, setFlatLength] = useState(null)



    const [foldType, setFoldType] = useState('B')
    const [relativeEdgeIndex, setRelativeEdgeIndex] = useState(0)



    useEffect(() => {
        if (focusedVertexIndex === undefined || focusedVertexIndex === null || focusedEdgeIndex === undefined || focusedEdgeIndex === null) return;

        console.log('doing angle stuff')
        const vertexIndex = focusedVertexIndex
        const edgeIndex = focusedEdgeIndex 

        axios.get(`${backendLink}/get-edge-info`, { params: { vertexIndex, edgeIndex }})
        .then(response => {
            console.log('angle', response.data['angle'])
            setCurrentAngle( Math.round(response.data['angle'] * (180/Math.PI) * 100) / 100);
            setFoldType(response.data['fold_type'])
            setRelativeEdgeIndex(response.data['id'][1])
            setFlatLength(response.data['flat_length'])
            setLength(response.data['length'])
            setflatSectorAngle(response.data['flat_sector'])
            setSectorAngle(response.data['sector'])

        })
        .catch(error => console.error("Error fetching angle data:", error));
    }, [focusedEdgeIndex, focusedVertexIndex])

    const handleAngleChange = (e) => {
        const value = e.target.value;
        // Allow empty string for better UX (so user can clear the field)
        setCurrentAngle(value === '' ? '' : Number(value));
    };

    
    
    const handleFoldEdge = (e) => {
        if (focusedVertexIndex === undefined || focusedVertexIndex === null || focusedEdgeIndex === undefined || focusedEdgeIndex === null) return;
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const vertexIndex = focusedVertexIndex
        const edgeIndex = focusedEdgeIndex
        const angle = Number(formData.get('foldEdge'))
        const sym = Number(formData.get('foldSym'))
        const slider = false

        const angleApproxMeth = foldOptions.angleApproxMeth
        const angleMaxIt = Number(foldOptions.angleMaxIt)
        const angleFTol = Math.pow(10, -Number(foldOptions.angleFTol))
        const angleEps = Math.pow(10, -Number(foldOptions.angleEps));
        const vertexPointMeth = foldOptions.vertexPointMeth
        const vertexMaxIt = Number(foldOptions.vertexMaxIt)
        const vertexFTol = Math.pow(10, -Number(foldOptions.vertexFTol));
        const vertexEps = Math.pow(10, -Number(foldOptions.vertexEps));
        
        axios.post(`${backendLink}/fold-edge`, { vertexIndex, edgeIndex, angle, sym, angleApproxMeth, angleMaxIt, angleFTol, angleEps, vertexPointMeth,vertexMaxIt, vertexFTol, vertexEps, slider})
            .then(response => {
                setFoldPattern(response.data.pattern); 
                setFoldResults(response.data.approx_results);  
            })
            .catch(error => console.error("Error folding edge:", error));
    };


    return(
        <form method="post" onSubmit={handleFoldEdge}>
            <label>
            <strong>{foldType == 'M' ? 'Mountain' : 'Valley'} Edge {relativeEdgeIndex}<br></br></strong>
            Dihedral Angle: <input name="foldEdge" type="number" value={currentAngle} onChange={handleAngleChange} min="0" max="180" required style={{width: '3rem'}}/>°<br></br>
            Flat Sector Angle: {flatSectorAngle}°<br></br>
            Sector Angle: {sectorAngle}°<br></br>
            Flat Length: {flatLength}<br></br>
            Current Length:  {length}<br></br>
            <br></br>
            </label>
            <div style={{display:'flex', flexDirection: 'row', gap:'0.5rem'}}>
                <button type="submit" style={{height: '2.2rem', width:'5rem', padding:'auto', fontSize: '0.8rem'}}>Fold</button>
            </div>
        </form>
    )
}

const PatternLoader = () => {
    const { origamiModel, foldOptions, setFoldOptions, focusedVertexIndex, foldPattern, setFoldPattern, setFocusedEdgeIndex, focusedEdgeIndex, setUniformAngle, uniformAngle, setFoldResults} = useContext(PatternContext);
    const [setUp, changeSetUp] = useState(false)

    useEffect(() => {
        fetchFoldPattern();
    }, []);

    const fetchFoldPattern = () => {
        axios.post(`${backendLink}/get-fold-pattern`, { patternId: 'wbb' })
            .then(response => {
                changeSetUp(true)
                setFoldPattern(response.data);
            })
            .catch(error => console.error("Error fetching pattern data:", error));
    };

    // const handleFoldEdge = (vertexIndex, edgeIndex, angle, sym) => {
    //     axios.post(`${backendLink}/fold-edge`, { vertexIndex, edgeIndex, angle, sym })
    //         .then(response => {
    //             changeSetUp(false)
    //             setFoldPattern(response.data);  // Update with new fold state
    //         })
    //         .catch(error => console.error("Error folding edge:", error));
    // };

    const resetPattern = () => {
        setUniformAngle(180)
        axios.get(`${backendLink}/reset-pattern`)
        .then(response => {
            changeSetUp(true)
            setFoldPattern(response.data);  // Reset to pre-fold configuraton
        })
        .catch(error => console.error("Error resetting pattern:", error));


    }

    const handleFoldEdge = (inputAngle, slide) => {
        if (focusedVertexIndex === undefined || focusedVertexIndex === null || inputAngle == null) return;
        // e.preventDefault();

        // const form = e.target;
        // const formData = new FormData(form);
        const slider = slide
        const vertexIndex = focusedVertexIndex
        const angle = Number(inputAngle)
        const sym = 0

        const angleApproxMeth = foldOptions.angleApproxMeth
        const angleMaxIt = Number(foldOptions.angleMaxIt)
        const angleFTol = Math.pow(10, -Number(foldOptions.angleFTol))
        const angleEps = Math.pow(10, -Number(foldOptions.angleEps));
        const vertexPointMeth = foldOptions.vertexPointMeth
        const vertexMaxIt = Number(foldOptions.vertexMaxIt)
        const vertexFTol = Math.pow(10, -Number(foldOptions.vertexFTol));
        const vertexEps = Math.pow(10, -Number(foldOptions.vertexEps));
        
        axios.post(`${backendLink}/fold-edge-around-vertex`, { origamiModel, vertexIndex, angle, sym, angleApproxMeth, angleMaxIt, angleFTol, angleEps, vertexPointMeth,vertexMaxIt, vertexFTol, vertexEps, slider})
            .then(response => {
                changeSetUp(false)
                setFoldPattern(response.data.pattern); 
                setFoldResults(response.data.approx_results);  
            })
            .catch(error => console.error("Error folding around vertex:", error));
    };

    // useEffect(() => {
    //     handleFoldEdge(uniformAngle)
    // }, [uniformAngle])
      

    return (
        <div>    
            {foldPattern ? (
                <div style={{display: 'flex', flexDirection: 'column', height: '50rem', margin: 'auto', padding:'0rem 2rem', gap: '1rem' }}>
                    <br></br>
                    <br></br>

                    <div style={{display: 'flex', flexDirection: 'row', margin:'auto', gap:'1rem'}}> 

                        <div style={{ width:'15rem'}}>
                            <h2 style={{margin: 'auto'}}>Fold Pattern Viewer</h2>
                            <br></br>
                            {(focusedVertexIndex !== null) ? <FoldVertexDialogue pattern={foldPattern} changeSetUp={changeSetUp}/> : <></>}
                            <br></br><br></br>
                            {(focusedEdgeIndex !== null) ? <FoldEdgeDialogue  /> : <></>}
                            <VertexViewer vertexIndex={focusedVertexIndex} pattern={foldPattern}/>
                            <br></br><br></br><br></br>
                            <button onClick={resetPattern} style={{height: '3rem', margin: 'auto', }}>Reset Fold Pattern</button>

                        </div>


                        <div  style={{ width: '50rem', height: '40rem', backgroundColor: '#E2DCCB', margin:'auto'}}>
                            <Canvas >
                                <PatternViewer pattern={foldPattern} setUp={setUp}/>
                            </Canvas>

                            <input 
                                type="range" 
                                onInput={(e) => {setUniformAngle(e.target.value); handleFoldEdge(e.target.value, true)}}  
                                // onPointerUp={(e) => {setUniformAngle(e.target.value); handleFoldEdge(e.target.value, false)}}  
                                onMouseUp={(e) => {setUniformAngle(e.target.value); handleFoldEdge(e.target.value, false)}}  
                                name="uniformFoldEdgesAroundVertexAngle" value={uniformAngle} min="0" max="180" required />
                        </div>

                        <div style={{flexDirection: 'column', gap:'2rem'}}>
                            <ApproxOptions />
                            <br></br> <br></br>
                            <Results />
                        </div>
                        <div style={{flexDirection: 'column', gap:'2rem'}}>
                            <Options setUp={setUp} changeSetUp={changeSetUp} />
                            <br></br><br></br>


                        </div>
                        

                        
                    </div>

                    <div style={{display: 'flex', flexDirection: 'row', backgroundColor: '#fbfbfa', width:'100rem', gap: '1rem', margin:'auto' }}> 
                            {'AAAHHHH!!! FML'}
                            {/* onInput changes for every slide change regardless of whether the slider has stopped, onChange on triggers once slider stops and mouse press is false */}
                            
                    </div>
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
};

export default PatternLoader;
