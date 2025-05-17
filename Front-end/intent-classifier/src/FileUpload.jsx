import { useState } from 'react';

function FileUpload() {
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');

  const handleFileUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    setLoading(true);
    setDownloadUrl('');

    try {
      const res = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Upload failed');

      const data = await res.json();
      setDownloadUrl(`http://localhost:5000/downloads/${data.filename}`);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-wrapper">
      {loading && (
        <div className="overlay">
          <div className="overlay-text">Processing files, please wait...</div>
        </div>
      )}

      <div className={`container ${loading ? 'blurred' : ''}`}>
        <form onSubmit={handleFileUpload}>
          <label htmlFor="SEQ"><h4>Enter Seq File</h4></label>
          <input type="file" name="file1" accept=".txt" required />

          <label htmlFor="label"><h4>Enter Label File</h4></label>
          <input type="file" name="file2" accept=".txt" required />

          <button type="submit" disabled={loading}>
            {loading ? 'Processing...' : 'Upload'}
          </button>
        </form>

        {downloadUrl && (
          <a className="download-btn" href={downloadUrl} download>
            Download Result
          </a>
        )}
      </div>
    </div>
  );
}

export default FileUpload;
