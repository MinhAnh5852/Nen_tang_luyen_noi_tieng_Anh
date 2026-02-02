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

import './index.css';

function App() {
  const token = localStorage.getItem('token');
  const userRole = localStorage.getItem('user_role')?.toLowerCase(); // Lấy role từ localStorage
  const isAuthenticated = !!token;

  // Helper để hiển thị trang công khai
  const PublicLayout = ({ children }: { children: React.ReactNode }) => (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <PublicHeader />
      <main style={{ flex: '1 0 auto', marginTop: '80px' }}> 
        {children}
      </main>
      <Footer />
    </div>
  );

  return (
    <Router>
      <Routes>
        {/* --- NHÓM 1: CÁC TRANG CÔNG KHAI --- */}
        <Route path="/" element={<PublicLayout><LandingPage /></PublicLayout>} />
        <Route path="/login" element={<PublicLayout><Login /></PublicLayout>} />
        <Route path="/register" element={<PublicLayout><Register /></PublicLayout>} />

        {/* --- NHÓM 2: CÁC TRANG NỘI BỘ (Yêu cầu đăng nhập) --- */}
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              // KIỂM TRA ROLE ĐỂ ĐIỀU HƯỚNG RA NGOÀI REACT NẾU CẦN
              userRole === 'admin' ? (
                /* Admin sẽ thoát khỏi app React để vào trang HTML tĩnh */
                <script>{window.location.href = '/admin/index.html'}</script>
              ) : userRole === 'mentor' ? (
                /* Mentor sẽ thoát khỏi app React để vào trang HTML tĩnh */
                <script>{window.location.href = '/mentor/mentor.html'}</script>
              ) : (
                /* Chỉ Học viên (Learner) mới ở lại app React này */
                <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: '#f1f5f9' }}>
                  <Header />
                  <main style={{ flex: '1 0 auto', marginTop: '100px', paddingBottom: '50px' }}>
                    <div className="container">
                      <Routes>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/practice" element={<Practice />} />
                        <Route path="/progress" element={<Progress />} />
                        <Route path="/subscription" element={<Subscription />} />
                        <Route path="/profile" element={<Profile />} />
                        <Route path="*" element={<Navigate to="/dashboard" />} />
                      </Routes>
                    </div>
                  </main>
                  <Footer />
                </div>
              )
            ) : (
              <Navigate to="/login" />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;