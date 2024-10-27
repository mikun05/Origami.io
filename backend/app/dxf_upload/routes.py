from flask import Blueprint, request
from flask_cors import cross_origin
import os

dxf_upload_bp = Blueprint('dxf_upload', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../../../data')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@dxf_upload_bp.route('/data', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == "POST":
        file = request.files['file']
        
        if file.filename == '':
            return('no file uploaded')
        
        elif file.filename.endswith('.dxf'):
            # file_contents = file.read()
            # display_content = process_dxf_file(file_contents)  
            return save_dxf_file(file)
        else:
            return "File type not allowed. Please upload a .dxf file."
    
    return 'WE NOT POSTING...'
        
        
def process_dxf_file(contents):
    return []


def save_dxf_file(file):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)  
        return f"File saved successfully to {file_path}"
    

