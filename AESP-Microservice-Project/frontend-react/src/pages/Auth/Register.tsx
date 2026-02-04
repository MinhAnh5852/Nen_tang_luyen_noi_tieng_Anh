import React, { useState } from 'react';
import { initializeApp } from "firebase/app";
import { getAuth, createUserWithEmailAndPassword } from "firebase/auth";
import './Auth.css';

const firebaseConfig = {
  apiKey: "AIzaSyAR_mMEOLmcQeewl7ECynfLe-0ymFiqx9g",
  authDomain: "pj-luyen-noi-tieng-anh.firebaseapp.com",
  projectId: "pj-luyen-noi-tieng-anh",
  storageBucket: "pj-luyen-noi-tieng-anh.firebasestorage.app",
  messagingSenderId: "835156032196",
  appId: "1:835156032196:web:b8920adabf15ace0bbe791"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const Register: React.FC = () => {
  const [role, setRole] = useState<'learner' | 'mentor'>('learner'); // Đổi sang chữ thường để khớp DB
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // --- BƯỚC 1: TẠO USER TRÊN FIREBASE ---
      const userCredential = await createUserWithEmailAndPassword(auth, formData.email, formData.password);
      const firebaseUser = userCredential.user;

      // --- BƯỚC 2: ĐỒNG BỘ VÀO MYSQL QUA API GATEWAY ---
      // SỬA: Route đúng phải có thêm /auth/ trước register
      const syncResponse = await fetch('/api/users/auth/register', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: firebaseUser.email,
          username: formData.name,
          password: formData.password, // Gửi để Backend hash và lưu MySQL
          role: role,
          firebase_uid: firebaseUser.uid
        })
      });

      const result = await syncResponse.json();

      if (!syncResponse.ok) {
        throw new Error(result.message || "Lưu MySQL thất bại");
      }

      // --- BƯỚC 3: THÔNG BÁO VÀ CHUYỂN TRANG ---
      if (role === 'mentor') {
        alert("🎉 Đăng ký thành công! Hồ sơ Mentor của bạn đang chờ phê duyệt.");
      } else {
        alert("🎉 Đăng ký thành công! Chào mừng bạn.");
      }
      
      window.location.href = '/login';

    } catch (err: any) {
      let msg = err.message;
      if (msg.includes("email-already-in-use")) msg = "Email này đã được sử dụng!";
      else if (msg.includes("weak-password")) msg = "Mật khẩu nên có ít nhất 6 ký tự!";
      setError("❌ " + msg);
      console.error("Lỗi đăng ký:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Đăng ký tài khoản AESP</h2>
          <p>Tham gia cộng đồng luyện nói tiếng Anh với AI</p>
        </div>

        <form className="auth-form" onSubmit={handleRegister}>
          <div className="role-selection" style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <div 
              className={`role-option ${role === 'learner' ? 'selected' : ''}`} 
              onClick={() => setRole('learner')}
              style={{ 
                cursor: 'pointer', padding: '15px', flex: 1, textAlign: 'center',
                border: role === 'learner' ? '2px solid #2563eb' : '1px solid #ddd',
                borderRadius: '8px', background: role === 'learner' ? '#eff6ff' : '#fff'
              }}
            >
              <i className="fas fa-user-graduate"></i>
              <h4>Học viên</h4>
            </div>
            <div 
              className={`role-option ${role === 'mentor' ? 'selected' : ''}`} 
              onClick={() => setRole('mentor')}
              style={{ 
                cursor: 'pointer', padding: '15px', flex: 1, textAlign: 'center',
                border: role === 'mentor' ? '2px solid #ea580c' : '1px solid #ddd',
                borderRadius: '8px', background: role === 'mentor' ? '#fff7ed' : '#fff'
              }}
            >
              <i className="fas fa-chalkboard-teacher"></i>
              <h4>Mentor</h4>
            </div>
          </div>

          <div className="form-group">
            <label>Họ và tên</label>
            <input 
              type="text" 
              placeholder="Nhập tên hiển thị" 
              required 
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input 
              type="email" 
              placeholder="Nhập email của bạn" 
              required 
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
          </div>

          <div className="form-group">
            <label>Mật khẩu</label>
            <input 
              type="password" 
              placeholder="Tối thiểu 6 ký tự" 
              required 
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>

          {error && <div className="error-message" style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}

          <button 
            type="submit" 
            className={`btn btn-primary ${loading ? 'btn-loading' : ''}`} 
            style={{ 
              width: '100%', padding: '15px', marginTop: '10px',
              backgroundColor: role === 'mentor' ? '#ea580c' : '#2563eb',
              color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold'
            }}
          >
            {loading ? "Đang xử lý..." : `Đăng ký làm ${role === 'mentor' ? 'Mentor' : 'Học viên'}`}
          </button>

          <div className="form-footer" style={{ textAlign: 'center', marginTop: '15px' }}>
            <p>Đã có tài khoản? <a href="/login">Đăng nhập ngay</a></p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;