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
  const [selectedTopic, setSelectedTopic] = useState("Hàng ngày");
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Khởi tạo Speech Recognition
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;

  if (recognition) {
    recognition.lang = 'en-US';
    recognition.interimResults = false;
  }

  useEffect(() => {
    if (!recognition) return;

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      handleSendMessage(transcript);
    };

    recognition.onend = () => setIsListening(false);

    recognition.onerror = () => {
      setStatus("Không nghe rõ, vui lòng thử lại.");
      setIsListening(false);
    };
  }, [selectedTopic]);

  // Tự động cuộn xuống cuối chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toggleMic = () => {
    if (!recognition) {
      alert("Trình duyệt không hỗ trợ nhận diện giọng nói.");
      return;
    }
    if (!isListening) {
      recognition.start();
      setIsListening(true);
      setStatus("Đang lắng nghe... Hãy nói tiếng Anh");
    } else {
      recognition.stop();
      setIsListening(false);
    }
  };

  const handleSendMessage = async (text: string) => {
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setStatus("AI đang phân tích...");

    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text, 
          topic: selectedTopic,
          user_id: localStorage.getItem('user_id') || 'admin-001' 
        })
      });

      const data = await response.json();
      setMessages(prev => [...prev, { 
        sender: 'ai', 
        text: data.reply, 
        accuracy: data.accuracy, 
        correction: data.correction 
      }]);
      setStatus(`Hoàn tất! Độ chính xác: ${data.accuracy}%`);
    } catch (e) {
      setMessages(prev => [...prev, { sender: 'ai', text: "Rất tiếc, tôi gặp lỗi kết nối." }]);
      setStatus("Lỗi kết nối.");
    }
  };

  return (
    <main className="container">
      <div className="practice-header" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
        <h1>AESP AI Speaking</h1>
        <button className="btn-outline" onClick={() => window.location.reload()}>Làm mới</button>
      </div>

      <div className="content-card" style={{ background: 'white', padding: '20px', borderRadius: '12px', margin: '20px 0' }}>
        <h3>1. Chọn chủ đề hội thoại</h3>
        <div className="topic-grid" style={{ display: 'flex', gap: '10px' }}>
          {['Công việc', 'Du lịch', 'Hàng ngày', 'Sức khỏe'].map(topic => (
            <div 
              key={topic}
              className={`topic-card ${selectedTopic === topic ? 'selected' : ''}`}
              onClick={() => setSelectedTopic(topic)}
              style={{ padding: '10px 20px', border: '1px solid #ccc', borderRadius: '8px', cursor: 'pointer' }}
            >
              {topic}
            </div>
          ))}
        </div>
      </div>

      <div className="practice-area">
        <div className="conversation-box">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.sender}`}>
              <div className="message-content">
                <strong>{msg.sender === 'ai' ? 'AI' : 'Bạn'}:</strong> {msg.text}
              </div>
              {msg.accuracy !== undefined && (
                <div className="feedback-note">
                  <i className="fas fa-check-circle"></i> Accuracy: {msg.accuracy}% <br />
                  <i className="fas fa-magic"></i> Suggestion: {msg.correction}
                </div>
              )}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div className="controls-container" style={{ textAlign: 'center' }}>
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