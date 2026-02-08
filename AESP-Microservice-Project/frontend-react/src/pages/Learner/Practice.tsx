import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle, Mic, Square, Volume2, MessageSquare, Award, Loader2 } from 'lucide-react';
import './Practice.css';

interface Message {
  sender: 'ai' | 'user';
  text: string;
  accuracy?: number;
  correction?: string;
}

const Practice: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const taskData = location.state;

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis>(window.speechSynthesis);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [userLevel] = useState(() => {
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
    return userInfo.level || userInfo.user_level || "A1"; 
  });

  const [messages, setMessages] = useState<Message[]>([
    { 
      sender: 'ai', 
      text: taskData?.isFromTask 
        ? `Hello! Mentor assigned you a task: "${taskData.topic}". ${taskData.description}. Let's start!` 
        : `Hi! I'm your AI Coach. Your current level is ${userLevel}. What topic would you like to practice today?` 
    }
  ]);

  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState(taskData?.isFromTask ? "Task Mode Active" : "Press mic to speak");
  const [selectedTopic] = useState(taskData?.topic || "Daily Life");
  const [isAiThinking, setIsAiThinking] = useState(false);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.lang = 'en-US';
      recognitionRef.current.interimResults = false;

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript.trim()) {
          // 🔥 Quan trọng: Dừng recorder trước để kích hoạt sự kiện onstop
          if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
            mediaRecorderRef.current.onstop = () => {
              const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
              handleProcessExchange(transcript, audioBlob);
              stopStream(); // Tắt đèn micro trên trình duyệt
            };
            mediaRecorderRef.current.stop();
          }
        }
      };

      recognitionRef.current.onend = () => setIsListening(false);
      recognitionRef.current.onerror = () => {
        setIsListening(false);
        setStatus("Could not hear you. Try again.");
        stopStream();
      };
    }
  }, [selectedTopic]);

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  const speak = (text: string) => {
    synthRef.current.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    const voices = synthRef.current.getVoices();
    const voice = voices.find(v => v.lang.includes('en') && v.name.includes('Google')) || voices[0];
    if (voice) utterance.voice = voice;
    synthRef.current.speak(utterance);
  };

  const toggleMic = async () => {
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) audioChunksRef.current.push(e.data);
        };
        
        mediaRecorder.start();
        recognitionRef.current.start();
        setIsListening(true);
        setStatus("Listening...");
      } catch (err) {
        setStatus("Mic access denied");
      }
    }
  };

  const handleProcessExchange = async (text: string, audioBlob: Blob) => {
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
    const userId = userInfo.id || userInfo.user_id;
    
    setMessages(prev => [...prev, { sender: 'user', text }]);
    setIsAiThinking(true);
    setStatus("Syncing data to mentor...");

    try {
      // 1. GỬI AUDIO + TRANSCRIPT CHO MENTOR
      const audioFormData = new FormData();
      audioFormData.append('audio', audioBlob, 'voice_record.wav');
      audioFormData.append('user_id', userId);
      audioFormData.append('topic', selectedTopic);
      audioFormData.append('transcript', text); // Gửi chữ để Mentor chấm bài

      const audioPromise = fetch('/api/mentors/submissions/upload-audio', {
        method: 'POST',
        body: audioFormData
      });

      // 2. GỬI TEXT CHO AI CHAT
      const aiPromise = fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, topic: selectedTopic, user_id: userId, level: userLevel })
      });

      const [aiRes] = await Promise.all([aiPromise, audioPromise]);
      const data = await aiRes.json();

      if (data.reply) {
        setMessages(prev => [...prev, { sender: 'ai', text: data.reply, accuracy: data.accuracy, correction: data.correction }]);
        speak(data.reply);
        setStatus(`Accuracy: ${data.accuracy}%`);
      }
    } catch (e) {
      setStatus("Error saving voice.");
    } finally {
      setIsAiThinking(false);
    }
  };

  const handleFinishTask = async () => {
    if (!taskData?.taskId) return;
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`/api/mentors/tasks/${taskData.taskId}/complete`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
      });
      if (res.ok) navigate('/progress');
    } catch (e) { alert("Submit failed."); }
  };

  return (
    <main className="practice-container">
      <div className="practice-sidebar">
        <div className="sidebar-top">
          <div className="level-badge">
            <Award size={20} className="icon-gold" />
            <span>Level: {userLevel}</span>
          </div>
          <div className="topic-section">
            <p className="section-label">Topic</p>
            <div className="topic-card-fixed active">
              <MessageSquare size={16} /> {selectedTopic}
            </div>
          </div>
        </div>
        {taskData?.isFromTask && messages.length > 2 && (
          <button onClick={handleFinishTask} className="finish-btn">
            <CheckCircle size={18} /> Submit Task
          </button>
        )}
      </div>

      <div className="chat-main">
        <div className="chat-history" ref={chatContainerRef}>
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble-wrapper ${msg.sender}`}>
              <div className="chat-bubble">
                <p>{msg.text}</p>
                {msg.sender === 'ai' && (
                  <button className="tts-btn" onClick={() => speak(msg.text)}>
                    <Volume2 size={16} />
                  </button>
                )}
              </div>
              {msg.accuracy !== undefined && (
                <div className="score-badge animate-in">
                  <span className="accuracy">Score: {msg.accuracy}%</span>
                  {msg.correction && msg.correction !== 'Perfect' && (
                    <span className="correction">💡 {msg.correction}</span>
                  )}
                </div>
              )}
            </div>
          ))}
          {isAiThinking && (
            <div className="chat-bubble-wrapper ai">
              <div className="chat-bubble typing">
                <Loader2 size={18} className="spin" />
                <span>AI evaluating...</span>
              </div>
            </div>
          )}
        </div>

        <div className="input-area">
          <div className="input-status-group">
            <div className={`visualizer ${isListening ? 'active' : ''}`}>
              <span></span><span></span><span></span><span></span><span></span>
            </div>
            <p className="status-msg">{status}</p>
          </div>
          <button 
            className={`mic-main-btn ${isListening ? 'recording' : ''}`} 
            onClick={toggleMic}
            disabled={isAiThinking}
          >
            {isListening ? <Square size={24} fill="white" /> : <Mic size={32} />}
          </button>
        </div>
      </div>
    </main>
  );
};

export default Practice;