import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Assessment.css';

const testSentences = [
  { level: 'A1', text: "Hello, my name is John and I am a student." },
  { level: 'A2', text: "I enjoy learning English because it helps me in my career." },
  { level: 'B1', text: "Artificial intelligence is transforming the way we communicate and learn globally." }
];

const Assessment: React.FC = () => {
  const [step, setStep] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [scores, setScores] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Khởi tạo Speech Recognition
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognition = SpeechRecognition ? new SpeechRecognition() : null;
  if (recognition) recognition.lang = 'en-US';

  const handleStart = () => {
    if (!recognition) {
      alert("Trình duyệt của bạn không hỗ trợ nhận diện giọng nói.");
      return;
    }
    setIsRecording(true);
    recognition.start();

    recognition.onresult = async (event: any) => {
      const transcript = event.results[0][0].transcript;
      recognition.stop();
      setIsRecording(false);
      await evaluateSpeech(transcript);
    };

    recognition.onerror = () => {
      setIsRecording(false);
      alert("Lỗi ghi âm, vui lòng thử lại.");
    };
  };

  const evaluateSpeech = async (text: string) => {
    setLoading(true);
    try {
      // Gửi bài nói sang AI Core để chấm điểm
      const res = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text, 
          topic: 'Assessment',
          user_id: JSON.parse(localStorage.getItem('user_info') || '{}').id 
        })
      });
      const data = await res.json();
      
      // Độ chính xác (accuracy) mặc định 50 nếu API không trả về
      const currentScore = data.accuracy || 50;
      const newScores = [...scores, currentScore];
      setScores(newScores);

      if (step < testSentences.length - 1) {
        setStep(step + 1);
      } else {
        await finishAssessment(newScores);
      }
    } catch (e) {
      console.error("Lỗi đánh giá:", e);
      alert("Không thể kết nối với AI Service.");
    } finally {
      setLoading(false);
    }
  };

  const finishAssessment = async (allScores: number[]) => {
    const avg = allScores.reduce((a, b) => a + b, 0) / allScores.length;
    let level = 'A1 (Beginner)';
    if (avg > 75) level = 'B1 (Intermediate)';
    else if (avg > 50) level = 'A2 (Elementary)';

    const token = localStorage.getItem('token');
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');

    try {
      // 1. Cập nhật trình độ vào User Service (Sử dụng endpoint update-role bạn đã có)
      const res = await fetch('/api/users/auth/update-level', {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify({ 
          id: userInfo.id,
          role: 'learner',
          user_level: level 
        })
      });

      if (res.ok) {
        localStorage.setItem('assessment_scores', JSON.stringify(allScores));
        // 2. QUAN TRỌNG NHẤT: Cập nhật lại localStorage để mở khóa App.tsx
        const updatedUserInfo = { ...userInfo, level: level };
        localStorage.setItem('user_info', JSON.stringify(updatedUserInfo));

        alert(`Chúc mừng! AI đánh giá trình độ của bạn là: ${level}.`);
        
        // 3. Chuyển hướng và tải lại để cập nhật Header/Sidebar
        navigate('/dashboard', { replace: true });
        window.location.reload(); 
      }
    } catch (e) {
      console.error("Lỗi cập nhật profile:", e);
    }
  };

  return (
    <div className="assessment-container">
      <div className="assessment-card">
        <div className="ai-icon">
          <i className="fa-solid fa-robot-astromech"></i>
        </div>
        <h2>Kiểm tra năng lực đầu vào</h2>
        <p className="subtitle">AI sẽ phân tích phát âm để xếp lớp phù hợp cho bạn.</p>
        
        <div className="progress-bar-container">
            <div className="progress-fill" style={{ width: `${((step + 1) / testSentences.length) * 100}%` }}></div>
        </div>
        <p className="progress-text">Câu hỏi {step + 1} / {testSentences.length}</p>
        
        <div className="sentence-box">
          <p className="sentence-label">Hãy đọc to câu sau:</p>
          <p className="sentence-text">"{testSentences[step].text}"</p>
        </div>

        <button 
          className={`mic-btn ${isRecording ? 'recording' : ''}`} 
          onClick={handleStart}
          disabled={loading}
        >
          <div className="mic-circle">
            <i className={`fas fa-${isRecording ? 'stop' : 'microphone'}`}></i>
          </div>
          <span>{isRecording ? 'AI đang lắng nghe...' : 'Nhấn để ghi âm'}</span>
        </button>
        
        {loading && (
            <div className="loading-ai">
                <i className="fa-solid fa-spinner fa-spin"></i>
                <p>AI đang phân tích giọng nói...</p>
            </div>
        )}
      </div>
    </div>
  );
};

export default Assessment;