import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { 
  Users, 
  BarChart3, 
  MessageSquare, 
  ClipboardCheck, 
  FolderOpen, 
  Settings, 
  LogOut,
  Bot,
  LayoutDashboard,
  BookOpen
} from 'lucide-react';
import './MentorLayout.css';

const MentorLayout: React.FC = () => {
  const navigate = useNavigate();
  
  // Lấy thông tin người dùng từ localStorage để hiển thị thực tế
  const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
  const username = userInfo.username || "Mentor AESP";

  const handleLogout = () => {
    if (window.confirm("Bạn có chắc muốn đăng xuất khỏi hệ thống Mentor?")) {
      localStorage.clear();
      navigate('/login');
    }
  };

  return (
    <div className="mentor-app-container">
      {/* SIDEBAR - Kế thừa phong cách từ mentor.html cũ */}
      <aside className="mentor-sidebar">
        <div className="sb-brand">
          <div className="sb-logo">
            <Bot size={28} color="#3b82f6" />
          </div>
          <div>
            <h3>AESP</h3>
            <p>Mentor Dashboard</p>
          </div>
        </div>

        <div className="sb-menu">
          <div className="sb-group-title">DASHBOARD</div>
          <NavLink to="/mentor/learners" className={({ isActive }) => isActive ? "sb-link active" : "sb-link"}>
            <Users size={18} /> <span>Học viên</span>
          </NavLink>

          <div className="sb-group-title">QUẢN LÝ</div>
          <NavLink to="/mentor/submissions" className={({ isActive }) => isActive ? "sb-link active" : "sb-link"}>
            <ClipboardCheck size={18} /> <span>Chấm điểm bài nộp</span>
          </NavLink>
          <NavLink to="/mentor/tasks" className={({ isActive }) => isActive ? "sb-link active" : "sb-link"}>
            <BookOpen size={18} /> <span>Giao bài tập</span>
          </NavLink>
          <NavLink to="/mentor/feedback" className={({ isActive }) => isActive ? "sb-link active" : "sb-link"}>
            <MessageSquare size={18} /> <span>Phản hồi AI</span>
          </NavLink>
          <NavLink to="/mentor/resources" className={({ isActive }) => isActive ? "sb-link active" : "sb-link"}>
            <FolderOpen size={18} /> <span>Tài liệu hỗ trợ</span>
          </NavLink>

          <div className="sb-group-title">HỆ THỐNG</div>
          <NavLink to="/mentor/settings" className={({ isActive }) => isActive ? "sb-link active" : "sb-link"}>
            <Settings size={18} /> <span>Cài đặt</span>
          </NavLink>
          <button className="sb-link btn-logout-sidebar" onClick={handleLogout}>
            <LogOut size={18} /> <span>Đăng xuất</span>
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT Area */}
      <div className="mentor-main-content">
        <header className="mentor-topbar">
          <div className="topbar-inner">
            <h1 className="topbar-title">Hệ thống Cố vấn AESP</h1>
            <div className="topbar-right">
              <div className="mentor-profile-info">
                <div className="mentor-avatar">
                  {username.charAt(0).toUpperCase()}
                </div>
                <div className="mentor-details">
                  <span className="mentor-name">{username}</span>
                  <span className="mentor-role">Chuyên gia ngôn ngữ</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        <section className="mentor-page-body">
          {/* Outlet: Nơi render các trang con (Learners, Submissions, v.v.) */}
          <Outlet />
        </section>
      </div>
    </div>
  );
};

export default MentorLayout;