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

interface Mentor {
  id: string;
  username: string;
  skills: string;
  rating: number;
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

  const [mentors, setMentors] = useState<Mentor[]>([]);
  const [myMentor, setMyMentor] = useState<Mentor | null>(null);
  const [isPro, setIsPro] = useState(false);

  useEffect(() => {
    // 1. Lấy thông tin user từ localStorage
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
    const token = localStorage.getItem('token');
    
    // Đảm bảo lấy ID từ object user_info (Khớp với ảnh Application của bạn)
    const userId = userInfo.id; 

    if (userInfo.username) setUsername(userInfo.username);
    
    // 2. Kiểm tra gói cước để mở khóa tính năng Mentor
    if (userInfo.package_id === 'pro-id-002') {
      setIsPro(true);
    }

    const fetchData = async () => {
      if (!token || !userId) return;
      
      try {
        // Lấy dữ liệu thống kê
        const resAnalytics = await fetch(`/api/analytics/summary/${userId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (resAnalytics.ok) {
          const result = await resAnalytics.json();
          setData(prev => ({ ...prev, ...result }));
        }

        // Lấy danh sách Mentor có sẵn
        const resMentors = await fetch('/api/users/mentors/available', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (resMentors.ok) setMentors(await resMentors.json());

        // Lấy Mentor hiện tại của tôi
        const resMyMentor = await fetch(`/api/users/my-mentor/${userId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (resMyMentor.ok) {
          const mentorData = await resMyMentor.json();
          setMyMentor(mentorData); // mentorData có thể là null nếu chưa chọn
        }

      } catch (error) {
        console.error("Lỗi nạp dữ liệu Dashboard:", error);
      }
    };

    fetchData();
  }, []);

  const handleSelectMentor = async (mentorId: string) => {
    const token = localStorage.getItem('token');
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
    const userId = userInfo.id;
    
    if (!isPro) {
      alert("Bạn cần nâng cấp lên gói Pro AI để chọn Mentor hướng dẫn!");
      return;
    }

    if (!userId) {
      alert("Không tìm thấy thông tin người dùng. Vui lòng đăng nhập lại.");
      return;
    }

    try {
      const res = await fetch('/api/users/mentors/select', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ learner_id: userId, mentor_id: mentorId })
      });

      if (res.ok) {
        alert("Kết nối với Cố vấn thành công!");
        window.location.reload();
      } else {
        const errData = await res.json();
        alert("Lỗi: " + (errData.error || "Không thể chọn mentor"));
      }
    } catch (err) {
      alert("Đã xảy ra lỗi kết nối với máy chủ.");
    }
  };

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

      <div className="mentor-section-dashboard">
        <div className="section-title-row">
          <h3><i className="fas fa-user-graduate"></i> Cố vấn đồng hành</h3>
          {!isPro && <Link to="/subscription" className="upgrade-link">Nâng cấp để chọn Mentor</Link>}
        </div>

        {myMentor ? (
          <div className="my-mentor-active-card">
            <div className="mentor-avatar-circle">{myMentor.username ? myMentor.username[0].toUpperCase() : 'M'}</div>
            <div className="mentor-meta">
              <h4>{myMentor.username}</h4>
              <p>Chuyên gia: {myMentor.skills || 'General English'}</p>
            </div>
            <button className="btn-msg"><i className="fas fa-comments"></i> Nhắn tin</button>
          </div>
        ) : (
          <div className="mentor-scroll-container">
            {mentors.map(m => (
              <div key={m.id} className="mentor-mini-card">
                <div className="mini-avatar">{m.username[0].toUpperCase()}</div>
                <h5>{m.username}</h5>
                <span className="rating-tag">⭐ {m.rating}</span>
                <button 
                  onClick={() => handleSelectMentor(m.id)} 
                  disabled={!isPro}
                  className={isPro ? "btn-connect-active" : "btn-connect-disabled"}
                >
                  Kết nối
                </button>
              </div>
            ))}
            {mentors.length === 0 && <p className="empty-text">Hiện chưa có Mentor nào sẵn sàng.</p>}
          </div>
        )}
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