import { useState, useEffect } from "react";
import axios from "axios";
import PatternViewer from "./PatternViewer";

const PatternLoader = () => {
    const [foldPattern, setFoldPattern] = useState(null);
    const [focusedVertex, setFocusedVertex] = useState(null);
    const [focusedEdge, setFocusedEdge] = useState(null);

    const backendLink = 'http://127.0.0.1:5000';

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

    const fetchFoldVertex = (vertexIndex) => {
        axios.get(`${backendLink}/get-vertex-info`, { vertexIndex })
            .then(response => {
                setFocusedVertex(response.data);
            })
            .catch(error => console.error("Error fetching veretx data:", error));
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

    return (
        <div>
            <h2>Fold Pattern Viewer</h2>
            {foldPattern ? (
                <div>
                    <PatternViewer pattern={foldPattern['fold_format'][0]} />

                    <pre>{JSON.stringify(foldPattern, null, 2)}</pre>
                    
                </div>
            ) : (
                <p>Loading...</p>
            )}
        </div>
    );
};

export default PatternLoader;
