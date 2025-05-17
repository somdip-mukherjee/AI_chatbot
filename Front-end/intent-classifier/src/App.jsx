import React from 'react';
// Add your CSS file for styling
import FileUpload from './FileUpload';
import './App.css'
function App() {
  return (
    <div className="App">
      <h1 style={{textAlign:"center",color:"white"}}>Intent Classifier</h1>
      <FileUpload />
    </div>
  );
}

export default App;
