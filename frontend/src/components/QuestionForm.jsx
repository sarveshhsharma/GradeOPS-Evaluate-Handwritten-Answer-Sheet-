import React from 'react';

export default function QuestionForm({ index, question, onChange, onRemove, generatingIndex, onGenerateRubric }) {
  
  // Helper to update the rubric mode state
  const handleModeChange = (mode) => {
    onChange(index, 'rubricMode', mode);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 relative">
      {/* Header & Remove Button */}
      <div className="flex justify-between items-center mb-4 border-b border-slate-100 pb-2">
        <h3 className="text-lg font-bold text-slate-800">Question {question.q_number}</h3>
        {onRemove && (
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="text-red-500 hover:text-red-700 text-sm font-medium transition-colors"
          >
            Remove Question
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Question Number</label>
          <input
            type="number"
            value={question.q_number}
            readOnly
            className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-500 cursor-not-allowed"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Max Marks</label>
          <input
            type="number"
            min="1"
            step="0.5"
            value={question.max_marks}
            onChange={(e) => onChange(index, 'max_marks', parseFloat(e.target.value) || 0)}
            className="w-full p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />
        </div>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-slate-700 mb-1">Question Text</label>
        <textarea
          value={question.question_text}
          onChange={(e) => onChange(index, 'question_text', e.target.value)}
          className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          rows="3"
          placeholder="Enter the exact test question here..."
          required
        />
      </div>

      {/* ========================================================= */}
      {/* NEW: Rubric Mode Toggle & Generation Area                   */}
      {/* ========================================================= */}
      <div className="mt-6 flex flex-col sm:flex-row sm:items-end justify-between mb-2 gap-3">
        <label className="block text-sm font-medium text-slate-700">Strict Rubric / Correct Answer</label>
        
        {/* Segmented Control for Mode */}
        <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200 w-fit">
          <button
            type="button"
            onClick={() => handleModeChange('manual')}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200 ${
              question.rubricMode !== 'auto' ? 'bg-white shadow-sm text-blue-700 font-bold' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            Write Yourself
          </button>
          <button
            type="button"
            onClick={() => handleModeChange('auto')}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all duration-200 flex items-center gap-1 ${
              question.rubricMode === 'auto' ? 'bg-white shadow-sm text-purple-700 font-bold' : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            ✨ Generate
          </button>
        </div>
      </div>

      {/* Auto-Generate Action Banner */}
      {question.rubricMode === 'auto' && (
        <div className="mb-3 bg-purple-50 border border-purple-100 rounded-lg p-4 flex flex-col sm:flex-row items-center justify-between gap-4 transition-all">
          <p className="text-sm text-purple-800">
            The AI will draft a rubric based on the Question Text above.
          </p>
          <button
            type="button"
            onClick={() => onGenerateRubric(index)}
            disabled={generatingIndex === index || !question.question_text.trim()}
            className={`whitespace-nowrap px-4 py-2 rounded-lg text-sm font-bold text-white transition-colors ${
              generatingIndex === index || !question.question_text.trim()
                ? 'bg-purple-300 cursor-not-allowed' 
                : 'bg-purple-600 hover:bg-purple-700 shadow-sm'
            }`}
          >
            {generatingIndex === index ? 'Generating...' : 'Generate AI Rubric'}
          </button>
        </div>
      )}

      {/* The Editable Text Area */}
      <textarea
        value={question.correct_answer}
        onChange={(e) => onChange(index, 'correct_answer', e.target.value)}
        className={`w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-slate-800 transition-colors ${
          question.rubricMode === 'auto' && !question.correct_answer ? 'bg-slate-50 border-slate-200' : 'bg-white border-slate-300'
        }`}
        rows="4"
        placeholder={question.rubricMode === 'auto' ? "Click 'Generate AI Rubric' to let the model draft the answer..." : "State exactly what the student needs to write to get full marks..."}
        required
      />
    </div>
  );
}