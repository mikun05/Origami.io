import { useContext } from "react";

import { PatternContext } from "../contexts/patternContext";
import axios from "axios";
import { backendLink } from "./PatternLoader";


const Options = () => {
    const {foldPattern, setFoldPattern} = useContext(PatternContext)

    const updateFoldPattern = (e) => {
        console.log(e)
        const patternId = e.target.value
       

        axios.post(`${backendLink}/get-fold-pattern`, { patternId })
        .then(response => {
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
                        <option value="wbb">Waterbomb Base </option>
                        <option value="bf">Book Fold</option>
                        <option value="mo_single">Miura Ori Fold - Single Vertex</option>
                        <option value="bel_fig_2">Belcastro Figure 2</option>
                    </select>
            </label>
        </div>
        <br></br>
        <div style={{backgroundColor: '#5868a8', color:'#fbfbfa', padding:'1rem 1rem', width:'14rem', height:'fit-content'}}>
            <label >
                {"Origami Model:    "}
                    <select name="modelOptions" type="text"  defaultValue="CBH" required style={{width: '14rem', backgroundColor:'#fbfbfa'}}> 
                        <option value="CBH">Custom Bar-Hinge Model</option>
                        <option value="TSBH">Torsional Spring Bar-Hinge Model</option>
                        <option value="TSS">Truss Model</option>
                    </select>
            </label>
        </div>
    </div>

                        
)
}

export default Options