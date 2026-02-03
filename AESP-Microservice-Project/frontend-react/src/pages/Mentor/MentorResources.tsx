import React, { useState, useEffect } from 'react';
import { FolderOpen, CloudUpload, ExternalLink, Filter, Trash2 } from 'lucide-react';
import './MentorResources.css';

interface Resource {
  id: number;
  title: string;
  link: string;
  skill_type: string;
  description: string;
}

const MentorResources: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [filter, setFilter] = useState('All');
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);

  const [formData, setFormData] = useState({
    title: '',
    link: '',
    skill_type: 'Speaking',
    description: ''
  });

  const fetchResources = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:5002/api/resources');
      const data = await res.json();
      setResources(data);
    } catch (e) {
      console.error("Lỗi tải tài liệu:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResources();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('http://127.0.0.1:5002/api/resources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        alert("✅ Thêm tài liệu thành công!");
        setShowModal(false);
        setFormData({ title: '', link: '', skill_type: 'Speaking', description: '' });
        fetchResources();
      }
    } catch (e) {
      alert("❌ Lỗi kết nối");
    }
  };

  const filteredData = filter === 'All' ? resources : resources.filter(r => r.skill_type === filter);

  return (
    <div className="mentor-resources-container">
      <div className="content-card">
        <div className="resources-header">
          <div>
            <h2><FolderOpen size={24} /> Kho Tài Liệu Hỗ Trợ</h2>
            <p className="muted">Quản lý các nguồn học liệu bổ trợ cho học viên AESP.</p>
          </div>
          <button className="btn-primary" onClick={() => setShowModal(true)}>
            <CloudUpload size={18} /> Thêm tài liệu
          </button>
        </div>

        <div className="filter-bar">
          <Filter size={18} />
          <select value={filter} onChange={(e) => setFilter(e.target.value)} className="form-control">
            <option value="All">Tất cả kỹ năng</option>
            <option value="Speaking">Speaking</option>
            <option value="Listening">Listening</option>
            <option value="Grammar">Grammar</option>
            <option value="Vocabulary">Vocabulary</option>
          </select>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Kỹ năng</th>
                <th>Tên tài liệu</th>
                <th>Mô tả</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={4} className="text-center">Đang tải...</td></tr>
              ) : filteredData.map(res => (
                <tr key={res.id}>
                  <td><span className={`skill-pill ${res.skill_type.toLowerCase()}`}>{res.skill_type}</span></td>
                  <td style={{ fontWeight: 600 }}>{res.title}</td>
                  <td className="muted">{res.description}</td>
                  <td>
                    <a href={res.link} target="_blank" rel="noreferrer" className="btn-sm btn-outline">
                      <ExternalLink size={14} /> Mở link
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay show">
          <div className="modal-content">
            <h3>📂 Thêm Tài Liệu Mới</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Tên tài liệu:</label>
                <input type="text" required className="form-control" 
                  onChange={e => setFormData({...formData, title: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Đường dẫn (URL):</label>
                <input type="url" required className="form-control" 
                  onChange={e => setFormData({...formData, link: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Kỹ năng:</label>
                <select className="form-control" onChange={e => setFormData({...formData, skill_type: e.target.value})}>
                  <option value="Speaking">Speaking</option>
                  <option value="Listening">Listening</option>
                  <option value="Grammar">Grammar</option>
                  <option value="Vocabulary">Vocabulary</option>
                </select>
              </div>
              <div className="form-group">
                <label>Mô tả ngắn:</label>
                <textarea className="form-control" rows={3} 
                  onChange={e => setFormData({...formData, description: e.target.value})} />
              </div>
              <div className="modal-footer">
                <button type="submit" className="btn-primary">Lưu lại</button>
                <button type="button" className="btn-outline" onClick={() => setShowModal(false)}>Đóng</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MentorResources;