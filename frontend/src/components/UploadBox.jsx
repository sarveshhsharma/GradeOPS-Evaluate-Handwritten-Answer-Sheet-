import React, { useRef } from 'react';

export default function UploadBox({ onFileSelect, selectedFile }) {
  const fileInputRef = useRef(null);

  const validateAndSetFile = (file) => {
    if (file) {
      const allowedTypes = [
        "application/pdf", 
        "image/jpeg", 
        "image/jpg", 
        "image/png"
      ];
      
      if (allowedTypes.includes(file.type)) {
        onFileSelect(file);
      } else {
        alert("Please upload a PDF, JPG, or PNG file.");
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    validateAndSetFile(e.dataTransfer.files[0]);
  };

  const handleChange = (e) => {
    validateAndSetFile(e.target.files[0]);
  };

  return (
    <div 
      className="border-2 border-dashed border-slate-300 bg-slate-50 p-10 rounded-xl text-center cursor-pointer hover:bg-slate-100 transition-colors"
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current.click()}
    >
      <input 
        type="file" 
        className="hidden" 
        ref={fileInputRef} 
        accept=".pdf, .jpg, .jpeg, .png" 
        onChange={handleChange} 
      />
      
      {selectedFile ? (
        <div>
          <p className="text-lg font-medium text-blue-600">{selectedFile.name}</p>
          <p className="text-sm text-slate-500 mt-1">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
        </div>
      ) : (
        <div>
          <svg className="w-12 h-12 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
          </svg>
          <p className="text-base font-bold text-black">Click to upload or drag and drop</p>
          <p className="text-sm text-slate-500 mt-2">PDF, JPG, or PNG (Max 10MB)</p>
        </div>
      )}
    </div>
  );
}