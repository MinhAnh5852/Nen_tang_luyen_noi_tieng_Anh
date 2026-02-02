import React, { useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("Học viên");

  useEffect(() => {
    // SỬA LỖI TẠI ĐÂY: Lấy từ user_info thay vì username lẻ
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
      localStorage.clear();
      navigate('/login');
    }
  };

  return (
    <header className="main-header">
      <div className="container header-content">
        {/* Logo */}
        <div className="logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
          <i className="fas fa-robot logo-icon"></i>
          <span className="logo-text">AESP</span>
        </div>

        {/* Thanh điều hướng */}
        <nav className="nav-links">
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? "active" : ""}>Bảng điều khiển</NavLink>
          <NavLink to="/practice" className={({ isActive }) => isActive ? "active" : ""}>Luyện tập AI</NavLink>
          <NavLink to="/progress" className={({ isActive }) => isActive ? "active" : ""}>Tiến độ</NavLink>
          <NavLink to="/subscription" className={({ isActive }) => isActive ? "active" : ""}>Gói dịch vụ</NavLink>
          <NavLink to="/profile" className={({ isActive }) => isActive ? "active" : ""}>Hồ sơ</NavLink>
        </nav>

        {/* Menu người dùng */}
        <div className="user-menu">
          <div className="user-info">
            <div className="user-avatar">
              {username.charAt(0).toUpperCase()}
            </div>
            <span className="user-name">{username}</span>
          </div>
          <button onClick={handleLogout} className="btn-logout">Đăng xuất</button>
        </div>
      </div>
    </header>
  );
};

export default Header;