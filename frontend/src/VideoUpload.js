import React, { useState } from 'react';
import axios from 'axios';
import ClipLoader from 'react-spinners/ClipLoader';
import { FaCheckCircle, FaTimesCircle } from 'react-icons/fa';
import './VideoUpload.css';

const VideoUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setResponse(null);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setResponse(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('media', selectedFile);

    setLoading(true);

    try {
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      };

      const res = await axios.post('http://localhost:8000/backend/upload/', formData, config);

      setResponse(res.data);
    } catch (error) {
      console.error('Error uploading file:', error);
      if (error.response) {
        setResponse({ error: error.response.data });
      } else {
        setResponse({ error: 'An unexpected error occurred' });
      }
    }
    setLoading(false);
  };

  return (
    <div className="upload-container">
      <h1>Sign Language Converter</h1>
      <div className="input-container">
        <input
          type="file"
          accept="video/*,image/*"
          id="file-input"
          onChange={handleFileChange}
        />
        <label htmlFor="file-input" className="input-label">
          Choose Media
        </label>
      </div>
      <button onClick={handleUpload} disabled={loading}>
        Upload Media
      </button>
      {selectedFile && (
        <div className="selected-file-display-container">
          <p>Selected file: {selectedFile.name}</p>
          {selectedFile.type.startsWith('image') ? (
            <img src={URL.createObjectURL(selectedFile)} alt="selected_file" className="selected-file-media" />
          ) : (
            <video controls className="selected-file-media">
              <source src={URL.createObjectURL(selectedFile)} type={selectedFile.type} />
            </video>
          )}
          <button onClick={handleRemoveFile} disabled={loading} id="remove-file">
            Remove File
          </button>
        </div>
      )}
      <div>
        <ClipLoader loading={loading} color="black" size={100} speedMultiplier={1} />
      </div>
      {response && response.message && <FaCheckCircle color="green" size={50} />}
      {response && response.error && (
        <div className="error-container">
          <FaTimesCircle color="red" size={50} />
          <p>We apologize, but an error occurred:</p>
          <p>{response.error}</p>
        </div>
      )}
      <div className="processed-media-container">
        {response && response.text && (
          <h3 className="converted-text">Converted Text: {response.text}</h3>
        )}
      </div>
    </div>
  );
};

export default VideoUpload;