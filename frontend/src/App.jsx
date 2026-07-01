import { Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import PatientRegistration from './pages/PatientRegistration';
import Consultation from './pages/Consultation';
import Questionnaire from './pages/Questionnaire';
import PhysicianReview from './pages/PhysicianReview';
import ConsultationHistory from './pages/ConsultationHistory';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

const DISCLAIMER = 'This system does not replace a professional medical consultation.';

function App() {
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <h1>MediGraph AI</h1>
        <p className="subtitle">Clinical Orientation System</p>
        <nav>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/register">Patient Registration</NavLink>
          <NavLink to="/consultation">Consultation</NavLink>
          <NavLink to="/questionnaire">Questionnaire</NavLink>
          <NavLink to="/physician">Physician Review</NavLink>
          <NavLink to="/history">Consultation History</NavLink>
          <NavLink to="/reports">Reports</NavLink>
          <NavLink to="/settings">Settings</NavLink>
        </nav>
        <div className="disclaimer" style={{ marginTop: '2rem', fontSize: '0.7rem' }}>
          {DISCLAIMER}
        </div>
      </aside>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/register" element={<PatientRegistration />} />
          <Route path="/consultation" element={<Consultation />} />
          <Route path="/questionnaire" element={<Questionnaire />} />
          <Route path="/physician" element={<PhysicianReview />} />
          <Route path="/history" element={<ConsultationHistory />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
