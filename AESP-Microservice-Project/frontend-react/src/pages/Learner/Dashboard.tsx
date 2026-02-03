// Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import './Dashboard.css';

interface ProgressData {
  total_time: string;
  accuracy: number | null;
  lessons_completed: number;
  streak: number;
  ai_suggestion: string;
  weekly_activity: { day: string; hours: number }[];
}

const Dashboard: React.FC = () => {
  const [username, setUsername] = useState("Học viên");
  const [data, setData] = useState<ProgressData>({
    total_time: "0h 0m",
    accuracy: null,
    lessons_completed: 0,
    streak: 0,
    ai_suggestion: "Hôm nay bạn đã sẵn sàng để luyện tập chưa? Hãy bắt đầu ngay nhé!",
    weekly_activity: []
  });

  useEffect(() => {
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
    if (userInfo.username) setUsername(userInfo.username);
    
    const token = localStorage.getItem('token');
    const userId = userInfo.id || localStorage.getItem('user_id');

    const fetchDashboardData = async () => {
      if (!token || !userId) return;
      
      try {
        const response = await fetch(`/api/analytics/summary/${userId}`, {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
           console.error(`Lỗi hệ thống: ${response.status}`);
           return;
        }

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          const result = await response.json();
          setData(prev => ({
            ...prev,
            ...result,
            total_time: result.total_time || "0h 0m"
          }));
        }
      } catch (error) {
        console.error("Lỗi nạp dữ liệu Dashboard:", error);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="learner-dashboard-wrapper">
      <div className="welcome-banner-aesp">
        <div className="banner-text">
          <h1>Chào mừng trở lại, {username}!</h1>
          <p>{data.ai_suggestion}</p>
          <Link to="/practice" className="btn-action-primary">
            <i className="fas fa-microphone"></i> Bắt đầu luyện tập
          </Link>
        </div>
      </div>
      
      <div className="stats-cards-row">
        {[
          { label: 'Thời gian', val: data.total_time, icon: 'fa-clock', color: 'blue' },
          { label: 'Chính xác', val: (data.accuracy || 0) + '%', icon: 'fa-bullseye', color: 'green' },
          { label: 'Bài học', val: data.lessons_completed, icon: 'fa-book', color: 'orange' },
          { label: 'Streak', val: data.streak, icon: 'fa-fire', color: 'red' }
        ].map((item, idx) => (
          <div key={idx} className="stat-box-card">
            <div className={`icon-circle ${item.color}`}><i className={`fas ${item.icon}`}></i></div>
            <div className="box-val">
              <h3>{item.val}</h3>
              <p>{item.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="dashboard-main-row">
        <div className="activity-chart-box">
          <h3>Hoạt động tuần này</h3>
          {/* Cố định chiều cao 300px để tránh lỗi ResponsiveContainer width/height <= 0 */}
          <div className="chart-container-fixed" style={{ height: '300px', width: '100%', minHeight: '300px' }}>
            {data.weekly_activity && data.weekly_activity.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.weekly_activity}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="hours" stroke="#4361ee" fill="#e0e7ff" strokeWidth={3} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="no-data-placeholder" style={{ textAlign: 'center', paddingTop: '100px', color: '#64748b' }}>
                Chưa có dữ liệu hoạt động tuần này
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;