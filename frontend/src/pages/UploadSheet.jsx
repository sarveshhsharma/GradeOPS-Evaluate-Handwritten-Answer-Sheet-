import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import apiClient from '../api/client';
import UploadBox from '../components/UploadBox';

export default function UploadSheet() {
  const { examId } = useParams();
  const navigate = useNavigate();
  
  const [studentId, setStudentId] = useState('');
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [submissionId, setSubmissionId] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !studentId) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('student_id', studentId);
      formData.append('file', file);

      // Post to the backend upload route
      const response = await apiClient.post(`/submissions/${examId}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setSubmissionId(response.data.submission_id);
    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to upload the file.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto pt-10">
      <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
        <h1 className="text-2xl font-bold text-black mb-2">Upload Student Answer Sheet</h1>
        <p className="text-gray-700 mb-8">
          Exam ID: <span className="font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-700">{examId}</span>
        </p>

        {submissionId ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-green-100 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
            </div>
            <h2 className="text-xl font-bold text-slate-800 mb-2">Upload Successful!</h2>
            <p className="text-slate-600 mb-6">The AI pipeline is currently grading the paper in the background.</p>
            <Link 
              to={`/results/${submissionId}`}
              className="inline-block bg-blue-600 text-white font-semibold px-6 py-2.5 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Go to Grading Dashboard
            </Link>
          </div>
        ) : (
          <form onSubmit={handleUpload} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Student ID / Roll Number</label>
              {/* FIXED: Restored to type="text" */}
              <input
                type="text"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="e.g., BT23001"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Scanned Answer Sheet (PDF, JPG, PNG)</label>
              <UploadBox onFileSelect={setFile} selectedFile={file} />
            </div>

            <button
              type="submit"
              disabled={isUploading || !file || !studentId.trim()}
              className={`w-full py-3 font-bold rounded-lg text-white transition-colors shadow-sm
                ${(isUploading || !file || !studentId) ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
            >
              {isUploading ? 'Uploading & Processing...' : 'Upload & Start Grading'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}