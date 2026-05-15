import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../api/client';
import ScoreCard from '../components/ScoreCard';
import AnswerBreakdown from '../components/AnswerBreakdown';

export default function Results() {
  const { submissionId } = useParams();
  
  const [submission, setSubmission] = useState(null);
  const [grades, setGrades] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch the data on component mount and set up polling
  useEffect(() => {
    let timeoutId;

    const fetchData = async () => {
      try {
        const subRes = await apiClient.get(`/submissions/${submissionId}`);
        setSubmission(subRes.data);

        // If grading is finished, fetch the grades and stop polling
        if (subRes.data.status !== 'PENDING') {
          const gradesRes = await apiClient.get(`/grading/${submissionId}/grades`);
          // Sort by question number to keep it organized
          const sortedGrades = gradesRes.data.sort((a, b) => a.question.q_number - b.question.q_number);
          setGrades(sortedGrades);
        } else {
          // If still PENDING, automatically check again in 5 seconds
          timeoutId = setTimeout(fetchData, 5000);
        }
      } catch (err) {
        console.error(err);
        setError("Failed to load grading data. The AI might still be processing.");
      } finally {
        // Only set loading to false if we actually have data or an error
        // so the screen doesn't flicker while polling
        setIsLoading(false); 
      }
    };

    fetchData();

    // Cleanup function to stop polling if the user leaves the page
    return () => clearTimeout(timeoutId);
  }, [submissionId]);

  const handleOverride = async (gradeId, newScore) => {
    try {
      const response = await apiClient.put(`/grading/override/${gradeId}`, { final_score: newScore });
      const updatedGrade = response.data;

      // Update local grades array so the UI reflects the change
      const updatedGrades = grades.map(g => g.id === gradeId ? updatedGrade : g);
      setGrades(updatedGrades);

      // Recalculate total score locally to update the ScoreCard immediately
      const newTotal = updatedGrades.reduce((sum, g) => sum + (g.final_score !== null ? g.final_score : g.ai_score), 0);
      setSubmission(prev => ({ 
        ...prev, 
        total_score: newTotal,
        status: 'REVIEWED' // Mark as human-reviewed
      }));

    } catch (err) {
      console.error("Failed to override grade", err);
      alert("Failed to save the override.");
    }
  };

  if (isLoading) {
    return <div className="text-center py-20 text-slate-500 font-medium animate-pulse">Loading grading dashboard...</div>;
  }

  if (error || !submission) {
    return (
      <div className="text-center py-20">
        <p className="text-red-500 font-medium mb-4">{error}</p>
        <button onClick={() => window.location.reload()} className="text-blue-600 underline">Refresh Page</button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div className="flex justify-between items-end mb-6 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Grading Dashboard</h1>
          <p className="text-slate-500 mt-1">Student: <span className="font-semibold text-slate-700">{submission.student_id}</span></p>
        </div>
        <Link to={`/upload/${submission.exam_id}`} className="text-sm text-blue-600 hover:text-blue-800 font-medium">
          ← Upload another paper
        </Link>
      </div>

      {submission.status === 'PENDING' ? (
        <div className="bg-yellow-50 border border-yellow-200 p-8 text-center rounded-lg">
          <h2 className="text-xl font-bold text-yellow-800 mb-2">Processing...</h2>
          <p className="text-yellow-700">The AI is currently extracting and evaluating this answer sheet. This page will automatically update when finished.</p>
        </div>
      ) : (
        <>
          <div className="mb-8">
            <ScoreCard 
              status={submission.status} 
              aiTotal={grades.reduce((sum, g) => sum + g.ai_score, 0)} 
              finalTotal={submission.total_score} 
            />
          </div>

          <div className="space-y-6">
            <h2 className="text-xl font-bold text-slate-800">Answer Breakdown</h2>
            {grades.map(grade => (
              <AnswerBreakdown 
                key={grade.id} 
                grade={grade} 
                onOverride={handleOverride} 
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}