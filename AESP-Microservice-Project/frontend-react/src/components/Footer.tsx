import React from 'react';
import './Footer.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMapMarkerAlt, faPhone, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { faFacebookF, faTwitter, faInstagram, faYoutube } from '@fortawesome/free-brands-svg-icons';

const Footer: React.FC = () => {
  return (
    <footer className="footer-container">
      <div className="container">
        <div className="footer-content">
          <div className="footer-column">
            <h3>AESP</h3>
            <p>
              Nền tảng luyện nói tiếng Anh với AI tiên tiến, giúp bạn cải thiện kỹ năng
              giao tiếp một cách hiệu quả và cá nhân hóa.
            </p>
            <div className="social-icons">
              <a href="#"><FontAwesomeIcon icon={faFacebookF} /></a>
              <a href="#"><FontAwesomeIcon icon={faTwitter} /></a>
              <a href="#"><FontAwesomeIcon icon={faInstagram} /></a>
              <a href="#"><FontAwesomeIcon icon={faYoutube} /></a>
            </div>
          </div>

          <div className="footer-column">
            <h3>Tính năng</h3>
            <a href="#">Luyện nói với AI</a>
            <a href="#">Phân tích phát âm</a>
            <a href="#">Hội thoại tương tác</a>
            <a href="#">Theo dõi tiến độ</a>
          </div>

          <div className="footer-column">
            <h3>Tài nguyên</h3>
            <a href="#">Tài liệu học tập</a>
            <a href="#">Blog</a>
            <a href="#">Câu hỏi thường gặp</a>
            <a href="#">Hỗ trợ</a>
          </div>

          <div className="footer-column">
            <h3>Liên hệ</h3>
            <p><FontAwesomeIcon icon={faMapMarkerAlt} /> 70 Tô Ký, Quận 12, TP.HCM</p>
            <p><FontAwesomeIcon icon={faPhone} /> (028) 2345 9786</p>
            <p><FontAwesomeIcon icon={faEnvelope} /> support@aienglish.com</p>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; 2026 AESP. Tất cả các quyền được bảo lưu.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;