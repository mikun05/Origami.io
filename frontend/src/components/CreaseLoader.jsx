import { useState } from 'react';

const CreaseLoader = () => {
  const [file, setFile] = useState(null);
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
    } catch (error) {
      setResponseMessage('Error uploading file.');
      console.error('Error:', error);
    }
  };


  console.log(file)

  return (
    <>
      <form onSubmit={handleSubmit} encType="multipart/form-data">
        <div className="input-group">
          <input name="file" type="file" onChange={handleFileChange} />

          {file && 
            <input type="submit" value="Upload File"></input>
          }
        </div>
      </form>


      {responseMessage && <p>{responseMessage}</p>}
    </>
  );
};

export default CreaseLoader;


