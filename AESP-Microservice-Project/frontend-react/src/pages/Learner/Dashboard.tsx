import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

interface ProgressData {
  total_time: string;
  accuracy: number | null;
  lessons_completed: number;
  streak: number;
  ai_suggestion: string;
}

const Dashboard: React.FC = () => {
  const [username, setUsername] = useState("Học viên");
  const [data, setData] = useState<ProgressData>({
    total_time: "--h --m",
    accuracy: null,
    lessons_completed: 0,
    streak: 0,
    ai_suggestion: "Hôm nay bạn đã sẵn sàng để luyện tập chưa? Hãy bắt đầu ngay nhé!"
  });

  useEffect(() => {
    const storedName = localStorage.getItem('username');
    const token = localStorage.getItem('token');
    if (storedName) setUsername(storedName);

    const fetchProgress = async () => {
      if (!token) return;
      try {
        const response = await fetch('/api/analytics/my-progress', {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const result = await response.json();
          setData(prevData => ({
            ...prevData,
            total_time: result.total_time || "0h 0m",
            accuracy: result.accuracy,
            lessons_completed: result.lessons_completed || 0,
            streak: result.streak || 0,
            ai_suggestion: result.ai_suggestion || prevData.ai_suggestion
          }));
        }
      } catch (error) {
        console.error("Lỗi nạp dữ liệu:", error);
      }
    };

    fetchProgress();
  }, []);

  return (
    <div className="container">
      <div className="welcome-banner">
        <h1>Chào mừng trở lại, {username}!</h1>
        <p>{data.ai_suggestion}</p>
        <div style={{ marginTop: '25px' }}>
          {/* Sửa textDecoration: 'none' ở dưới đây */}
          <Link to="/practice" className="btn btn-primary" style={{ background: 'white', color: '#4361ee', fontWeight: 700, textDecoration: 'none', padding: '15px 30px', borderRadius: '12px', display: 'inline-block', boxShadow: '0 4px 15px rgba(0,0,0,0.1)' }}>
            <i className="fas fa-microphone" style={{ marginRight: '8px' }}></i> Bắt đầu luyện tập ngay
          </Link>
        </div>
      </div>
      
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-icon primary"><i className="fas fa-clock"></i></div>
          <div className="stat-info">
            <h3>{data.total_time}</h3>
            <p>Tổng thời gian</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon success"><i className="fas fa-chart-line"></i></div>
          <div className="stat-info">
            <h3>{data.accuracy !== null ? data.accuracy + "%" : "0%"}</h3>
            <p>Độ chính xác</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon warning"><i className="fas fa-trophy"></i></div>
          <div className="stat-info">
            <h3>{data.lessons_completed}</h3>
            <p>Bài học</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon accent"><i className="fas fa-fire"></i></div>
          <div className="stat-info">
            <h3>{data.streak}</h3>
            <p>Ngày liên tiếp</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;