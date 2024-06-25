import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import ClipLoader from 'react-spinners/ClipLoader';
import { FaCheckCircle, FaTimesCircle } from 'react-icons/fa';
import './VideoUpload.css';

const VideoUpload = () => {
  // Define States
  const [selectedFile, setSelectedFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [annotations, setAnnotations] = useState([]);
  const [mediaType, setMediaType] = useState(null);
  const canvasRef = useRef(null);

  // Function to Handle File Change
  const handleFileChange =  (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setSelectedFile(file);
    setResponse(null);
    setAnnotations([]);
    setMediaType(null);
  };

  // Function to remove the selected file
  const handleRemoveFile = () => {
    setSelectedFile(null);  
    setResponse(null);
    setAnnotations([]);
    setMediaType(null);
    setResponse(null)
  };

  // Function to upload the file to the backend and return the response
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
      setAnnotations(res.data.annotations);
      setMediaType(res.data.media_type);
    } catch (error) {
      console.error('Error uploading file:', error);
      if (error.response) {
        setResponse({ error: error.response.data.error });
      } else {
        setResponse({ error: 'An unexpected error occurred' });
      }
    }
    setLoading(false);
  };


  // Function to draw the annotations on the image (no annotation are displayed on videos)
  const drawAnnotations = useCallback((fileUrl) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const image = new Image();
    image.onload = () => {
      const scaleX = canvas.width / image.width;
      const scaleY = canvas.height / image.height;
      const scale = Math.min(scaleX, scaleY);
      const xOffset = (canvas.width - image.width * scale) / 2;
      const yOffset = (canvas.height - image.height * scale) / 2;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(image, xOffset, yOffset, image.width * scale, image.height * scale);

      annotations.forEach(annotation => {
        const { xmin, ymin, xmax, ymax, class_label } = annotation;
        ctx.beginPath();
        ctx.strokeStyle = 'blue';
        ctx.lineWidth = 4;
        ctx.rect(
          xOffset + xmin * scale,
          yOffset + ymin * scale,
          (xmax - xmin) * scale,
          (ymax - ymin) * scale
        );
        ctx.stroke();
        ctx.fillStyle = 'blue';
        ctx.font = '25px arial'
        ctx.fillText(class_label, xOffset + xmin * scale, yOffset + ymin * scale - 5);
      });
    };
    image.src = fileUrl;
  }, [annotations]);

  useEffect(() => {
    if (selectedFile && mediaType === 'image') {
      drawAnnotations(URL.createObjectURL(selectedFile));
    }
  }, [annotations, selectedFile, mediaType, drawAnnotations]);

  // Render
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
            <div style={{ position: 'relative', width: '750px', height: 'auto', margin: '0 auto' }}>
              <img
                src={URL.createObjectURL(selectedFile)}
                alt="selected_file"
                className="selected-file-media"
                style={{ width: '100%', height: '100%' }}
              />
              <canvas
                ref={canvasRef}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                }}
                width="750"
                height="auto"
              />
            </div>
          ) : (
            <div>
              <video
                controls
                className="selected-file-media"
                style={{ width: '750px', height: 'auto' }}
                src={URL.createObjectURL(selectedFile)}
              />
            </div>
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
      {response && response.text && (
        <h3 className="converted-text" style={{ margin: '10px' }}>Converted Text: {response.text}</h3>
      )}
      {response && response.error && (
        <div className="error-container">
          <FaTimesCircle color="red" size={50} />
          <p>We apologize, but an error occurred:</p>
          <p>{response.error}</p>
        </div>
      )}
      {mediaType === 'image' && annotations && (
        <div className="annotated-image-container">
          <h2>Annotated Image :</h2>
          <canvas id="annotatedCanvas" ref={canvasRef} width="800" height="400" />
        </div>
      )}
    </div>
  );
};

export default VideoUpload;
