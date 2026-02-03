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
  const [timeFilter, setTimeFilter] = useState('Hôm nay');

  useEffect(() => {
    const fetchAnalytics = async () => {
      const token = localStorage.getItem('token');
      const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
      const userId = userInfo.id;
      
      if (!userId) return;

      try {
        const res = await fetch(`/api/analytics/detailed/${userId}?filter=${timeFilter}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (e) {
        console.error("Lỗi nạp dữ liệu tiến độ:", e);
      }
    };
    fetchAnalytics();
  }, [timeFilter]);

  const vocabPercentage = stats ? Math.min((stats.vocabulary_count / 500) * 100, 100) : 0;

  return (
    /* Dùng ID duy nhất để Scoped CSS, ngăn chặn đụng chạm Header/Footer */
    <div id="aesp-progress-unique-page">
      <div className="inner-content">
        
        <header className="page-header">
          <h1>Phân tích tiến độ học tập</h1>
          <div className="filter-group">
            {['Hôm nay', '7 ngày', '10 ngày'].map(f => (
              <button 
                key={f} 
                className={`filter-item ${timeFilter === f ? 'active' : ''}`}
                onClick={() => setTimeFilter(f)}
              >
                {f}
              </button>
            ))}
          </div>
        </header>

        {/* Thẻ chỉ số tổng quan */}
        <div className="stats-grid">
          <div className="card-item">
            <TrendingUp color="#4361ee" size={28} />
            <div className="card-val">
              <h3>{stats?.completion_rate ?? 0}%</h3>
              <p>Hoàn thành lộ trình</p>
            </div>
          </div>
          <div className="card-item">
            <CheckCircle color="#22c55e" size={28} />
            <div className="card-val">
              <h3>{stats?.lessons_done ?? 0}</h3>
              <p>Bài học đã học</p>
            </div>
          </div>
          <div className="card-item">
            <Award color="#f59e0b" size={28} />
            <div className="card-val">
              <h3>{stats?.streak ?? 0}</h3>
              <p>Ngày liên tiếp</p>
            </div>
          </div>
          <div className="card-item">
            <Clock color="#4cc9f0" size={28} />
            <div className="card-val">
              <h3>{stats?.learning_hours ?? 0}h</h3>
              <p>Thời gian luyện tập</p>
            </div>
          </div>
        </div>

        {/* Biểu đồ chính */}
        <section className="chart-box">
          <h2>Độ chính xác phát âm (AI Feedback)</h2>
          <div className="chart-render">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats?.pronunciation_history || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#eee" />
                <XAxis dataKey="date" tick={{fontSize: 12}} />
                <YAxis domain={[0, 100]} tick={{fontSize: 12}} />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#4361ee" 
                  strokeWidth={4} 
                  dot={{ r: 6, fill: "#4361ee", strokeWidth: 2, stroke: "#fff" }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Chi tiết từ vựng và cột mốc */}
        <div className="bottom-row">
          <div className="detail-card vocab">
            <h3>Vốn từ vựng đã nạp</h3>
            <div className="number-display">{stats?.vocabulary_count ?? 0} <span>từ</span></div>
            <div className="progress-bar-bg">
               <div className="progress-bar-fill" style={{ width: `${vocabPercentage}%` }}></div>
            </div>
            <div className="bar-label">Mục tiêu: 500 từ</div>
          </div>
          
          <div className="detail-card milestones">
            <h3>Cột mốc quan trọng</h3>
            <ul className="list-milestone">
                <li><CheckCircle size={18} color="#22c55e" /> Đã xong Phát âm cơ bản</li>
                <li><CheckCircle size={18} color="#22c55e" /> Đạt 70% độ chính xác</li>
                <li><span className="dot-wait"></span> Đạt trình độ Trung cấp</li>
            </ul>
          </div>
        </div>

        {/* Nút thao tác */}
        <footer className="footer-actions">
          <button className="btn-main" onClick={() => window.print()}>
            <Download size={18} /> Tải báo cáo
          </button>
          <button className="btn-sub">
            <Share2 size={18} /> Chia sẻ Mentor
          </button>
        </footer>
      </div>
    </div>
  );
};

export default Progress;