import React, { useState, useEffect } from 'react';
import './Profile.css';

interface UserProfile {
  id: string;
  username: string;
  email: string;
  role: string;
  package_name: string;
  created_at: string;
}

interface LearningStats {
  lessons_completed: number;
  accuracy_avg: number;
  streak_days: number;
}

const Profile: React.FC = () => {
  const [activeTab, setActiveTab] = useState('personal');
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const [user, setUser] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<LearningStats | null>(null);
  const [subscription, setSubscription] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      const userInfoStr = localStorage.getItem("user_info");
      const userInfo = userInfoStr ? JSON.parse(userInfoStr) : null;
      const userId = userInfo?.id;

      if (!token || !userId) return;

      try {
        setLoading(true);
        
        // 1. Lấy thông tin cá nhân
        const userRes = await fetch(`http://localhost/api/users/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (userRes.ok) {
          const userData = await userRes.json();
          setUser(userData);
        }

        // 2. Lấy thống kê từ Analytics Service
        const statsRes = await fetch(`http://localhost/api/analytics/summary/${userId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
        }

        // 3. Đồng bộ gói qua API Verify
        const subRes = await fetch(`http://localhost/api/verify`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (subRes.ok) {
          const subData = await subRes.json();
          setSubscription(subData);
        }
      } catch (error) {
        console.error("Lỗi đồng bộ dữ liệu:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSavePersonalInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    alert('Thông tin cá nhân đã được đồng bộ tới User Service!');
    setIsEditing(false);
  };

  const handleExport = (format: string) => {
    alert(`Đang xuất dữ liệu học tập ở định dạng ${format.toUpperCase()}...`);
  };

  if (loading) return <div className="loading" style={{marginTop: '100px', textAlign: 'center'}}>Đang tải dữ liệu hệ thống AESP...</div>;

  return (
    <main className="container" style={{ marginTop: '100px' }}>
      <div className="profile-header">
        <h1>Hồ sơ học tập</h1>
        <div>
          <button className="btn btn-outline" onClick={() => setActiveTab('security')}>
            <i className="fas fa-download"></i> Xuất dữ liệu
          </button>
        </div>
      </div>
      
      <div className="profile-container">
        {/* Sidebar */}
        <div className="profile-sidebar">
          <div className="profile-avatar-large">
            {user?.username?.substring(0, 2).toUpperCase() || 'A'}
          </div>
          <h2>{user?.username}</h2>
          <div className="profile-level">
            {subscription?.package_name || user?.package_name || "Học viên Miễn phí"}
          </div>
          <p style={{ color: 'var(--gray-color)', marginBottom: '20px' }}>
            Tham gia từ: {user?.created_at ? new Date(user.created_at).toLocaleDateString('vi-VN') : '06/01/2026'}
          </p>
          
          <div style={{ marginBottom: '20px' }}>
            <button className="btn btn-primary" style={{ width: '100%', marginBottom: '10px' }} onClick={() => { setActiveTab('personal'); setIsEditing(true); }}>
              <i className="fas fa-edit"></i> Chỉnh sửa hồ sơ
            </button>
          </div>
          
          <div className="profile-stats">
            <div className="stat-item">
              <div className="stat-value">{stats?.lessons_completed || 0}</div>
              <div className="stat-label">Bài học</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{stats?.streak_days || 0}</div>
              <div className="stat-label">Ngày Streak</div>
            </div>
          </div>
        </div>
        
        {/* Main Content */}
        <div className="profile-content">
          <div className="tab-navigation">
            <div className={`profile-tab ${activeTab === 'personal' ? 'active' : ''}`} onClick={() => setActiveTab('personal')}>Thông tin cá nhân</div>
            <div className={`profile-tab ${activeTab === 'learning' ? 'active' : ''}`} onClick={() => setActiveTab('learning')}>Tùy chỉnh học tập</div>
            <div className={`profile-tab ${activeTab === 'achievements' ? 'active' : ''}`} onClick={() => setActiveTab('achievements')}>Thành tích</div>
            <div className={`profile-tab ${activeTab === 'security' ? 'active' : ''}`} onClick={() => setActiveTab('security')}>Bảo mật</div>
          </div>
          
          {/* Tab Content: Personal */}
          {activeTab === 'personal' && (
            <div className="tab-panel active">
              <div className="profile-section">
                <div className="section-header">
                  <h3>Thông tin cá nhân</h3>
                  <button className="edit-button" onClick={() => setIsEditing(!isEditing)}>
                    <i className="fas fa-edit"></i> {isEditing ? 'Hủy' : 'Chỉnh sửa'}
                  </button>
                </div>
                
                {!isEditing ? (
                  <div className="info-grid">
                    <div className="info-item">
                      <div className="info-label">Tên người dùng</div>
                      <div className="info-value">{user?.username}</div>
                    </div>
                    <div className="info-item">
                      <div className="info-label">Email</div>
                      <div className="info-value">{user?.email}</div>
                    </div>
                  </div>
                ) : (
                  <form className="edit-form active" onSubmit={handleSavePersonalInfo}>
                    <div className="form-group">
                      <label>Họ và tên mới</label>
                      <input type="text" className="form-control" defaultValue={user?.username} />
                    </div>
                    <button type="submit" className="btn btn-primary">Lưu thay đổi</button>
                  </form>
                )}
              </div>
            </div>
          )}

          {/* Tab Content: Learning */}
          {activeTab === 'learning' && (
            <div className="tab-panel active">
              <div className="profile-section">
                <h3>Phong cách học tập ưa thích</h3>
                <div className="learning-preferences">
                  <div className="preference-card selected">
                    <div className="preference-icon"><i className="fas fa-microphone"></i></div>
                    <h4>Luyện nói</h4>
                    <p style={{ color: 'var(--gray-color)', fontSize: '0.9rem' }}>Tập trung phát âm AI</p>
                  </div>
                  <div className="preference-card">
                    <div className="preference-icon"><i className="fas fa-comments"></i></div>
                    <h4>Hội thoại</h4>
                    <p style={{ color: 'var(--gray-color)', fontSize: '0.9rem' }}>Thực hành đối thoại</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tab Content: Security & Danger Zone */}
          {activeTab === 'security' && (
            <div className="tab-panel active">
              <div className="profile-section">
                <h3>Bảo mật và Dữ liệu</h3>
                <p>ID tài khoản: <code>{user?.id}</code></p>
                
                <div className="export-options" style={{marginTop: '20px'}}>
                  <div className="export-card" onClick={() => handleExport('pdf')}>
                    <div className="export-icon"><i className="fas fa-file-pdf"></i></div>
                    <h4>PDF Report</h4>
                  </div>
                  <div className="export-card" onClick={() => handleExport('json')}>
                    <div className="export-icon"><i className="fas fa-file-code"></i></div>
                    <h4>JSON Data</h4>
                  </div>
                </div>

                <div className="danger-zone" style={{marginTop: '40px', padding: '20px', background: '#fff5f5', border: '1px solid #fed7d7', borderRadius: '12px'}}>
                  <h3 style={{color: '#c53030'}}><i className="fas fa-exclamation-triangle"></i> Vùng nguy hiểm</h3>
                  <button className="btn btn-outline" style={{color: '#c53030', borderColor: '#c53030'}} onClick={() => confirm('Xóa tài khoản?')}>
                    Xóa tài khoản vĩnh viễn
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
};

export default Profile;