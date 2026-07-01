import { useState } from 'react';

export default function Settings() {
  const [apiUrl, setApiUrl] = useState(localStorage.getItem('apiUrl') || 'http://localhost:8000');

  const handleSave = () => {
    localStorage.setItem('apiUrl', apiUrl);
    alert('Settings saved. Restart the app to apply API URL changes.');
  };

  return (
    <div>
      <div className="page-header">
        <h2>Settings</h2>
        <p>Configure MediGraph AI application settings</p>
      </div>

      <div className="card">
        <div className="form-group">
          <label>API Base URL</label>
          <input value={apiUrl} onChange={(e) => setApiUrl(e.target.value)} />
        </div>
        <button className="btn btn-primary" onClick={handleSave}>Save Settings</button>
      </div>

      <div className="card">
        <h3>About MediGraph AI</h3>
        <p>Version: 1.0.0</p>
        <p>Technologies: LangGraph, LangChain, FastAPI, MCP, React</p>
        <p>Python: 3.12</p>
        <div className="disclaimer" style={{ marginTop: '1rem' }}>
          This system does not replace a professional medical consultation.
          This is an educational project for academic purposes only.
        </div>
      </div>
    </div>
  );
}
