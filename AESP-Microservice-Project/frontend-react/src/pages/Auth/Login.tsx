// import React, { useState } from 'react';
// import { initializeApp } from "firebase/app";
// import { getAuth, signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider, signOut } from "firebase/auth";
// import './Auth.css';

// // Cấu hình Firebase giữ nguyên từ file HTML của bạn
// const firebaseConfig = {
//   apiKey: "AIzaSyAR_mMEOLmcQeewl7ECynfLe-0ymFiqx9g",
//   authDomain: "pj-luyen-noi-tieng-anh.firebaseapp.com",
//   projectId: "pj-luyen-noi-tieng-anh",
//   storageBucket: "pj-luyen-noi-tieng-anh.firebasestorage.app",
//   messagingSenderId: "835156032196",
//   appId: "1:835156032196:web:b8920adabf15ace0bbe791"
// };

// const app = initializeApp(firebaseConfig);
// const auth = getAuth(app);

// const Login: React.FC = () => {
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [error, setError] = useState('');
//   const [loading, setLoading] = useState(false);

//   const syncAndRedirect = async (firebaseUser: any) => {
//     setLoading(true);
//     setError('');

//     try {
//       // Gọi qua API Gateway (Nginx) để đồng bộ vào MySQL
//       const response = await fetch('/api/users/auth/login-firebase', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ 
//           email: firebaseUser.email.toLowerCase().trim(),
//           username: firebaseUser.displayName || firebaseUser.email.split('@')[0]
//         })
//       });

//       const data = await response.json();
//       if (!response.ok) throw new Error(data.error || "Lỗi đồng bộ dữ liệu!");

//       // Lưu trữ thông tin đăng nhập vào LocalStorage
//       localStorage.setItem('token', data.token);
//       localStorage.setItem('user_info', JSON.stringify(data.user));
//       localStorage.setItem('user_role', data.user.role.toLowerCase());

//       // Chuyển hướng theo vai trò
//       const role = data.user.role.toLowerCase();
//       if (role === 'admin') window.location.href = '/admin';
//       else if (role === 'mentor') window.location.href = '/mentor';
//       else window.location.href = '/dashboard'; 

//     } catch (err: any) {
//       setError("❌ " + err.message);
//       await signOut(auth);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleEmailLogin = async (e: React.FormEvent) => {
//     e.preventDefault();
//     try {
//       const result = await signInWithEmailAndPassword(auth, email, password);
//       await syncAndRedirect(result.user);
//     } catch (err) {
//       setError("Email hoặc mật khẩu không đúng!");
//     }
//   };

//   const handleGoogleLogin = async () => {
//     try {
//       const provider = new GoogleAuthProvider();
//       provider.setCustomParameters({ prompt: 'select_account' });
//       const result = await signInWithPopup(auth, provider);
//       await syncAndRedirect(result.user);
//     } catch (err: any) {
//       if (err.code !== 'auth/popup-closed-by-user') {
//         setError("Lỗi Google: " + err.message);
//       }
//     }
//   };

//   return (
//     <div className="auth-container">
//       <div className="auth-card">
//         <div className="auth-header">
//           <h2>Đăng nhập</h2>
//           <p>Chào mừng trở lại! Vui lòng đăng nhập để tiếp tục</p>
//         </div>

//         <form className="auth-form" onSubmit={handleEmailLogin}>
//           <div className="form-group">
//             <label>Email</label>
//             <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Nhập địa chỉ email" required />
//           </div>

//           <div className="form-group">
//             <label>Mật khẩu</label>
//             <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Nhập mật khẩu" required />
//           </div>

//           {error && <div className="error-message" style={{display: 'block'}}>{error}</div>}

//           <button type="submit" className={`btn btn-primary ${loading ? 'btn-loading' : ''}`} style={{ width: '100%', padding: '15px' }}>
//             {loading ? "⏳ Đang đồng bộ..." : "Đăng nhập"}
//           </button>

//           <div className="divider"><span>Hoặc đăng nhập với</span></div>

//           <div className="social-login">
//             <button type="button" className="social-btn" onClick={handleGoogleLogin}>
//               <i className="fab fa-google"></i><span> Google</span>
//             </button>
//           </div>

//           <div className="form-footer">
//             <p>Chưa có tài khoản? <a href="/register">Đăng ký ngay</a></p>
//           </div>
//         </form>
//       </div>
//     </div>
//   );
// };

// export default Login;
import React, { useState } from 'react';
import { initializeApp } from "firebase/app";
import { getAuth, signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider, signOut } from "firebase/auth";
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

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const syncAndRedirect = async (firebaseUser: any) => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/users/auth/login-firebase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: firebaseUser.email.toLowerCase().trim(),
          username: firebaseUser.displayName || firebaseUser.email.split('@')[0]
        })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Lỗi đồng bộ dữ liệu!");

      // 🔥 SỬA LỖI TẠI ĐÂY: Dùng Optional Chaining (?.) và Default Value
      const user = data.user;
      const token = data.token;

      // Nếu không có user hoặc role, gán giá trị mặc định để không bị lỗi toLowerCase()
      const role = (user?.role || 'learner').toLowerCase();
      const status = (user?.status || 'active').toLowerCase();

      // Kiểm tra chặn Mentor chưa duyệt
      if (role === 'mentor' && status === 'pending') {
        await signOut(auth);
        setError("🔒 Tài khoản Cố vấn của bạn đang chờ phê duyệt. Vui lòng quay lại sau!");
        setLoading(false);
        return;
      }

      // Lưu trữ an toàn
      localStorage.setItem('token', token);
      localStorage.setItem('user_info', JSON.stringify(user));
      localStorage.setItem('user_role', role);

      // Chuyển hướng dựa trên role đã xử lý
      if (role === 'admin') window.location.href = '/admin';
      else if (role === 'mentor') window.location.href = '/mentor';
      else window.location.href = '/dashboard'; 

    } catch (err: any) {
      console.error("Login Error:", err);
      setError("❌ " + err.message);
      await signOut(auth);
    } finally {
      setLoading(false);
    }
  };

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      await syncAndRedirect(result.user);
    } catch (err) {
      setError("Email hoặc mật khẩu không chính xác!");
    }
  };

  const handleGoogleLogin = async () => {
    try {
      const provider = new GoogleAuthProvider();
      provider.setCustomParameters({ prompt: 'select_account' });
      const result = await signInWithPopup(auth, provider);
      await syncAndRedirect(result.user);
    } catch (err: any) {
      if (err.code !== 'auth/popup-closed-by-user') {
        setError("Lỗi Google: " + err.message);
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Đăng nhập AESP</h2>
          <p>Luyện nói tiếng Anh cùng AI và Mentor</p>
        </div>

        <form className="auth-form" onSubmit={handleEmailLogin}>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="example@gmail.com" required />
          </div>

          <div className="form-group">
            <label>Mật khẩu</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Nhập mật khẩu" required />
          </div>

          {error && (
            <div className="error-message" style={{
              display: 'block', color: '#ef4444', backgroundColor: '#fef2f2', 
              padding: '10px', borderRadius: '5px', marginBottom: '15px', fontSize: '14px'
            }}>
              {error}
            </div>
          )}

          <button type="submit" disabled={loading} className={`btn btn-primary ${loading ? 'btn-loading' : ''}`} style={{ width: '100%', padding: '15px' }}>
            {loading ? "⏳ Đang xác thực..." : "Đăng nhập ngay"}
          </button>

          <div className="divider"><span>Hoặc</span></div>

          <div className="social-login">
            <button type="button" className="social-btn" onClick={handleGoogleLogin} style={{width: '100%', display: 'flex', justifyContent: 'center', gap: '10px', alignItems: 'center'}}>
              <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="google" width="18"/>
              <span>Tiếp tục với Google</span>
            </button>
          </div>

          <div className="form-footer">
            <p>Thành viên mới? <a href="/register">Đăng ký tại đây</a></p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;