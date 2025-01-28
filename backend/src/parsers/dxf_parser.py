from flask import json
import ezdxf


def process_dxf_file(file_path):
    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()
    
    color_picker = {0: "#000000", 1: "#FF0000",5: "#00FF00" }
    
    parsed_data = {
        "Paper": [],
        "Polygon": [],
        "Valley": [],
        "CrimpValley": [],
        "Mountain": [],
        "CrimpMountain": []
    }
    
    # Iterate over POLYLINE entities
    #all shapes are closed in the dxf files that will be loaded in from Origmaizer 
    for layer_name in parsed_data.keys():

        for polyline in msp.query('POLYLINE[layer=="{}"]'.format(layer_name)):
            
            vertices = [(v.dxf.location.x, v.dxf.location.y, v.dxf.location.z) for v in polyline.vertices]
            color = color_picker[polyline.dxf.color]
            
            parsed_data[layer_name].append({
                "color": color,
                "vertices": vertices
            })
        
        for line in msp.query('LINE[layer=="{}"]'.format(layer_name)):
            
            start_point = (line.dxf.start.x, line.dxf.start.y, line.dxf.start.z)
            end_point = (line.dxf.end.x, line.dxf.end.y, line.dxf.end.z)
            
            color = color_picker[line.dxf.color]
            
            parsed_data[layer_name].append({
                "color": color,
                "start": start_point,
                "end": end_point
            })
    return parsed_data

def save_parsed_data_as_json(parsed_data, json_output_path):
    with open(json_output_path, 'w') as json_file:
        json.dump(parsed_data, json_file, indent=2)
        
def smooth_fold_as_json():
    pass