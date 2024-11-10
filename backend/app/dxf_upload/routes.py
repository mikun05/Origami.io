from flask import Blueprint, json, jsonify, request
from flask_cors import cross_origin
import os
import ezdxf

dxf_upload_bp = Blueprint('dxf_upload', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../../../frontend/public/data')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@dxf_upload_bp.route('/data', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == "POST":
        file = request.files['file']
        
        if file.filename == '':
            return('no file uploaded')
        
        elif file.filename.endswith('.dxf'):
            return save_dxf_file(file, '.dxf')
        
        # elif file.filename.endswith('.obj'):
        #     # file_contents = file.read()
        #     # display_content = process_dxf_file(file_contents)  
        #     return save_dxf_file(file, 'obj')
        
        else:
            return ("File type not allowed. Please upload a .dxf file.")
    
    return('WE NOT POSTING...')
        
        
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

def save_dxf_file(file, type):
        file_path = os.path.join(UPLOAD_FOLDER, 'rawdata.dxf')
        file.save(file_path)  #saves raw data from dxf
        
        parsed_data = process_dxf_file(file_path)
        parsed_data_file_path = os.path.join(UPLOAD_FOLDER, 'data.json') #saves parsed data from dxf

        save_parsed_data_as_json(parsed_data, parsed_data_file_path)
        return jsonify(message=f"{type} file saved successfully")
    

