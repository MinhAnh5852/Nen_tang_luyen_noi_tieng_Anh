import React, { useState, useEffect } from 'react';
import './Leaderboard.css';

interface LeaderboardUser {
  rank: number;
  username: string;
  points: number;
  level: string;
  streak: number;
}

const Leaderboard: React.FC = () => {
  const [users, setUsers] = useState<LeaderboardUser[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/users/leaderboard')
      .then(res => res.json())
      .then(data => {
        setUsers(data);
        setLoading(false);
      })
      .catch(err => console.error("Lỗi nạp bảng xếp hạng:", err));
  }, []);

  if (loading) return <div className="container" style={{marginTop: '100px', textAlign: 'center'}}>Đang tải bảng vàng AESP...</div>;

  return (
    <div className="container" style={{ marginTop: '100px' }}>
      <div className="leaderboard-header" style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h1><i className="fas fa-trophy" style={{ color: '#f59e0b' }}></i> Bảng Xếp Hạng Học Viên</h1>
        <p>Vinh danh những nỗ lực luyện tập không ngừng nghỉ</p>
      </div>

      <div className="leaderboard-card" style={{ background: 'white', padding: '30px', borderRadius: '15px', boxShadow: '0 10px 15px rgba(0,0,0,0.05)' }}>
        <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '2px solid #eee' }}>
              <th style={{ padding: '15px' }}>Hạng</th>
              <th style={{ padding: '15px' }}>Học viên</th>
              <th style={{ padding: '15px' }}>Trình độ</th>
              <th style={{ padding: '15px' }}>Chuỗi ngày</th>
              <th style={{ padding: '15px' }}>Tổng điểm</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.rank} style={{ borderBottom: '1px solid #f9f9f9', backgroundColor: user.rank <= 3 ? '#fffbeb' : 'transparent' }}>
                <td style={{ padding: '15px', fontWeight: 'bold' }}>
                  {user.rank === 1 ? '🥇' : user.rank === 2 ? '🥈' : user.rank === 3 ? '🥉' : user.rank}
                </td>
                <td style={{ padding: '15px' }}>{user.username}</td>
                <td style={{ padding: '15px' }}><span className="status-badge status-active">{user.level}</span></td>
                <td style={{ padding: '15px' }}><i className="fas fa-fire" style={{ color: '#ef4444' }}></i> {user.streak}</td>
                <td style={{ padding: '15px', fontWeight: 'bold', color: '#4361ee' }}>{user.points.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Leaderboard;