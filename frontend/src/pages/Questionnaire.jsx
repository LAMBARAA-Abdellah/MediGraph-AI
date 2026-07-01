import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getConsultation, submitAnswer } from '../services/api';

export default function Questionnaire() {
  const navigate = useNavigate();
  const threadId = localStorage.getItem('threadId') || '';
  const [consultation, setConsultation] = useState(null);
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    if (!threadId) return;
    try {
      const response = await getConsultation(threadId);
      setConsultation(response.data);
      if (response.data.consultation_status === 'awaiting_physician_review') {
        navigate('/physician');
      }
      if (response.data.consultation_status === 'completed') {
        navigate('/reports');
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => { fetchStatus(); }, [threadId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!answer.trim()) return;
    setLoading(true);
    try {
      const response = await submitAnswer(threadId, answer);
      setConsultation(response.data);
      setAnswer('');
      if (response.data.consultation_status === 'awaiting_physician_review') {
        navigate('/physician');
      }
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit answer');
    } finally {
      setLoading(false);
    }
  };

  const questionCount = consultation?.question_count || 0;
  const progress = (questionCount / 5) * 100;

  return (
    <div>
      <div className="page-header">
        <h2>Diagnostic Questionnaire</h2>
        <p>Answer 5 sequential questions from the Diagnostic Agent</p>
      </div>

      {!threadId && (
        <div className="alert alert-warning">No active session. Please register a patient first.</div>
      )}

      {consultation && (
        <>
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Progress: Question {questionCount} of 5</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
          </div>

          {consultation.current_question && consultation.consultation_status === 'questionnaire_in_progress' && (
            <div className="card">
              <h3>Question {questionCount}</h3>
              <p style={{ fontSize: '1.2rem', margin: '1rem 0' }}>{consultation.current_question}</p>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label>Your Answer</label>
                  <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} required placeholder="Type your answer here..." />
                </div>
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Submitting...' : 'Submit Answer'}
                </button>
              </form>
            </div>
          )}

          {consultation.patient_answers?.length > 0 && (
            <div className="card">
              <h3>Previous Answers</h3>
              {consultation.patient_answers.map((qa, i) => (
                <div key={i} className="qa-item">
                  <strong>Q{qa.question_number}: {qa.question}</strong>
                  <p>{qa.answer}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
