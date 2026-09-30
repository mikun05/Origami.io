import { useState } from 'react';
import CreaseMaker from './CreaseMaker';
import { fileContext } from '../contexts/fileContext';


const CreaseLoader = () => {
  const [file, setFile] = useState(null);
  const [creasableFile, setCreasableFile] = useState(null);
  const [responseMessage, setResponseMessage] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files) {
      console.log(e.target.files)
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent the default form submission

    if (!file) {
      setResponseMessage('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/data', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const result = await response.json();
      setResponseMessage(result.message); // Display server response
      fetchCrease()
    } catch (error) {
      setResponseMessage('Error uploading file.');
      console.error('Error:', error);
    }
  };

  const fetchCrease = async () => {
    
    try {
      const response = await fetch('/data/data.json');
      if (!response.ok) throw new Error('Failed to fetch data');
      const data = await response.json();
      console.log('Fetched Data:', data);
      setCreasableFile(data); 
    } catch (err) {
      console.error('Error fetching JSON:', err);
    }
  };



  return (
    <div style={{margin:'auto', display: 'flex', flexDirection: 'column'}}>
      <form style={{margin:'auto'}} onSubmit={handleSubmit} encType="multipart/form-data">
        <div className="input-group">
          <input name="file" type="file" onChange={handleFileChange} />

          
          {file && 
            <input type="submit" value="Upload File"></input>
          }
        </div>
      </form>

      <div style={{margin:'auto'}}>
        {responseMessage && <p>{responseMessage}</p>}
      </div>
      {file ?  <fileContext.Provider value={creasableFile}><CreaseMaker /></fileContext.Provider> : ''}
    </div>
  );
};

export default CreaseLoader;


