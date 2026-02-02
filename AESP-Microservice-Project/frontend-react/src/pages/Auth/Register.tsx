import React, { useState } from 'react';
import { initializeApp } from "firebase/app";
import { getAuth, createUserWithEmailAndPassword } from "firebase/auth";
import './Auth.css';

// Cấu hình Firebase đồng bộ với trang Login
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
  const [role, setRole] = useState<'LEARNER' | 'MENTOR'>('LEARNER');
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
      // Lưu ý: Chúng ta gọi qua Gateway cổng 80 để trỏ vào user-service
      const syncResponse = await fetch('/api/users/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: firebaseUser.email,
          username: formData.name,
          role: role,
          firebase_uid: firebaseUser.uid
        })
      });

      if (!syncResponse.ok) {
        console.warn("Lưu MySQL thất bại nhưng Firebase đã tạo xong.");
      }

      // --- BƯỚC 3: LƯU LOCAL VÀ CHUYỂN TRANG ---
      alert("🎉 Đăng ký thành công!");
      window.location.href = '/login';

    } catch (err: any) {
      let msg = err.message;
      if (msg.includes("email-already-in-use")) msg = "Email này đã được sử dụng!";
      else if (msg.includes("weak-password")) msg = "Mật khẩu nên có ít nhất 6 ký tự!";
      setError("❌ " + msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Đăng ký tài khoản</h2>
          <p>Tạo tài khoản để bắt đầu luyện nói tiếng Anh với AI</p>
        </div>

        <form className="auth-form" onSubmit={handleRegister}>
          {/* Chọn vai trò */}
          <div className="role-selection" style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <div 
              className={`role-option ${role === 'LEARNER' ? 'selected' : ''}`} 
              onClick={() => setRole('LEARNER')}
              style={{ cursor: 'pointer', padding: '15px', border: '1px solid #ddd', borderRadius: '8px', flex: 1, textAlign: 'center' }}
            >
              <i className="fas fa-user-graduate"></i>
              <h4>Học viên</h4>
            </div>
            <div 
              className={`role-option ${role === 'MENTOR' ? 'selected' : ''}`} 
              onClick={() => setRole('MENTOR')}
              style={{ cursor: 'pointer', padding: '15px', border: '1px solid #ddd', borderRadius: '8px', flex: 1, textAlign: 'center' }}
            >
              <i className="fas fa-chalkboard-teacher"></i>
              <h4>Mentor</h4>
            </div>
          </div>

          <div className="form-group">
            <label>Họ và tên</label>
            <input 
              type="text" 
              placeholder="Nhập họ và tên" 
              required 
              onChange={(e) => setFormData({...formData, name: e.target.value})}
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input 
              type="email" 
              placeholder="Nhập địa chỉ email" 
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

          {error && <div className="error-message" style={{ display: 'block' }}>{error}</div>}

          <button type="submit" className={`btn btn-primary ${loading ? 'btn-loading' : ''}`} style={{ width: '100%', padding: '15px', marginTop: '10px' }}>
            {loading ? "Đang xử lý..." : "Đăng ký tài khoản"}
          </button>

          <div className="form-footer">
            <p>Đã có tài khoản? <a href="/login">Đăng nhập ngay</a></p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;