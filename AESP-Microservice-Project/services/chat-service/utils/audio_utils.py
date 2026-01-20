import base64
import re
import wave
import struct
import numpy as np
from typing import Tuple, Optional
import tempfile
import os

def validate_audio_base64(audio_base64: str) -> bool:
    """Validate base64 audio data"""
    try:
        # Kiểm tra chuỗi base64
        if not audio_base64 or len(audio_base64) < 100:
            return False
        
        # Thử decode
        decoded = base64.b64decode(audio_base64)
        
        # Kiểm tra kích thước (max 10MB)
        if len(decoded) > 10 * 1024 * 1024:
            return False
        
        return True
    
    except Exception:
        return False

def convert_audio_format(
    input_path: str,
    output_path: str,
    target_sample_rate: int = 16000,
    target_channels: int = 1
) -> bool:
    """Chuyển đổi định dạng audio"""
    try:
        from pydub import AudioSegment
        
        audio = AudioSegment.from_file(input_path)
        
        # Convert sample rate
        if audio.frame_rate != target_sample_rate:
            audio = audio.set_frame_rate(target_sample_rate)
        
        # Convert channels
        if audio.channels != target_channels:
            audio = audio.set_channels(target_channels)
        
        # Export
        audio.export(output_path, format="wav")
        return True
    
    except ImportError:
        print("pydub not installed, skipping audio conversion")
        return False
    except Exception as e:
        print(f"Audio conversion error: {e}")
        return False

def extract_audio_features(audio_base64: str) -> Optional[Dict]:
    """Trích xuất đặc trưng từ audio"""
    try:
        audio_data = base64.b64decode(audio_base64)
        
        # Lưu file tạm
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        try:
            # Đọc file WAV
            with wave.open(tmp_path, 'rb') as wav_file:
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                
                # Đọc audio data
                frames = wav_file.readframes(n_frames)
                
                # Convert sang numpy array
                if sample_width == 2:
                    dtype = np.int16
                elif sample_width == 4:
                    dtype = np.int32
                else:
                    dtype = np.int8
                
                audio_array = np.frombuffer(frames, dtype=dtype)
                
                # Reshape nếu stereo
                if n_channels > 1:
                    audio_array = audio_array.reshape(-1, n_channels)
                    # Chuyển thành mono bằng cách tính trung bình
                    audio_array = np.mean(audio_array, axis=1)
                
                # Tính các đặc trưng
                duration = n_frames / frame_rate
                rms_energy = np.sqrt(np.mean(audio_array**2))
                zero_crossing_rate = np.sum(np.abs(np.diff(np.sign(audio_array)))) / (2 * len(audio_array))
                
                # Tính FFT cho frequency analysis
                fft_result = np.fft.rfft(audio_array)
                fft_freq = np.fft.rfftfreq(len(audio_array), 1/frame_rate)
                fft_magnitude = np.abs(fft_result)
                
                # Tìm dominant frequency
                if len(fft_magnitude) > 0:
                    dominant_freq_idx = np.argmax(fft_magnitude)
                    dominant_freq = fft_freq[dominant_freq_idx]
                else:
                    dominant_freq = 0
                
                return {
                    "duration": duration,
                    "sample_rate": frame_rate,
                    "channels": n_channels,
                    "sample_width": sample_width,
                    "rms_energy": float(rms_energy),
                    "zero_crossing_rate": float(zero_crossing_rate),
                    "dominant_frequency": float(dominant_freq),
                    "frame_count": n_frames
                }
        
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        print(f"Audio feature extraction error: {e}")
        return None

def calculate_silence_threshold(audio_array: np.ndarray, percentile: int = 10) -> float:
    """Tính ngưỡng silence cho audio"""
    if len(audio_array) == 0:
        return 0.0
    
    # Sử dụng percentile để xác định ngưỡng
    threshold = np.percentile(np.abs(audio_array), percentile)
    return float(threshold)

def detect_silence_periods(
    audio_array: np.ndarray,
    sample_rate: int,
    silence_threshold: float = None,
    min_silence_duration: float = 0.1
) -> List[Tuple[float, float]]:
    """Phát hiện các khoảng silence trong audio"""
    
    if silence_threshold is None:
        silence_threshold = calculate_silence_threshold(audio_array)
    
    # Tìm các sample dưới ngưỡng silence
    is_silence = np.abs(audio_array) < silence_threshold
    
    # Tìm các đoạn silence liên tục
    silence_starts = []
    silence_ends = []
    
    in_silence = False
    for i, silent in enumerate(is_silence):
        if silent and not in_silence:
            silence_starts.append(i)
            in_silence = True
        elif not silent and in_silence:
            silence_ends.append(i)
            in_silence = False
    
    # Kết thúc nếu đang trong silence
    if in_silence:
        silence_ends.append(len(audio_array))
    
    # Chuyển sang thời gian (giây) và lọc theo duration
    silence_periods = []
    min_silence_samples = min_silence_duration * sample_rate
    
    for start, end in zip(silence_starts, silence_ends):
        duration_samples = end - start
        if duration_samples >= min_silence_samples:
            start_time = start / sample_rate
            end_time = end / sample_rate
            silence_periods.append((start_time, end_time))
    
    return silence_periods

def calculate_speech_rate(
    text: str,
    audio_duration: float,
    pause_duration: float = 0
) -> Dict:
    """Tính tốc độ nói"""
    
    if audio_duration <= 0:
        return {
            "words_per_minute": 0,
            "syllables_per_second": 0,
            "articulation_rate": 0
        }
    
    # Đếm từ và syllables
    words = text.split()
    word_count = len(words)
    
    # Đếm syllables (đơn giản)
    syllable_count = sum(count_syllables(word) for word in words)
    
    # Tính speaking time (trừ pause time)
    speaking_time = audio_duration - pause_duration
    if speaking_time <= 0:
        speaking_time = audio_duration
    
    # Tính WPM
    words_per_minute = (word_count / speaking_time) * 60 if speaking_time > 0 else 0
    
    # Tính syllables per second
    syllables_per_second = syllable_count / speaking_time if speaking_time > 0 else 0
    
    # Tính articulation rate
    articulation_rate = syllables_per_second
    
    return {
        "words_per_minute": round(words_per_minute, 1),
        "syllables_per_second": round(syllables_per_second, 1),
        "articulation_rate": round(articulation_rate, 2),
        "word_count": word_count,
        "syllable_count": syllable_count,
        "speaking_time": round(speaking_time, 2),
        "pause_time": round(pause_duration, 2)
    }

def count_syllables(word: str) -> int:
    """Đếm syllables trong một từ (đơn giản)"""
    word = word.lower().strip()
    if not word:
        return 0
    
    # Đếm vowels
    vowels = "aeiouy"
    count = 0
    prev_char_is_vowel = False
    
    for char in word:
        if char in vowels:
            if not prev_char_is_vowel:
                count += 1
            prev_char_is_vowel = True
        else:
            prev_char_is_vowel = False
    
    # Điều chỉnh đặc biệt
    if word.endswith("e"):
        count -= 1
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1
    if count == 0:
        count = 1
    
    return count