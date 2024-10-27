import { useState } from 'react';

const CreaseLoader = () => {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files) {
      console.log(e.target.files)
      setFile(e.target.files[0]);
    }
  };

  // const handleUpload = async () => {

  //   if (file) {
  //       console.log('Uploading file...');

  //       const formData = new FormData();
  //       console.log('f', file)
  //       formData.append('file', file);
  
  //       try {
  //         // You can write the URL of your server or any other endpoint used for file upload
  //         const result = await fetch('http://localhost:5000/data', {
  //           method: 'POST',
  //           body: formData,
  //           name: 'file'
  //         });
  
  //         const data = await result.json();
  
  //         console.log('d', data);
  //       } catch (error) {
  //         console.error(error);
  //       }
  //     }
  //   };

  console.log(file)

  return (
    <>
      <form action="http://localhost:5000/data" encType="multipart/form-data" method="post">
        <div className="input-group">
          <input name="file" type="file" onChange={handleFileChange} />

          {file && 
            <input type="submit" value="Upload File"></input>
          }
        </div>
      </form>



    </>
  );
};

export default CreaseLoader;