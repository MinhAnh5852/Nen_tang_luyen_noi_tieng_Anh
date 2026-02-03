import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import PublicHeader from './components/PublicHeader'; 
import Footer from './components/Footer';
import LandingPage from './pages/Home/LandingPage';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import Dashboard from './pages/Learner/Dashboard';
import Practice from './pages/Learner/Practice';
import Progress from './pages/Learner/Progress';
import Profile from './pages/Learner/Profile';
import Subscription from './pages/Learner/Subscription';
import Assessment from './pages/Learner/Assessment';
import Leaderboard from './pages/Learner/Leaderboard';

import './index.css';

function App() {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('user_role')?.toLowerCase(); 
  const isAuthenticated = !!token;

  const PublicLayout = ({ children }: { children: React.ReactNode }) => (
    <div className="app-viewport">
      <PublicHeader />
      <main className="main-content"> 
        {children}
      </main>
      <Footer />
    </div>
  );

  const ProtectedLayout = () => {
    if (!isAuthenticated) return <Navigate to="/login" />;

    // Chuyển hướng cho Admin/Mentor theo yêu cầu hệ thống AESP
    if (userRole === 'admin') {
      window.location.href = '/admin/index.html';
      return null;
    }
    if (userRole === 'mentor') {
      window.location.href = '/mentor/mentor.html';
      return null;
    }

    return (
      <div className="app-viewport protected-bg">
        <Header />
        <main className="main-content">
          <div className="container">
            <Routes>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/practice" element={<Practice />} />
              <Route path="/progress" element={<Progress />} />
              <Route path="/subscription" element={<Subscription />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/assessment" element={<Assessment />} />
              <Route path="/leaderboard" element={<Leaderboard />} />
              <Route path="*" element={<Navigate to="/dashboard" />} />
            </Routes>
          </div>
        </main>
        <Footer />
      </div>
    );
  };

  return (
    <Router>
      <Routes>
        <Route path="/" element={<PublicLayout><LandingPage /></PublicLayout>} />
        <Route path="/login" element={<PublicLayout><Login /></PublicLayout>} />
        <Route path="/register" element={<PublicLayout><Register /></PublicLayout>} />
        <Route path="/*" element={<ProtectedLayout />} />
      </Routes>
    </Router>
  );
}

export default App;