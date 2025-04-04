import { useContext } from "react";

import { PatternContext } from "../contexts/patternContext";


const ApproxOptions = () => {
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
    <div style={{backgroundColor: '#fbfbfa', color:'#000000', padding:'1rem 1rem', width:'14rem'}}>
                            <label onChange={(e) => updateFoldOptions(e)}>
                                <div style={{margin: 'auto', textAlign:'center'}}>OPTIONS</div> 
                                <br></br><br></br>
                                {"Angle Method:    "}
                                    <select name="angleApproxMeth" type="text" defaultValue="LBFGS" required style={{width: '10rem'}}> 
                                        <option value="GD">Gradient Descent</option>
                                        <option value="LBFGS">Limited-memory BFGS</option>
                                        <option value="Pos_Anneal_LBFGS">Positive Annealing LBFGS</option>
                                        <option value="Neg_Anneal_LBFGS">Negative Annealing LBFGS</option>
                                        <option value="SQP">Sequential Least Squares Programming</option>
                                    </select>
                                <br></br><br></br>
                                {"Max Iterations:   "}
                                    <input name="angleMaxIt" type="number" defaultValue="200000"required style={{width: '5rem'}}/>
                                <br></br><br></br>

                                ftol (1e-n): <input name="angleFTol" type="number" defaultValue="15" max="15" min="0" required style={{width: '2rem'}}/>  <small>min: 1e-15</small><br></br>
                                eps (1e-n): <input name="vertexEps" defaultValue="14" type="number" max="15" min="0" required style={{width: '2rem'}}/> <small>min: 1e-15</small>
                                <br></br><br></br><br></br>

                                <hr style={{borderTop: '3px dashed #bbb'}}></hr>
                                <br></br>


                                {"Vertex Method:    "}
                                    <select name="vertexPointMeth" type="text" defaultValue="Rot" required style={{width: '10rem'}}> 
                                        <option value="Rot">Rotation</option>
                                        <option value="SQP">Sequential Least Squares Programming</option>
                                    </select>
                                <br></br><br></br>
                                {"Max Iterations:   "}
                                    <input name="vertexMaxIt" type="number" defaultValue="300" required style={{width: '5rem'}}/>
                                <br></br><br></br>

                                ftol (1e-n): <input name="vertexFTol" defaultValue="8" type="number" max="15" min="0" required style={{width: '2rem'}}/> <small>min: 1e-15</small><br></br>
                                eps (1e-n): <input name="vertexEps" defaultValue="8" type="number" max="15" min="0" required style={{width: '2rem'}}/> <small>min: 1e-15</small>

                            </label>
    </div>

                        
)
}

export default ApproxOptions