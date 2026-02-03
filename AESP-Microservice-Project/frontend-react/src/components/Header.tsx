import React, { useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("Học viên");

  const loadUserInfo = () => {
    const userInfoStr = localStorage.getItem('user_info');
    if (userInfoStr) {
      try {
        const userInfo = JSON.parse(userInfoStr);
        if (userInfo && userInfo.username) {
          setUsername(userInfo.username);
        }
      } catch (error) {
        console.error("Lỗi parse user_info:", error);
      }
    }
  };

  useEffect(() => {
    loadUserInfo();
    // Lắng nghe sự kiện nếu trang Profile cập nhật lại tên
    window.addEventListener('storage', loadUserInfo);
    return () => window.removeEventListener('storage', loadUserInfo);
  }, []);

  const handleLogout = () => {
    if (window.confirm("Bạn có chắc muốn đăng xuất khỏi AESP?")) {
      localStorage.clear();
      navigate('/login');
    }
  };

  return (
    <header className="main-header">
      <div className="container header-content">
        <div className="logo" onClick={() => navigate('/dashboard')}>
          <i className="fas fa-robot logo-icon"></i>
          <span className="logo-text">AESP</span>
        </div>

        <nav className="nav-links">
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? "active" : ""}>Bảng điều khiển</NavLink>
          <NavLink to="/practice" className={({ isActive }) => isActive ? "active" : ""}>Luyện tập AI</NavLink>
          <NavLink to="/leaderboard" className={({ isActive }) => isActive ? "active" : ""}>Bảng xếp hạng</NavLink>
          <NavLink to="/progress" className={({ isActive }) => isActive ? "active" : ""}>Tiến độ</NavLink>
          <NavLink to="/subscription" className={({ isActive }) => isActive ? "active" : ""}>Gói dịch vụ</NavLink>
          <NavLink to="/profile" className={({ isActive }) => isActive ? "active" : ""}>Hồ sơ</NavLink>
        </nav>

        <div className="user-menu">
          <div className="user-info">
            <div className="user-avatar">
              {username ? username.charAt(0).toUpperCase() : "H"}
            </div>
            <span className="user-name">{username}</span>
          </div>
          <button onClick={handleLogout} className="btn-logout">
            <i className="fas fa-sign-out-alt"></i> Đăng xuất
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;