import React, { useState, useEffect } from 'react';
import { ClipboardCheck, PlayCircle } from 'lucide-react';
import './MentorSubmissions.css';

const MentorSubmissions = () => {
  const [subs, setSubs] = useState([]);
  const [selected, setSelected] = useState<any>(null);
  const [form, setForm] = useState({ score: '', feedback: '' });

  useEffect(() => {
    // API lấy bài nộp từ database user_db
    fetch('http://127.0.0.1:5002/api/submissions').then(res => res.json()).then(setSubs);
  }, []);

  const submitGrade = async () => {
    if (!form.score) return alert("Vui lòng nhập điểm số!");
    const res = await fetch(`http://127.0.0.1:5002/api/submissions/${selected.id}/grade`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    });
    if (res.ok) { 
      alert("✅ Chấm điểm thành công!"); 
      setSelected(null); 
      // Refresh dữ liệu sau khi chấm
      fetch('http://127.0.0.1:5002/api/submissions').then(res => res.json()).then(setSubs);
    }
  };

  return (
    <div className="mentor-submissions-container">
      <div className="content-card">
        <div className="submissions-header">
          <h2>Quản Lý Bài Nộp</h2>
          <p>Nghe và chấm điểm các bài luyện nói của học viên.</p>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Học viên</th>
              <th>Bài tập</th>
              <th>Ngày nộp</th>
              <th>Trạng thái</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {subs.map((s: any) => (
              <tr key={s.id}>
                <td style={{fontWeight: 600}}>{s.learner_name}</td>
                <td>{s.task_title}</td>
                <td>{s.date}</td>
                <td>
                  {s.status === 'Pending' ? 
                    <span className="badge-warn">Chưa chấm</span> : 
                    <span className="badge-success">Đã chấm ({s.score})</span>
                  }
                </td>
                <td>
                  <button className="btn-sm btn-outline" onClick={() => setSelected(s)}>
                    <ClipboardCheck size={16} /> Chấm bài
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className="modal-overlay show">
          <div className="modal-content">
            <h3 style={{margin: '0 0 20px 0'}}>✍️ Chấm Điểm & Nhận Xét</h3>
            
            <div className="audio-preview-container">
              <p><PlayCircle size={16} /> Nghe bài làm học viên:</p>
              <audio controls src={selected.audio_link} style={{width:'100%'}} />
            </div>

            <div className="grading-form-group">
              <label>Điểm số (0 - 10):</label>
              <input 
                type="number" min="0" max="10" step="0.5" 
                placeholder="Nhập điểm..." 
                onChange={e => setForm({...form, score: e.target.value})} 
              />
            </div>

            <div className="grading-form-group">
              <label>Nhận xét chi tiết:</label>
              <textarea 
                placeholder="Nhận xét về phát âm, ngữ điệu..." 
                rows={4}
                onChange={e => setForm({...form, feedback: e.target.value})} 
              />
            </div>

            <div className="modal-actions">
              <button className="btn-primary" onClick={submitGrade}>Hoàn Tất</button>
              <button className="btn-outline" onClick={() => setSelected(null)}>Hủy bỏ</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MentorSubmissions;