import React from 'react';

export default function ScoreCard({ status, aiTotal, finalTotal }) {
  const isReviewed = status === "REVIEWED";
  // The finalTotal is now our 60/40 weighted math from the backend. 
  const displayScore = isReviewed && finalTotal !== null ? finalTotal : finalTotal;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Exam Grading Results</h2>
        <div className="flex items-center gap-3 mt-2">
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium uppercase tracking-wider
            ${status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' : 
              status === 'GRADED' ? 'bg-blue-100 text-blue-800' : 
              'bg-green-100 text-green-800'}`}
          >
            {status}
          </span>
          {isReviewed && <span className="text-sm text-green-600 font-medium">✓ Human Reviewed</span>}
        </div>
      </div>

      <div className="md:text-right">
        <p className="text-sm font-semibold text-slate-500 uppercase tracking-wide">
          {isReviewed ? 'Override Final Score' : 'Weighted Final Score'}
        </p>
        <div className="flex flex-col md:items-end">
          <p className="text-4xl font-bold text-blue-700 mt-1">
            {displayScore?.toFixed(1) || "0.0"} 
          </p>
          {!isReviewed && (
            <p className="text-xs text-slate-400 mt-1 max-w-[200px] leading-tight">
              *Calculated via 60% Rubric Vector Match and 40% AI Semantic Evaluation.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}