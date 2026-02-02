import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './PublicHeader.css';

const PublicHeader: React.FC = () => {
  const location = useLocation();
  const isLandingPage = location.pathname === '/';

  return (
    <header className="public-header">
      <div className="container header-container">
        <Link to="/" className="logo">
          <i className="fas fa-robot logo-icon"></i>
          <span className="logo-text">AESP</span>
        </Link>
        
        {/* Nếu là trang Landing thì hiện menu Tính năng/Giá cả, nếu là Login/Register thì hiện nút Trở về */}
        {isLandingPage ? (
          <>
            <nav className="nav-links">
              <a href="#features">Tính năng</a>
              <a href="#pricing">Giá cả</a>
              <a href="#about">Về chúng tôi</a>
            </nav>
            <div className="auth-buttons">
              <Link to="/login" className="btn btn-outline">Đăng nhập</Link>
              <Link to="/register" className="btn btn-primary">Đăng ký</Link>
            </div>
          </>
        ) : (
          <div className="auth-buttons">
            <Link to="/" className="btn btn-outline">Trở về trang chủ</Link>
          </div>
        )}
      </div>
    </header>
  );
};

export default PublicHeader;