import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const [showRedirect, setShowRedirect] = useState(false);
  const [countdown, setCountdown] = useState(5);

  // Superset database view URL
  const SUPERSET_DATABASE_URL = "http://127.0.0.1:8088/databaseview/list/?pageIndex=0&sortColumn=changed_on_delta_humanized&sortOrder=desc";

  // Countdown effect for Superset redirection
  useEffect(() => {
    let timer;
    if (showRedirect && countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    } else if (showRedirect && countdown === 0) {
      window.open(SUPERSET_DATABASE_URL, '_blank');
      setShowRedirect(false);
    }
    return () => clearTimeout(timer);
  }, [showRedirect, countdown, SUPERSET_DATABASE_URL]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage(null);
    setError(null);
    setShowRedirect(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setMessage(null);
    setError(null);
    setShowRedirect(false);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Something went wrong');
      }

      setMessage(data.message);
      setFile(null);
      // Reset the file input
      e.target.reset();
      
      // Start countdown to redirect to Superset
      setShowRedirect(true);
      setCountdown(5);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleManualRedirect = () => {
    window.open(SUPERSET_DATABASE_URL, '_blank');
  };

  return (
    <div className="app-container">
      <header>
        <h1>CSV Upload and Processing</h1>
        <p>Upload your CSV file to process and visualize in Superset</p>
      </header>

      <main>
        <form onSubmit={handleSubmit}>
          <div className="file-upload">
            <label htmlFor="file-input">
              {file ? file.name : 'Choose CSV file'}
            </label>
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="file-input"
            />
            {file && (
              <div className="file-info">
                <p>Selected file: {file.name}</p>
                <p>Size: {(file.size / 1024).toFixed(2)} KB</p>
              </div>
            )}
          </div>

          <button
            type="submit"
            className="upload-button"
            disabled={isUploading || !file}
          >
            {isUploading ? 'Processing...' : 'Upload and Process'}
          </button>
        </form>

        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}
        
        {showRedirect && (
          <div className="redirect-message">
            <p>Superset integration complete! Redirecting to Superset database page in {countdown} seconds...</p>
            <button onClick={handleManualRedirect} className="redirect-button">
              Go to Superset Now
            </button>
          </div>
        )}

        {/* <div className="pipeline-steps">
          <h2>Processing Pipeline</h2>
          <ol>
            <li>Upload CSV file</li>
            <li>Store data in MongoDB</li>
            <li>Process data</li>
            <li>Store in PostgreSQL</li>
            <li>Create Superset database connection</li>
          </ol>
        </div> */}
      </main>

      <footer>
        <p>Access your visualizations at <a href="http://127.0.0.1:8088/" target="_blank" rel="noopener noreferrer">Superset Dashboard</a></p>
      </footer>
    </div>
  );
}

export default App;