from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import os

from parsers.dxf_parser import process_dxf_file, save_parsed_data_as_json

dxf_upload_bp = Blueprint('dxf_upload', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../../../visualiser/public/data')
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


def save_dxf_file(file, type):
        file_path = os.path.join(UPLOAD_FOLDER, 'rawdata.dxf')
        file.save(file_path)  #saves raw data from dxf
        
        parsed_data = process_dxf_file(file_path)
        parsed_data_file_path = os.path.join(UPLOAD_FOLDER, 'data.json') #saves parsed data from dxf
        
        # fold_file = convert_to_fold(file_path)
        # fold_file_file_path = os.path.join(UPLOAD_FOLDER, 'data.fold') #saves parsed data from dxf

        save_parsed_data_as_json(parsed_data, parsed_data_file_path)
        #save_parsed_data_as_json(fold_file, fold_file_file_path)

        return jsonify(message=f"{type} file saved successfully")
    
