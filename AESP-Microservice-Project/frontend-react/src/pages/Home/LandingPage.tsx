import React from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage: React.FC = () => {
  return (
    <div className="landing-wrapper">
      {/* 1. HERO SECTION - Gây ấn tượng đầu tiên */}
      <section className="hero-section">
        <div className="container hero-container">
          <div className="hero-content">
            <h1>Luyện nói tiếng Anh với <br /><span>AI thông minh</span></h1>
            <p>Phá bỏ rào cản ngôn ngữ với công nghệ AI hàng đầu. Luyện phản xạ, chỉnh phát âm và tự tin giao tiếp chỉ sau 30 ngày.</p>
            <div className="cta-group">
              <Link to="/register" className="btn btn-primary btn-lg">Bắt đầu miễn phí</Link>
              <Link to="/login" className="btn btn-outline btn-lg">Đăng nhập</Link>
            </div>
          </div>
          <div className="hero-image">
            <i className="fas fa-robot"></i>
          </div>
        </div>
      </section>

      {/* 2. FEATURES SECTION - Tại sao chọn AESP? */}
      <section id="features" className="features-section">
        <div className="container">
          <h2 className="section-title">Tính năng đột phá</h2>
          <div className="features-grid">
            <div className="feature-card">
              <i className="fas fa-microphone-alt"></i>
              <h3>Nhận diện giọng nói</h3>
              <p>Phân tích chi tiết từng âm tiết, giúp bạn sửa lỗi phát âm ngay lập tức nhờ AI Core Service.</p>
            </div>
            <div className="feature-card">
              <i className="fas fa-comments"></i>
              <h3>Hội thoại không giới hạn</h3>
              <p>Trò chuyện về bất kỳ chủ đề nào bạn thích với "gia sư AI" hỗ trợ 24/7.</p>
            </div>
            <div className="feature-card">
              <i className="fas fa-chart-line"></i>
              <h3>Theo dõi tiến độ</h3>
              <p>Biểu đồ trực quan giúp bạn thấy rõ sự thăng tiến qua từng ngày tập luyện.</p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. PRICING SECTION - Các gói dịch vụ */}
      <section id="pricing" className="pricing-section">
        <div className="container">
          <h2 className="section-title">Chọn lộ trình của bạn</h2>
          <div className="pricing-grid">
            <div className="price-card">
              <h4>Gói Miễn Phí</h4>
              <div className="price">0đ</div>
              <ul>
                <li><i className="fas fa-check"></i> 10 phút luyện tập mỗi ngày</li>
                <li><i className="fas fa-check"></i> Chủ đề giao tiếp cơ bản</li>
              </ul>
              <Link to="/register" className="btn btn-outline">Thử ngay</Link>
            </div>
            <div className="price-card recommended">
              <div className="badge">Phổ biến nhất</div>
              <h4>Gói Pro AI</h4>
              <div className="price">500.000đ<span>/30 ngày</span></div>
              <ul>
                <li><i className="fas fa-check"></i> Không giới hạn thời gian</li>
                <li><i className="fas fa-check"></i> 100+ chủ đề nâng cao</li>
                <li><i className="fas fa-check"></i> Hỗ trợ từ Mentor chuyên nghiệp</li>
              </ul>
              <Link to="/register" className="btn btn-primary">Nâng cấp ngay</Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;