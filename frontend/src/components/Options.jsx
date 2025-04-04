import { useContext } from "react";

import { PatternContext } from "../contexts/patternContext";


const Options = () => {
    const { foldOptions, setFoldOptions} = useContext(PatternContext);

    const updateFoldOptions = (e) => {
        console.log('Showing changes to any part of laabel')
        let copy = foldOptions
        copy[e.target.name] = e.target.value
        setFoldOptions(copy)
        console.log(e.target.name, e.target.value)
        console.log(foldOptions)
    }

return(
    <div>
    <div style={{backgroundColor: '#5868a8', color:'#fbfbfa', padding:'1rem 1rem', width:'14rem', height:'fit-content'}}>
        <label onChange={(e) => updateFoldOptions(e)}>
            {"Patterns:    "}
                <select name="patternOptions" type="text"  defaultValue="WBB" required style={{width: '10rem', backgroundColor:'#fbfbfa'}}> 
                    <option value="WBB">Waterbomb Base </option>
                    <option value="BF">Book Fold</option>
                    <option value="MOF_Single">Miura Ori Fold - Single Vertex</option>
                </select>
        </label>
    </div>
    <br></br>
    <div style={{backgroundColor: '#5868a8', color:'#fbfbfa', padding:'1rem 1rem', width:'14rem', height:'fit-content'}}>
        <label onChange={(e) => updateFoldOptions(e)}>
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