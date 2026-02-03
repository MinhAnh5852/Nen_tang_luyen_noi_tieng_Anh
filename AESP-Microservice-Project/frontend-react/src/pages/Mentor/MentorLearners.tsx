import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, Eye } from 'lucide-react';
// Bổ sung import CSS tại đây
import './MentorLearners.css'; 

interface Learner {
  id: string;
  username: string;
  email: string;
  user_level: string;
  status: string;
  package_name: string;
}

const MentorLearners: React.FC = () => {
  const [learners, setLearners] = useState<Learner[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  const fetchLearners = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5002/api/learners-list');
      const data = await response.json();
      setLearners(data);
    } catch (error) {
      console.error("Lỗi tải danh sách học viên:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLearners();
  }, []);

  const filteredLearners = learners.filter(l => 
    l.username.toLowerCase().includes(searchTerm.toLowerCase()) || 
    l.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="mentor-learners-container">
      <div className="content-card">
        <div className="header-flex">
          <div>
            <h2>Học Viên Của Tôi</h2>
            <p className="muted">Quản lý và theo dõi lộ trình học tập của học viên</p>
          </div>
          <button className="btn-primary" onClick={fetchLearners}>
            <RefreshCw size={18} className={loading ? 'fa-spin' : ''} /> 
            <span>Làm mới</span>
          </button>
        </div>

        <div className="toolbar">
          <div className="search-box">
            <Search size={18} className="search-icon" />
            <input 
              type="text" 
              placeholder="Tìm theo tên hoặc email..." 
              className="form-control"
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Học viên</th>
                <th>Cấp độ</th>
                <th>Gói dịch vụ</th>
                <th>Trạng thái</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="text-center">Đang tải dữ liệu...</td></tr>
              ) : filteredLearners.length > 0 ? (
                filteredLearners.map((learner) => (
                  <tr key={learner.id}>
                    <td>
                      <div className="user-info-cell">
                        <div className="mentor-avatar">
                          {learner.username.charAt(0).toUpperCase()}
                        </div>
                        <div className="user-text">
                          <div className="username">{learner.username}</div>
                          <div className="email">{learner.email}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="level-badge">{learner.user_level || 'N/A'}</span>
                    </td>
                    <td>{learner.package_name}</td>
                    <td>
                      <span className={`pill ${learner.status === 'active' ? 'pill-success' : 'pill-muted'}`}>
                        {learner.status === 'active' ? 'Đang học' : 'Tạm khóa'}
                      </span>
                    </td>
                    <td>
                      <button className="btn-sm btn-outline">
                        <Eye size={14} /> <span>Chi tiết</span>
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan={5} className="text-center">Không tìm thấy học viên nào.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default MentorLearners;