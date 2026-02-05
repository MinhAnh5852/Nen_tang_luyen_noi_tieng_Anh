import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // 1. Import useNavigate
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Download, Award, Clock, TrendingUp, BookOpen, Send } from 'lucide-react';
import './Progress.css';

interface Task {
  id: number;
  title: string;
  description: string;
  deadline: string;
  status: string;
  learner_name: string;
}

interface ProgressStats {
  lessons_done: number;
  streak: number;
  learning_hours: string;
  accuracy: number;
  vocabulary_count: number;
  pronunciation_history: { date: string; score: number }[];
  assigned_tasks: Task[];
}

const Progress: React.FC = () => {
  const navigate = useNavigate(); // 2. Khởi tạo hook chuyển hướng
  const [stats, setStats] = useState<ProgressStats | null>(null);
  const [timeFilter, setTimeFilter] = useState('7 ngày');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const token = localStorage.getItem('token');
      const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
      
      try {
        const analyticsRes = await fetch(`/api/analytics/detailed/${userInfo.id}?filter=${timeFilter}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        const tasksRes = await fetch(`/api/mentors/tasks`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        const analyticsData = analyticsRes.ok ? await analyticsRes.json() : {};
        const tasksData: Task[] = tasksRes.ok ? await tasksRes.json() : [];

        const myTasks = tasksData.filter(t => t.learner_name === userInfo.username);

        setStats({
          lessons_done: analyticsData.lessons_done || 0,
          streak: analyticsData.streak || 0,
          learning_hours: analyticsData.learning_hours || "0h 0m",
          accuracy: analyticsData.accuracy || 0,
          vocabulary_count: analyticsData.vocabulary_count || 0,
          pronunciation_history: analyticsData.pronunciation_history || [],
          assigned_tasks: myTasks
        });
      } catch (e) {
        console.error("Lỗi nạp dữ liệu hệ thống:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [timeFilter]);

  // 3. Cập nhật hàm xử lý chuyển hướng kèm dữ liệu bài tập
  const handleDoTask = (task: Task) => {
    // Chuyển hướng sang trang Luyện tập AI (thường là /practice hoặc /ai-chat)
    // Truyền dữ liệu qua state để AI Core Service nhận diện yêu cầu của Mentor
    navigate('/practice', { 
      state: { 
        taskId: task.id, 
        topic: task.title, 
        description: task.description,
        isFromTask: true
      } 
    });
  };

  if (loading) return <div className="loading-state">Đang đồng bộ dữ liệu từ AESP Services...</div>;

  return (
    <div className="aesp-progress-wrapper">
      <div className="progress-content-inner">
        <header className="progress-top-bar">
          <div className="header-title">
            <h1>Phân tích & Nhiệm vụ học tập</h1>
            <p>Dữ liệu đồng bộ từ Mentor & AI Core - {new Date().toLocaleDateString('vi-VN')}</p>
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
            { label: 'Độ chính xác', val: `${stats?.accuracy}%`, icon: <TrendingUp color="#4361ee" /> },
            { label: 'Ngày liên tiếp', val: stats?.streak, icon: <Award color="#f59e0b" /> },
            { label: 'Thời gian luyện', val: stats?.learning_hours, icon: <Clock color="#4cc9f0" /> }
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

        <section className="assigned-tasks-section">
          <div className="section-header">
            <h2><BookOpen size={20} /> Nhiệm vụ từ Mentor</h2>
          </div>
          <div className="tasks-grid">
            {stats?.assigned_tasks && stats.assigned_tasks.length > 0 ? (
              stats.assigned_tasks.map(task => (
                <div key={task.id} className="task-card">
                  <div className="task-status-tag">{task.status}</div>
                  <h3>{task.title}</h3>
                  <p>{task.description}</p>
                  <div className="task-footer">
                    <span><Clock size={14} /> Hạn: {task.deadline}</span>
                    {/* 4. Sửa nút bấm để truyền object task vào hàm xử lý */}
                    <button className="btn-do-task" onClick={() => handleDoTask(task)}>
                      Làm bài ngay <Send size={14} />
                    </button>
                  </div>
                </div>
              ))
            ) : (
              <p className="no-data">Hiện tại bạn chưa có nhiệm vụ nào từ Mentor.</p>
            )}
          </div>
        </section>

        <section className="analysis-chart-section">
          <h2>Xu hướng phát âm AI (AESP Feedback)</h2>
          <div className="chart-render-container">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={stats?.pronunciation_history}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="#4361ee" 
                  strokeWidth={3} 
                  dot={{ r: 5, fill: "#4361ee" }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <footer className="report-action-btns">
          <button className="btn-download-pdf" onClick={() => window.print()}>
            <Download size={18} /> Tải Performance Report (PDF)
          </button>
        </footer>
      </div>
    </div>
  );
};

export default Progress