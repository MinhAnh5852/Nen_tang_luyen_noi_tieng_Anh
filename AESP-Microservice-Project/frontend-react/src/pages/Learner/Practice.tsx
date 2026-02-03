import React, { useState, useEffect, useRef } from 'react';
import './Practice.css';

interface Message {
  sender: 'ai' | 'user';
  text: string;
  accuracy?: number;
  correction?: string;
}

const Practice: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'ai', text: "Hello! I'm your AESP assistant. Please select a topic and click the microphone to start our conversation." }
  ]);
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState("Nhấn mic để bắt đầu nói");
  const [selectedTopic, setSelectedTopic] = useState("Daily Life");
  const [userLevel, setUserLevel] = useState("A1");
  
  // Ref để quản lý khung chat và đối tượng nhận diện ổn định
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // 1. Tự động nạp lịch sử và khởi tạo Micro khi vào trang
  useEffect(() => {
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
    if (userInfo.user_level) setUserLevel(userInfo.user_level);

    // Lấy lịch sử cũ (Nếu bạn đã thêm endpoint /api/ai/history ở Backend)
    const fetchHistory = async () => {
      if (userInfo.id) {
        try {
          const response = await fetch(`/api/ai/history/${userInfo.id}`);
          const data = await response.json();
          if (Array.isArray(data) && data.length > 0) setMessages(data);
        } catch (e) { console.error("Lỗi nạp lịch sử:", e); }
      }
    };
    fetchHistory();

    // Khởi tạo SpeechRecognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.continuous = false; // Ngắt sau mỗi câu để gửi API xử lý

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript.trim()) handleSendMessage(transcript);
      };

      recognitionRef.current.onend = () => setIsListening(false);
      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech Recognition Error:", event.error);
        setIsListening(false);
        setStatus("Không nghe rõ, vui lòng thử lại.");
      };
    }
  }, []);

  // 2. Tự động cuộn khung chat nội bộ
  useEffect(() => {
    if (messages.length > 1 && chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages]);

  const toggleMic = () => {
    if (!recognitionRef.current) return alert("Trình duyệt không hỗ trợ nhận diện giọng nói.");

    if (!isListening) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        setStatus(`Đang lắng nghe chủ đề: ${selectedTopic}...`);
      } catch (e) { recognitionRef.current.stop(); }
    } else {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    const token = localStorage.getItem('token');
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
    
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setStatus("AI đang phân tích...");

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text, 
          topic: selectedTopic, // ✅ Đảm bảo chủ đề hiện tại được gửi đi
          user_id: userInfo.id,
          level: userLevel 
        })
      });

      const data = await response.json();
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: data.reply, 
        accuracy: data.accuracy, 
        correction: data.correction 
      }]);

      // Cập nhật tiến độ vào User Service
      if (data.accuracy > 50) {
        await fetch('/api/users/profile/update-progress', {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json' 
          },
          body: JSON.stringify({ accuracy: data.accuracy })
        });
      }
      setStatus(`Độ chính xác: ${data.accuracy}%`);
    } catch (e) {
      setStatus("Lỗi kết nối.");
    }
  };

  return (
    <main className="container">
      <div className="practice-header" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
        <h1>AESP AI Speaking</h1>
        <div className="user-level-tag" style={{ background: '#e0e7ff', color: '#4361ee', padding: '5px 15px', borderRadius: '20px', fontWeight: 'bold' }}>
          Trình độ: {userLevel}
        </div>
      </div>

      <div className="content-card" style={{ background: 'white', padding: '20px', borderRadius: '12px', margin: '20px 0' }}>
        <h3>1. Chọn chủ đề hội thoại</h3>
        <div className="topic-grid" style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {['Work', 'Travel', 'Daily Life', 'Health'].map(topic => (
            <div 
              key={topic}
              className={`topic-card ${selectedTopic === topic ? 'selected' : ''}`}
              onClick={() => setSelectedTopic(topic)}
              style={{ 
                padding: '10px 20px', 
                border: selectedTopic === topic ? '2px solid #4361ee' : '1px solid #ccc', 
                background: selectedTopic === topic ? '#f0f4ff' : 'white',
                borderRadius: '8px', 
                cursor: 'pointer' 
              }}
            >
              {topic}
            </div>
          ))}
        </div>
      </div>

      <div className="practice-area">
        {/* Khung chat có thanh cuộn nội bộ */}
        <div className="conversation-box" ref={chatContainerRef} style={{ height: '400px', overflowY: 'auto' }}>
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.sender}`}>
              <div className="message-content">
                <strong>{msg.sender === 'ai' ? 'AI' : 'Bạn'}:</strong> {msg.text}
              </div>
              {msg.accuracy !== undefined && (
                <div className="feedback-note">
                  📊 Điểm: {msg.accuracy}% | 💡 Gợi ý: {msg.correction}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="controls-container" style={{ textAlign: 'center', marginTop: '20px' }}>
          <button className={`recording-button ${isListening ? 'recording' : ''}`} onClick={toggleMic}>
            <i className={`fas fa-${isListening ? 'stop' : 'microphone'}`}></i>
          </button>
          <p>{status}</p>
        </div>
      </div>
    </main>
  );
};

export default Practice;