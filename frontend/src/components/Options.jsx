/* eslint-disable no-unused-vars */
 /* eslint-disable react/prop-types */
/* eslint-disable react/no-unknown-property */
import { useContext } from "react";

import { PatternContext } from "../contexts/patternContext";
import axios from "axios";
import { backendLink } from "./PatternLoader";


const Options = (props) => {
    const {foldPattern, setFoldPattern} = useContext(PatternContext)

    const updateFoldPattern = (e) => {
        console.log(e)
        const patternId = e.target.value
    

        axios.post(`${backendLink}/get-fold-pattern`, { patternId })
        .then(response => {
            props.changeSetUp(true)
            setFoldPattern(response.data); 
        })
        .catch(error => console.error("Error fetching pattern data:", error));
    
        console.log(foldPattern)
    }

    

    return(
        <div>
        <div style={{backgroundColor: '#5868a8', color:'#fbfbfa', padding:'1rem 1rem', width:'14rem', height:'fit-content'}}>
            <label onChange={(e) => updateFoldPattern(e)}>
                {"Patterns:    "}
                    <select name="patternOptions" type="text"  defaultValue="WBB" required style={{width: '10rem', backgroundColor:'#fbfbfa'}}> 
                        <optgroup label="Single-Vertex">
                            <option value="wbb">Waterbomb Base </option>
                            <option value="bf">Book Fold</option>
                            <option value="mo_single">Miura Ori Fold - Single Vertex</option>
                            <option value="ico_star">Icosahedron</option>
                            <option value="bel_fig_2">Belcastro Figure 2</option>
                            <option value="bel_fig_2_A">Belcastro Figure 2A</option> 
                        </optgroup>
                        <optgroup label="Multi-Vertex">
                            <option value="mo_double">Miura Ori Fold - Two Vertices</option>
                            <option value="three_sq">Three Squares</option>
                            <option value="four_sq">Four Squares</option>
                        </optgroup>
                    </select>
            </label>
        </div>
        <br></br>
        <div style={{backgroundColor: '#5868a8', color:'#fbfbfa', padding:'1rem 1rem', width:'14rem', height:'fit-content'}}>
            <label >
                {"Origami Model:    "}
                    <select name="modelOptions" type="text"  defaultValue="CRR" required style={{width: '14rem', backgroundColor:'#fbfbfa'}}> 
                        <option value="CBH">Custom Bar-Hinge Model</option>
                        <option value="CRR">Custom Rigid Rotational</option>
                    </select>
            </label>
        </div>
    </div>

                        
)
}

export default Options