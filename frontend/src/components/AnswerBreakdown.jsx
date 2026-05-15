import React, { useState } from 'react';

export default function AnswerBreakdown({ grade, onOverride }) {
  // Default to final_score (the weighted math) if it exists, otherwise fallback to ai_score
  const [overrideScore, setOverrideScore] = useState(grade.final_score !== null ? grade.final_score : grade.ai_score);
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    await onOverride(grade.id, overrideScore);
    setIsSaving(false);
  };

  const displayScore = grade.final_score !== null ? grade.final_score : grade.ai_score;

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      {/* Header */}
      <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
        <h3 className="text-lg font-bold text-slate-800">Question {grade.question?.q_number}</h3>
        <span className="text-sm font-medium text-slate-500">Max Marks: {grade.question?.max_marks}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 p-6 gap-8">
        {/* Left Side: Student Answer & Rubric */}
        <div>
          <h4 className="text-sm font-semibold text-slate-500 uppercase mb-3">Student's Extracted Answer</h4>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 font-mono text-sm text-slate-800 whitespace-pre-wrap min-h-[120px]">
            {grade.extracted_text || <span className="text-slate-400 italic">No answer detected.</span>}
          </div>
          
          <h4 className="text-sm font-semibold text-slate-500 uppercase mt-4 mb-2">Rubric / Expected Answer</h4>
          <div className="bg-green-50 border border-green-100 rounded-lg p-3 text-sm text-green-800">
            {grade.question?.correct_answer || "No rubric provided."}
          </div>
        </div>

        {/* Right Side: AI Reasoning & Weighted Score Breakdown */}
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <h4 className="text-sm font-semibold text-blue-600 uppercase mr-2">AI Evaluation</h4>
            
            {/* Breakdown Badges */}
            <span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-xs border border-slate-200">
              AI Base (40%): {grade.ai_score}
            </span>
            
            {grade.rubric_similarity !== null && (
               <span className="bg-purple-50 text-purple-700 px-2 py-0.5 rounded text-xs border border-purple-200">
                 Rubric Match (60%): {grade.rubric_similarity}%
               </span>
            )}
            
            <span className="bg-blue-100 text-blue-800 px-3 py-0.5 rounded text-xs font-bold border border-blue-200 shadow-sm">
              Final Weighted: {displayScore} / {grade.question?.max_marks}
            </span>
          </div>

          <p className="text-sm font-medium text-slate-700 mb-1">Justification:</p>
          <div className="bg-slate-50 rounded-lg p-3 text-sm text-slate-700 mb-4">
            {grade.ai_justification}
          </div>

          <p className="text-sm font-medium text-slate-700 mb-1">Deductions:</p>
          <div className="bg-red-50 rounded-lg p-3 text-sm text-red-800">
            {grade.deduction_reasons !== "None" ? grade.deduction_reasons : "No deductions."}
          </div>
        </div>
      </div>

      {/* Footer: TA Override */}
      <div className="bg-slate-50 px-6 py-4 border-t border-slate-200 flex justify-end items-center gap-4">
        <label className="text-sm font-semibold text-slate-700">TA Override Score:</label>
        <input 
          type="number" 
          step="0.1"
          min="0"
          max={grade.question?.max_marks}
          value={overrideScore}
          onChange={(e) => setOverrideScore(parseFloat(e.target.value) || 0)}
          className="w-20 p-2 border border-slate-300 rounded text-center font-bold focus:ring-2 focus:ring-blue-500 outline-none"
        />
        <span className="text-slate-500 text-sm">/ {grade.question?.max_marks}</span>
        <button 
          onClick={handleSave}
          disabled={isSaving}
          className={`px-4 py-2 rounded font-medium text-sm transition-colors ${
            isSaving ? 'bg-slate-300 text-slate-500 cursor-not-allowed' : 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200'
          }`}
        >
          {isSaving ? 'Saving...' : 'Save Override'}
        </button>
      </div>
    </div>
  );
}