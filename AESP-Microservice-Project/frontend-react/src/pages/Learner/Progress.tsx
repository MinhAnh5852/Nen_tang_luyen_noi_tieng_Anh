import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { Download, Share2, Award, Clock, TrendingUp, CheckCircle } from 'lucide-react';
import './Progress.css';

interface ProgressStats {
  completion_rate: number;
  lessons_done: number;
  streak: number;
  learning_hours: number;
  vocabulary_count: number;
  pronunciation_history: { date: string; score: number }[];
}

const Progress: React.FC = () => {
  const [stats, setStats] = useState<ProgressStats | null>(null);
  const [timeFilter, setTimeFilter] = useState('7 ngày');

  useEffect(() => {
    const fetchAnalytics = async () => {
      const token = localStorage.getItem('token');
      const userId = localStorage.getItem('user_id');
      
      try {
        // Gọi API thực tế từ Analytics Service
        const res = await fetch(`/api/analytics/detailed/${userId}?filter=${timeFilter}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        setStats(data);
      } catch (e) {
        console.error("Lỗi nạp dữ liệu tiến độ:", e);
      }
    };
    fetchAnalytics();
  }, [timeFilter]);

  return (
    <div className="container" style={{ marginTop: '100px' }}>
      <div className="progress-header">
        <h1>Phân tích tiến độ học tập</h1>
        <div className="time-filter">
          {['7 ngày', '30 ngày', '3 tháng'].map(f => (
            <button 
              key={f} 
              className={`btn btn-outline ${timeFilter === f ? 'active' : ''}`}
              onClick={() => setTimeFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Thẻ chỉ số tổng quan */}
      <div className="stats-overview-grid">
        <div className="stat-card-detailed">
          <TrendingUp color="#4361ee" />
          <h3>{stats?.completion_rate || 78}%</h3>
          <p>Hoàn thành lộ trình</p>
        </div>
        <div className="stat-card-detailed">
          <CheckCircle color="#22c55e" />
          <h3>{stats?.lessons_done || 24}</h3>
          <p>Bài học đã học</p>
        </div>
        <div className="stat-card-detailed">
          <Award color="#f59e0b" />
          <h3>{stats?.streak || 15}</h3>
          <p>Ngày liên tiếp</p>
        </div>
        <div className="stat-card-detailed">
          <Clock color="#4cc9f0" />
          <h3>{stats?.learning_hours || 12.5}h</h3>
          <p>Thời gian luyện tập</p>
        </div>
      </div>

      {/* Biểu đồ độ chính xác phát âm */}
      <div className="chart-section">
        <h2>Độ chính xác phát âm (AI Feedback)</h2>
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats?.pronunciation_history || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="#4361ee" strokeWidth={3} dot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Thống kê chi tiết */}
      <div className="detailed-grid">
        <div className="stat-box">
          <h3>Vốn từ vựng đã nạp</h3>
          <div className="big-number">{stats?.vocabulary_count || 320} từ</div>
          <div className="progress-bar">
             <div className="progress-fill" style={{ width: '64%', background: '#4361ee' }}></div>
          </div>
          <small>Mục tiêu: 500 từ</small>
        </div>
        
        <div className="stat-box">
          <h3>Cột mốc quan trọng</h3>
          <ul className="milestone-list">
             <li><CheckCircle size={16} color="#22c55e" /> Đã xong Phát âm cơ bản</li>
             <li><CheckCircle size={16} color="#22c55e" /> Đạt 70% độ chính xác</li>
             <li><div className="dot-pending"></div> Đạt trình độ Trung cấp (Đang luyện)</li>
          </ul>
        </div>
      </div>

      {/* Nút hành động */}
      <div className="action-buttons">
        <button className="btn btn-primary" onClick={() => window.print()}>
          <Download size={18} /> Tải báo cáo chi tiết
        </button>
        <button className="btn btn-outline">
          <Share2 size={18} /> Chia sẻ với Mentor
        </button>
      </div>
    </div>
  );
};

export default Progress;