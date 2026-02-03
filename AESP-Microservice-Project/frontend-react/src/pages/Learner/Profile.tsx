import React, { useState, useEffect } from 'react';
import './Profile.css';

interface UserProfile {
  id: string;
  username: string;
  email: string;
  role: string;
  package_name: string;
  user_level: string; // Thêm trường trình độ thật
  total_learning_points: number; // Thêm trường điểm thật
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
  const [newUsername, setNewUsername] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('token');
      const userInfoStr = localStorage.getItem("user_info");
      const userInfo = userInfoStr ? JSON.parse(userInfoStr) : null;
      const userId = userInfo?.id;

      if (!token || !userId) return;

      try {
        setLoading(true);
        
        // 1. Lấy thông tin cá nhân (bao gồm level và points)
        const userRes = await fetch(`http://localhost/api/users/me`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (userRes.ok) {
          const userData = await userRes.json();
          setUser(userData);
          setNewUsername(userData.username);
        }

        // 2. Lấy thống kê từ Analytics Service
        const statsRes = await fetch(`http://localhost/api/analytics/summary/${userId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (statsRes.ok) {
          const statsData = await statsRes.json();
          setStats(statsData);
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
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`http://localhost/api/users/profile/update`, {
        method: 'PUT',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: newUsername })
      });
      if (res.ok) {
        alert('Cập nhật thông tin thành công!');
        setIsEditing(false);
        window.location.reload(); // Reload để đồng bộ Header
      }
    } catch (error) {
      alert('Lỗi khi cập nhật thông tin.');
    }
  };

  // Logic hiển thị huy hiệu dựa trên thành tích thật
  const renderAchievements = () => {
    const achievements = [];
    if ((user?.total_learning_points || 0) > 1000) achievements.push({ icon: '🏆', title: 'Học giả chăm chỉ', desc: 'Đạt trên 1,000 điểm' });
    if ((stats?.accuracy_avg || 0) > 80) achievements.push({ icon: '🎯', title: 'Phát âm chuẩn', desc: 'Độ chính xác trung bình > 80%' });
    if ((stats?.streak_days || 0) >= 7) achievements.push({ icon: '🔥', title: 'Chiến binh bền bỉ', desc: 'Duy trì chuỗi 7 ngày' });

    return achievements.length > 0 ? (
      <div className="achievements-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
        {achievements.map((a, i) => (
          <div key={i} className="achievement-card" style={{ padding: '15px', background: '#f0f4ff', borderRadius: '12px', textAlign: 'center' }}>
            <div style={{ fontSize: '2rem' }}>{a.icon}</div>
            <h4 style={{ margin: '10px 0 5px' }}>{a.title}</h4>
            <p style={{ fontSize: '0.85rem', color: '#64748b' }}>{a.desc}</p>
          </div>
        ))}
      </div>
    ) : (
      <p style={{ textAlign: 'center', color: '#64748b' }}>Bạn chưa đạt được huy hiệu nào. Hãy luyện tập thêm!</p>
    );
  };

  if (loading) return <div className="loading" style={{marginTop: '100px', textAlign: 'center'}}>Đang tải hồ sơ AESP...</div>;

  return (
    <main className="container" style={{ marginTop: '100px' }}>
      <div className="profile-header">
        <h1>Hồ sơ học tập</h1>
        <button className="btn btn-outline" onClick={() => alert('Đang tạo báo cáo học tập...')}>
          <i className="fas fa-download"></i> Xuất dữ liệu
        </button>
      </div>
      
      <div className="profile-container">
        {/* Sidebar */}
        <div className="profile-sidebar">
          <div className="profile-avatar-large">
            {user?.username?.substring(0, 2).toUpperCase() || 'A'}
          </div>
          <h2>{user?.username}</h2>
          <div className="profile-level">
            {user?.user_level || "A1 (Beginner)"}
          </div>
          <div className="profile-points" style={{ color: '#4361ee', fontWeight: 'bold', margin: '10px 0' }}>
            <i className="fas fa-star"></i> {user?.total_learning_points?.toLocaleString() || 0} Điểm
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
            <div className={`profile-tab ${activeTab === 'personal' ? 'active' : ''}`} onClick={() => setActiveTab('personal')}>Thông tin</div>
            <div className={`profile-tab ${activeTab === 'achievements' ? 'active' : ''}`} onClick={() => setActiveTab('achievements')}>Thành tích</div>
            <div className={`profile-tab ${activeTab === 'security' ? 'active' : ''}`} onClick={() => setActiveTab('security')}>Bảo mật</div>
          </div>
          
          {activeTab === 'personal' && (
            <div className="tab-panel active">
              <div className="profile-section">
                <h3>Thông tin cá nhân</h3>
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
                    <button className="btn btn-primary" onClick={() => setIsEditing(true)}>Chỉnh sửa</button>
                  </div>
                ) : (
                  <form onSubmit={handleSavePersonalInfo}>
                    <div className="form-group">
                      <label>Tên mới</label>
                      <input type="text" className="form-control" value={newUsername} onChange={(e) => setNewUsername(e.target.value)} />
                    </div>
                    <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
                       <button type="submit" className="btn btn-primary">Lưu</button>
                       <button type="button" className="btn btn-outline" onClick={() => setIsEditing(false)}>Hủy</button>
                    </div>
                  </form>
                )}
              </div>
            </div>
          )}

          {activeTab === 'achievements' && (
            <div className="tab-panel active">
              <div className="profile-section">
                <h3>Huy hiệu vinh danh</h3>
                {renderAchievements()}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="tab-panel active">
              <div className="profile-section">
                <h3>Quản lý tài khoản</h3>
                <p>Mã định danh: <code>{user?.id}</code></p>
                <div className="danger-zone" style={{ marginTop: '20px', padding: '15px', background: '#fff5f5', border: '1px solid #fed7d7', borderRadius: '8px' }}>
                  <h4 style={{ color: '#c53030' }}>Vùng nguy hiểm</h4>
                  <button className="btn btn-outline" style={{ color: '#c53030', borderColor: '#c53030', marginTop: '10px' }}>
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