import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startSession } from '../services/api';

export default function PatientRegistration() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: '', age: '', gender: 'male',
    medical_history: '', chief_complaint: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await startSession({
        ...form,
        age: parseInt(form.age, 10),
      });
      localStorage.setItem('threadId', response.data.thread_id);
      localStorage.setItem('patientName', form.name);
      navigate('/consultation');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Patient Registration</h2>
        <p>Collect patient demographic and clinical intake information</p>
      </div>

      <div className="disclaimer">
        This system does not replace a professional medical consultation.
      </div>

      {error && <div className="alert alert-warning">{error}</div>}

      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Full Name *</label>
            <input id="name" name="name" value={form.name} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label htmlFor="age">Age *</label>
            <input id="age" name="age" type="number" min="0" max="150" value={form.age} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label htmlFor="gender">Gender *</label>
            <select id="gender" name="gender" value={form.gender} onChange={handleChange}>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="medical_history">Medical History</label>
            <textarea id="medical_history" name="medical_history" value={form.medical_history} onChange={handleChange} placeholder="Past conditions, allergies, surgeries..." />
          </div>
          <div className="form-group">
            <label htmlFor="chief_complaint">Chief Complaint *</label>
            <textarea id="chief_complaint" name="chief_complaint" value={form.chief_complaint} onChange={handleChange} required placeholder="Primary reason for consultation..." />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Registering...' : 'Register & Continue'}
          </button>
        </form>
      </div>
    </div>
  );
}
