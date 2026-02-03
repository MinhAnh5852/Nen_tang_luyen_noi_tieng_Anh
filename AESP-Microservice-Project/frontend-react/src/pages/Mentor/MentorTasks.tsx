import React, { useState, useEffect } from 'react';
import { BookOpen, Plus, Send, Calendar, User, AlignLeft } from 'lucide-react';
import './MentorTasks.css';

interface Task {
  id: number;
  learner_name: string;
  title: string;
  deadline: string;
  status: string;
}

const MentorTasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [learners, setLearners] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // State cho form bài tập mới
  const [formData, setFormData] = useState({
    learner_id: '',
    title: '',
    deadline: '',
    description: ''
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      // Tải danh sách bài tập đã giao
      const tasksRes = await fetch('http://127.0.0.1:5002/api/tasks');
      const tasksData = await tasksRes.json();
      setTasks(tasksData);

      // Tải danh sách học viên để chọn khi giao bài
      const learnersRes = await fetch('http://127.0.0.1:5002/api/learners-list');
      const learnersData = await learnersRes.json();
      setLearners(learnersData);
    } catch (error) {
      console.error("Lỗi nạp dữ liệu:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.learner_id || !formData.title || !formData.deadline) {
      alert("Vui lòng điền đầy đủ các thông tin bắt buộc!");
      return;
    }

    try {
      const res = await fetch('http://127.0.0.1:5002/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (res.ok) {
        alert("✅ Giao bài tập thành công!");
        setShowModal(false);
        setFormData({ learner_id: '', title: '', deadline: '', description: '' });
        fetchData();
      }
    } catch (error) {
      alert("❌ Lỗi kết nối server");
    }
  };

  return (
    <div className="mentor-tasks-container">
      <div className="content-card">
        <div className="tasks-header">
          <div>
            <h2><BookOpen size={24} /> Quản Lý Bài Tập</h2>
            <p className="muted">Giao bài tập và theo dõi tình trạng làm bài của học viên.</p>
          </div>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={18} /> Giao bài mới
          </button>
        </div>

        <div className="task-grid">
          {loading ? (
            <p>Đang tải danh sách bài tập...</p>
          ) : tasks.length > 0 ? (
            tasks.map(task => (
              <div key={task.id} className="task-item-card">
                <div className="task-status">
                  <span className={`pill ${task.status === 'Pending' ? 'pill-warn' : 'pill-success'}`}>
                    {task.status === 'Pending' ? 'Chưa nộp' : 'Đã hoàn thành'}
                  </span>
                </div>
                <h4 className="task-title">{task.title}</h4>
                <div className="task-info">
                  <span><User size={14} /> {task.learner_name}</span>
                  <span><Calendar size={14} /> Hạn: {task.deadline}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="no-data">Chưa có bài tập nào được giao.</div>
          )}
        </div>
      </div>

      {/* Modal Giao Bài Tập */}
      {showModal && (
        <div className="modal-overlay show">
          <div className="modal-content">
            <div className="modal-header">
              <h3>📋 Giao Bài Tập Mới</h3>
              <button className="close-btn" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleCreateTask}>
              <div className="form-group">
                <label>Chọn học viên *</label>
                <select 
                  className="form-control"
                  value={formData.learner_id}
                  onChange={e => setFormData({...formData, learner_id: e.target.value})}
                >
                  <option value="">-- Chọn học viên nhận bài --</option>
                  {learners.map(l => (
                    <option key={l.id} value={l.id}>{l.username}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Tiêu đề bài tập *</label>
                <input 
                  type="text" 
                  className="form-control"
                  placeholder="Ví dụ: Luyện nói chủ đề Daily Routine"
                  value={formData.title}
                  onChange={e => setFormData({...formData, title: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Hạn nộp (Deadline) *</label>
                <input 
                  type="date" 
                  className="form-control"
                  value={formData.deadline}
                  onChange={e => setFormData({...formData, deadline: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>Yêu cầu chi tiết</label>
                <textarea 
                  className="form-control"
                  rows={4}
                  placeholder="Mô tả các yêu cầu cần thực hiện..."
                  value={formData.description}
                  onChange={e => setFormData({...formData, description: e.target.value})}
                />
              </div>
              <div className="modal-footer">
                <button type="submit" className="btn-primary"><Send size={16} /> Gửi Bài Tập</button>
                <button type="button" className="btn-outline" onClick={() => setShowModal(false)}>Hủy</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MentorTasks;