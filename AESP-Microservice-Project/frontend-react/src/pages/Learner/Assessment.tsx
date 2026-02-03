import React, { useState } from 'react'; // Xóa useEffect đi là xong
import { useNavigate } from 'react-router-dom';
import './Assessment.css'; // Sẽ tạo ở bước sau

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

  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';

  const handleStart = () => {
    setIsRecording(true);
    recognition.start();
  };

  recognition.onresult = async (event: any) => {
    const transcript = event.results[0][0].transcript;
    recognition.stop();
    setIsRecording(false);
    await evaluateSpeech(transcript);
  };

  const evaluateSpeech = async (text: string) => {
    setLoading(true);
    try {
      // Gọi AI Core Service để chấm điểm (Sử dụng API chat hiện có để demo logic)
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
      setScores([...scores, data.accuracy]);

      if (step < testSentences.length - 1) {
        setStep(step + 1);
      } else {
        await finishAssessment([...scores, data.accuracy]);
      }
    } catch (e) {
      console.error("Lỗi đánh giá:", e);
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
    // Cập nhật trình độ vào User Service
    await fetch('/api/users/profile/update-level', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify({ user_level: level })
    });

    alert(`Chúc mừng! Trình độ của bạn là: ${level}`);
    navigate('/dashboard');
  };

  return (
    <div className="assessment-container">
      <div className="assessment-card">
        <h2>Kiểm tra năng lực đầu vào</h2>
        <p className="progress-text">Câu hỏi {step + 1} / {testSentences.length}</p>
        
        <div className="sentence-box">
          <p>"{testSentences[step].text}"</p>
        </div>

        <button 
          className={`mic-btn ${isRecording ? 'active' : ''}`} 
          onClick={handleStart}
          disabled={loading}
        >
          <i className={`fas fa-${isRecording ? 'stop' : 'microphone'}`}></i>
          {isRecording ? ' Đang lắng nghe...' : ' Nhấn để nói'}
        </button>
        
        {loading && <p>AI đang phân tích giọng nói...</p>}
      </div>
    </div>
  );
};

export default Assessment;