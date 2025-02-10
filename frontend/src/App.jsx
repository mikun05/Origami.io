import { useState } from 'react';
import './App.css'
import PatternLoader from './components/PatternLoader'
import { PatternContext } from './contexts/patternContext'



function App() {
  const [focusedVertexIndex, setFocusedVertexIndex] = useState(null);
  const [focusedVertexEdges, setFocusedVertexEdges] = useState(null);
  const [focusedEdgeIndex, setFocusedEdgeIndex] = useState(null);
  const [foldPattern, setFoldPattern] = useState(null);
 
  return (
    <div style={{display: 'flex', flexDirection: 'column', gap:'1rem'}}>
        <PatternContext.Provider value={{ focusedVertexIndex, setFocusedVertexIndex, focusedEdgeIndex, setFocusedEdgeIndex, focusedVertexEdges, setFocusedVertexEdges, foldPattern, setFoldPattern }}>                           
          <PatternLoader />
        </PatternContext.Provider>
    </div>
  )
}

export default App
