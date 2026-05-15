import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';

// We will build these exact pages in Step 7. 
// For now, these are basic placeholders so the router works immediately.
import CreateExam from './pages/CreateExam';
import UploadSheet from './pages/UploadSheet';
import Results from './pages/Results';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Simple Navigation Bar */}
      <nav className="bg-slate-900 text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <span className="font-bold text-xl tracking-wider uppercase">GradeOps</span>
            </div>
            <div className="flex space-x-4">
              <Link 
                to="/" 
                className="px-3 py-2 rounded-md text-sm font-medium hover:bg-slate-700 transition-colors"
              >
                1. Create Exam
              </Link>
              {/* In a real flow, you'd navigate here after creating an exam, passing the ID */}
              <Link 
                to="/upload/1" 
                className="px-3 py-2 rounded-md text-sm font-medium hover:bg-slate-700 transition-colors"
              >
                2. Upload Paper
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          {/* Professor creates the exam and rubric here */}
          <Route path="/" element={<CreateExam />} />
          
          {/* Professor uploads a student paper to a specific exam */}
          <Route path="/upload/:examId" element={<UploadSheet />} />
          
          {/* TA Dashboard to review AI grades for a specific submission */}
          <Route path="/results/:submissionId" element={<Results />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;