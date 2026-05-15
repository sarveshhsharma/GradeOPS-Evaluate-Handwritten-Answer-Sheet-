import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import QuestionForm from '../components/QuestionForm';

export default function CreateExam() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // NEW: State to track which question is currently generating
  const [generatingIndex, setGeneratingIndex] = useState(null);

  // NEW: Added rubricMode to the default state ('manual' or 'auto')
  const [questions, setQuestions] = useState([
    { q_number: 1, question_text: '', max_marks: 5, correct_answer: '', rubricMode: 'manual' }
  ]);

  const handleAddQuestion = () => {
    setQuestions([
      ...questions, 
      { q_number: questions.length + 1, question_text: '', max_marks: 5, correct_answer: '', rubricMode: 'manual' }
    ]);
  };

  const handleRemoveQuestion = (index) => {
    const updated = questions.filter((_, i) => i !== index);
    // Re-adjust question numbers
    updated.forEach((q, i) => q.q_number = i + 1);
    setQuestions(updated);
  };

  const handleQuestionChange = (index, field, value) => {
    const updated = [...questions];
    updated[index][field] = value;
    setQuestions(updated);
  };

  // NEW: Function to handle the LLM generation request
  const handleGenerateRubric = async (index) => {
    const questionText = questions[index].question_text;
    if (!questionText.trim()) {
      alert("Please enter a question first before generating a rubric.");
      return;
    }

    setGeneratingIndex(index);
    try {
      const response = await apiClient.post('/exams/generate-rubric', {
        question_text: questionText
      });
      
      const updatedQuestions = [...questions];
      updatedQuestions[index].correct_answer = response.data.generated_rubric;
      // Switch back to manual mode so the professor can immediately edit the generated text
      updatedQuestions[index].rubricMode = 'manual'; 
      setQuestions(updatedQuestions);

    } catch (error) {
      console.error("Failed to generate rubric:", error);
      alert("Failed to generate rubric. Make sure the backend is running.");
    } finally {
      setGeneratingIndex(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const payload = {
        title,
        total_questions: questions.length,
        created_by: 1, // Hardcoded for MVP
        questions: questions
      };
      
      const response = await apiClient.post('/exams/', payload);
      // Navigate to the upload page with the new Exam ID
      navigate(`/upload/${response.data.id}`);
    } catch (error) {
      console.error("Failed to create exam", error);
      alert("Failed to create exam. Check console for details.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto pb-12">
        <div className="mb-8 border-b border-gray-300 pb-4">
        <h1 className="text-3xl font-bold text-black">Create New Exam</h1>
        <p className="text-gray-700 mt-2">Define your test parameters and strict rubrics for the AI pipeline.</p>
        </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
          <label className="block text-sm font-medium text-slate-700 mb-2">Exam Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-lg"
            placeholder="e.g., Midterm: Computational Biology"
            required
          />
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-bold text-black border-b pb-2">Rubric & Questions</h2>
          {questions.map((q, index) => (
            <QuestionForm
              key={index}
              index={index}
              question={q}
              onChange={handleQuestionChange}
              onRemove={questions.length > 1 ? handleRemoveQuestion : null}
              // NEW: Pass down the generating state and function
              generatingIndex={generatingIndex}
              onGenerateRubric={handleGenerateRubric}
            />
          ))}
        </div>

        <div className="flex items-center gap-4 pt-4">
          <button
            type="button"
            onClick={handleAddQuestion}
            className="px-6 py-2.5 bg-slate-100 text-slate-700 font-medium rounded-lg hover:bg-slate-200 transition-colors"
          >
            + Add Another Question
          </button>

          <div className="flex-grow"></div>

          <button
            type="submit"
            disabled={isSubmitting || !title.trim()}
            className={`px-8 py-2.5 text-white font-bold rounded-lg transition-colors shadow-sm
              ${isSubmitting ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {isSubmitting ? 'Saving Exam...' : 'Save & Proceed to Upload'}
          </button>
        </div>
      </form>
    </div>
  );
}