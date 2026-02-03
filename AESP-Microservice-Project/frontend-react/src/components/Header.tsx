import React, { useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("Học viên");

  useEffect(() => {
    // Lấy thông tin từ user_info (Object) thay vì username (String) lẻ để đồng bộ dữ liệu thật
    const userInfoStr = localStorage.getItem('user_info');
    if (userInfoStr) {
      try {
        const userInfo = JSON.parse(userInfoStr);
        if (userInfo && userInfo.username) {
          setUsername(userInfo.username);
        }
      } catch (error) {
        console.error("Lỗi parse user_info trong Header:", error);
      }
    }
  }, []);

  const handleLogout = () => {
    if (window.confirm("Bạn có chắc muốn đăng xuất?")) {
      // Xóa toàn bộ session để bảo mật thông tin
      localStorage.clear();
      navigate('/login');
    }
  };

  return (
    <header className="main-header">
      <div className="container header-content">
        {/* Logo - Click để về Dashboard */}
        <div className="logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
          <i className="fas fa-robot logo-icon"></i>
          <span className="logo-text">AESP</span>
        </div>

        {/* Thanh điều hướng chính cho Learner */}
        <nav className="nav-links">
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? "active" : ""}>Bảng điều khiển</NavLink>
          <NavLink to="/practice" className={({ isActive }) => isActive ? "active" : ""}>Luyện tập AI</NavLink>
          
          {/* MỚI: Liên kết Bảng xếp hạng để học viên thi đua */}
          <NavLink to="/leaderboard" className={({ isActive }) => isActive ? "active" : ""}>Bảng xếp hạng</NavLink>
          
          <NavLink to="/progress" className={({ isActive }) => isActive ? "active" : ""}>Tiến độ</NavLink>
          <NavLink to="/subscription" className={({ isActive }) => isActive ? "active" : ""}>Gói dịch vụ</NavLink>
          <NavLink to="/profile" className={({ isActive }) => isActive ? "active" : ""}>Hồ sơ</NavLink>
        </nav>

        {/* Menu người dùng bên phải */}
        <div className="user-menu">
          <div className="user-info">
            <div className="user-avatar">
              {username.charAt(0).toUpperCase()}
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