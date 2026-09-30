import { useContext } from "react";

import { PatternContext } from "../contexts/patternContext";


const Results = () => {
    const { foldResults} = useContext(PatternContext);

    const makeMatrix = () => {
        console.log('fds', foldResults?.angle_approx_loop_closure_matrix)
        const matrix = foldResults?.angle_approx_loop_closure_matrix ?? null
        console.log('ma', matrix)
        if (matrix != null) {
            return(
                <small><table>
                    <tr>
                        <th>{matrix[0][0]}</th>
                        <th>{matrix[0][1]}</th>
                        <th>{matrix[0][2]}</th>
                    </tr>
                    <tr>
                        <th>{matrix[1][0]}</th>
                        <th>{matrix[1][1]}</th>
                        <th>{matrix[1][2]}</th>
                    </tr>
                    <tr>
                        <th>{matrix[2][0]}</th>
                        <th>{matrix[2][1]}</th>
                        <th>{matrix[2][2]}</th>
                    </tr>
                </table></small>
            )
        }
        return <></>
    }

    // const updateFoldOptions = (e) => {
    //     console.log('Showing changes to any part of laabel')
    //     let copy = foldOptions
    //     copy[e.target.name] = e.target.value
    //     setFoldOptions(copy)
    //     console.log(e.target.name, e.target.value)
    //     console.log(foldOptions)
    // }

    return(
        <div>
        <div style={{backgroundColor: '#5868a850', color:'#000000', padding:'1rem 1rem', width:'14rem', height:'fit-content'}}>
            ∥R-I∥R<sub>F</sub> = <input name="loop_closure" type="number" value={foldResults?.angle_approx_loop_closure ?? 0} required style={{width: '9rem'}}/><br></br><br></br>
            <div style={{flexDirection: 'row'}}> 
                <div>R = X <sub>1</sub>⋅ ... ⋅X<sub>n</sub> =</div>
                <div>{makeMatrix()}</div>
            </div><br></br>
            <small>Mean of Angles</small> <input name="fold_diff" type="number" value={foldResults?.dist_from_angle_results ?? 0} required style={{width: '10rem'}}/><br></br><br></br>
            <small>Total Edge Changes</small> <input name="edge_diff" type="number" value={foldResults?.total_edge_deviation ?? 0} required style={{width: '10rem'}}/><br></br><br></br>
            <small>Total Sector Angle Changes</small> <input name="sec_diff" type="number" value={foldResults?.total_sector_angle_deviation ?? 0} required style={{width: '10rem'}}/>


        </div>
    </div>

                            
    )
}

export default Results