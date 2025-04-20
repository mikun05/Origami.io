import { useState } from 'react';
import './App.css'
import PatternLoader from './components/PatternLoader'
import { PatternContext } from './contexts/patternContext'



function App() {
  const [focusedVertexIndex, setFocusedVertexIndex] = useState(null);
  const [focusedVertexEdges, setFocusedVertexEdges] = useState(null);
  const [focusedEdgeIndex, setFocusedEdgeIndex] = useState(null);
  const [foldPattern, setFoldPattern] = useState(null);
  const [foldOptions, setFoldOptions] = useState({
    angleApproxMeth: 'SQP',
    angleMaxIt:200000,
    angleFTol:10,
    angleEps:14,
    vertexPointMeth: 'Rot',
    vertexMaxIt:300,
    vertexFTol:8,
    vertexEps:8,
    
  })
  const [uniformAngle, setUniformAngle] = useState(180)
  const [foldResults, setFoldResults] = useState(null)
 
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap:'1rem'}} >
        <PatternContext.Provider value={{ focusedVertexIndex, setFocusedVertexIndex, focusedEdgeIndex, setFocusedEdgeIndex, focusedVertexEdges, setFocusedVertexEdges, foldPattern, setFoldPattern, foldOptions, setFoldOptions, uniformAngle, setUniformAngle, foldResults, setFoldResults }}>                           
          <PatternLoader />
        </PatternContext.Provider>
    </div>
  )
}

export default App
