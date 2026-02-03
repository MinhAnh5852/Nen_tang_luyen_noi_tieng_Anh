import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Download, Share2, Award, Clock, TrendingUp, CheckCircle } from 'lucide-react';
import './Progress.css';

interface ProgressStats {
  lessons_done: number;
  streak: number;
  learning_hours: string;
  accuracy: number;
  vocabulary_count: number;
  pronunciation_history: { date: string; score: number }[];
}

const Progress: React.FC = () => {
  const [stats, setStats] = useState<ProgressStats | null>(null);
  const [timeFilter, setTimeFilter] = useState('7 ngày');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      const token = localStorage.getItem('token');
      const userInfoStr = localStorage.getItem('user_info');
      const userInfo = userInfoStr ? JSON.parse(userInfoStr) : {};
      const userId = userInfo.id;
      
      try {
        const res = await fetch(`/api/analytics/detailed/${userId}?filter=${timeFilter}`, {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        } else {
          // Dữ liệu mẫu nếu API chưa trả về kết quả
          setStats({
            lessons_done: 15,
            streak: 4,
            learning_hours: "3h 45m",
            accuracy: 78,
            vocabulary_count: 124,
            pronunciation_history: [
              { date: '28/01', score: 65 },
              { date: '29/01', score: 70 },
              { date: '30/01', score: 68 },
              { date: '31/01', score: 75 },
              { date: '01/02', score: 82 },
              { date: '02/02', score: 80 },
              { date: '03/02', score: 85 }
            ]
          });
        }
      } catch (e) {
        console.error("Lỗi nạp dữ liệu tiến độ:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [timeFilter]);

  const vocabPercentage = stats ? Math.min((stats.vocabulary_count / 500) * 100, 100) : 0;

  return (
    <div className="aesp-progress-wrapper">
      <div className="progress-content-inner">
        <header className="progress-top-bar">
          <div className="header-title">
            <h1>Phân tích tiến độ học tập</h1>
            <p>Dữ liệu dựa trên đánh giá phát âm AI (AESP System)</p>
          </div>
          <div className="time-filter-container">
            {['Hôm nay', '7 ngày', '30 ngày'].map(f => (
              <button 
                key={f} 
                className={`filter-btn-item ${timeFilter === f ? 'active' : ''}`} 
                onClick={() => setTimeFilter(f)}
              >
                {f}
              </button>
            ))}
          </div>
        </header>

        <div className="metrics-grid">
          {[
            { label: 'Độ chính xác', val: `${stats?.accuracy ?? 0}%`, icon: <TrendingUp color="#4361ee" /> },
            { label: 'Bài tập hoàn thành', val: stats?.lessons_done ?? 0, icon: <CheckCircle color="#22c55e" /> },
            { label: 'Ngày liên tiếp', val: stats?.streak ?? 0, icon: <Award color="#f59e0b" /> },
            { label: 'Thời gian luyện', val: stats?.learning_hours ?? "0h 0m", icon: <Clock color="#4cc9f0" /> }
          ].map((item, idx) => (
            <div key={idx} className="metric-card">
              <div className="metric-icon-bg">{item.icon}</div>
              <div className="metric-info">
                <h3>{item.val}</h3>
                <p>{item.label}</p>
              </div>
            </div>
          ))}
        </div>

        <section className="analysis-chart-section">
          <h2>Xu hướng cải thiện phát âm (AI Feedback)</h2>
          <div className="chart-render-container">
            {!loading && stats ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={stats.pronunciation_history} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{fontSize: 12}} dy={10} />
                    <YAxis domain={[0, 100]} tick={{fontSize: 12}} />
                    <Tooltip contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)'}} />
                    <Line 
                      type="monotone" 
                      dataKey="score" 
                      stroke="#4361ee" 
                      strokeWidth={4} 
                      dot={{ r: 6, fill: "#4361ee", stroke: "#fff", strokeWidth: 3 }} 
                    />
                  </LineChart>
                </ResponsiveContainer>
            ) : (
                <div className="no-data-placeholder">Đang tải dữ liệu phân tích...</div>
            )}
          </div>
        </section>

        <div className="details-layout-grid">
          <div className="detail-box vocab-box">
            <h3>Vốn từ vựng đã nạp</h3>
            <div className="main-stat-number">{stats?.vocabulary_count ?? 0} từ</div>
            <div className="progress-line-bg">
                <div className="progress-line-fill" style={{ width: `${vocabPercentage}%` }}></div>
            </div>
            <p className="goal-text">Mục tiêu: 500 từ</p>
          </div>
          
          <div className="detail-box milestone-box">
            <h3>Cột mốc quan trọng</h3>
            <ul className="milestone-check-list">
                <li><CheckCircle size={18} color="#22c55e" /> Đạt 70% độ chính xác phát âm</li>
                <li><CheckCircle size={18} color="#22c55e" /> Hoàn thành bài đánh giá đầu vào</li>
                <li><span className="dot-indicator"></span> Sẵn sàng cho trình độ Trung cấp</li>
            </ul>
          </div>
        </div>

        <footer className="report-action-btns">
          <button className="btn-download-pdf" onClick={() => window.print()}>
            <Download size={18} /> Tải Performance Report
          </button>
          <button className="btn-share-mentor">
            <Share2 size={18} /> Chia sẻ với Mentor
          </button>
        </footer>
      </div>
    </div>
  );
};

export default Progress;