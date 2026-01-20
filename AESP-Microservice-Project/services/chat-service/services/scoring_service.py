from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta

class ScoringService:
    def __init__(self):
        pass
    
    def calculate_pronunciation_score(
        self,
        text: str,
        phonetic_accuracy: float,
        word_stress_accuracy: float,
        intonation_accuracy: float
    ) -> Dict:
        """Tính điểm phát âm chi tiết"""
        
        # Trọng số các yếu tố
        weights = {
            "phonetic": 0.5,
            "word_stress": 0.3,
            "intonation": 0.2
        }
        
        # Tính điểm tổng
        overall_score = (
            phonetic_accuracy * weights["phonetic"] +
            word_stress_accuracy * weights["word_stress"] +
            intonation_accuracy * weights["intonation"]
        )
        
        # Xác định level
        if overall_score >= 0.9:
            level = "Excellent"
        elif overall_score >= 0.7:
            level = "Good"
        elif overall_score >= 0.5:
            level = "Fair"
        else:
            level = "Needs Practice"
        
        # Tìm từ khó phát âm (đơn giản)
        difficult_words = self._identify_difficult_words(text)
        
        return {
            "overall_score": round(overall_score, 3),
            "breakdown": {
                "phonetic_accuracy": round(phonetic_accuracy, 3),
                "word_stress_accuracy": round(word_stress_accuracy, 3),
                "intonation_accuracy": round(intonation_accuracy, 3)
            },
            "level": level,
            "difficult_words": difficult_words,
            "improvement_suggestions": self._get_pronunciation_suggestions(overall_score, difficult_words)
        }
    
    def calculate_grammar_score(
        self,
        original_text: str,
        corrected_text: str,
        errors: List[Dict]
    ) -> Dict:
        """Tính điểm ngữ pháp"""
        
        total_words = len(original_text.split())
        error_count = len(errors)
        
        # Tính accuracy
        if total_words > 0:
            accuracy = 1 - (error_count / total_words)
        else:
            accuracy = 1.0
        
        # Phân loại lỗi
        error_types = {}
        for error in errors:
            error_type = error.get("type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Xác định lỗi phổ biến
        common_errors = []
        for error_type, count in error_types.items():
            if count > 1:  # Lỗi lặp lại
                common_errors.append({
                    "type": error_type,
                    "count": count,
                    "percentage": round(count / error_count * 100, 1) if error_count > 0 else 0
                })
        
        return {
            "accuracy_score": round(accuracy, 3),
            "error_count": error_count,
            "error_distribution": error_types,
            "common_errors": common_errors,
            "severity": "high" if accuracy < 0.6 else "medium" if accuracy < 0.8 else "low"
        }
    
    def calculate_vocabulary_score(
        self,
        text: str,
        unique_words: int,
        complex_words: int,
        word_variety: float
    ) -> Dict:
        """Tính điểm từ vựng"""
        
        total_words = len(text.split())
        
        if total_words == 0:
            return {
                "score": 0,
                "level": "Beginner",
                "feedback": "No words detected"
            }
        
        # Tính các chỉ số
        lexical_density = unique_words / total_words if total_words > 0 else 0
        complexity_ratio = complex_words / total_words if total_words > 0 else 0
        
        # Tính điểm tổng (đơn giản)
        score = (lexical_density * 0.4 + word_variety * 0.3 + complexity_ratio * 0.3)
        
        # Xác định level
        if score >= 0.7:
            level = "Advanced"
        elif score >= 0.5:
            level = "Intermediate"
        else:
            level = "Beginner"
        
        # Gợi ý từ vựng
        suggestions = self._get_vocabulary_suggestions(score, lexical_density, complexity_ratio)
        
        return {
            "score": round(score, 3),
            "level": level,
            "metrics": {
                "total_words": total_words,
                "unique_words": unique_words,
                "lexical_density": round(lexical_density, 3),
                "complex_words": complex_words,
                "complexity_ratio": round(complexity_ratio, 3),
                "word_variety": round(word_variety, 3)
            },
            "suggestions": suggestions
        }
    
    def calculate_fluency_score(
        self,
        words_per_minute: float,
        pause_frequency: float,
        filler_word_count: int,
        repetition_count: int
    ) -> Dict:
        """Tính điểm độ trôi chảy"""
        
        # Điểm WPM (Words Per Minute)
        if words_per_minute >= 150:
            wpm_score = 1.0
        elif words_per_minute >= 100:
            wpm_score = 0.8
        elif words_per_minute >= 70:
            wpm_score = 0.6
        elif words_per_minute >= 50:
            wpm_score = 0.4
        else:
            wpm_score = 0.2
        
        # Điểm pause frequency
        if pause_frequency <= 0.5:
            pause_score = 1.0
        elif pause_frequency <= 1.0:
            pause_score = 0.8
        elif pause_frequency <= 2.0:
            pause_score = 0.6
        elif pause_frequency <= 3.0:
            pause_score = 0.4
        else:
            pause_score = 0.2
        
        # Điểm filler words
        if filler_word_count == 0:
            filler_score = 1.0
        elif filler_word_count <= 2:
            filler_score = 0.7
        elif filler_word_count <= 5:
            filler_score = 0.4
        else:
            filler_score = 0.1
        
        # Điểm repetition
        if repetition_count == 0:
            repetition_score = 1.0
        elif repetition_count <= 2:
            repetition_score = 0.6
        else:
            repetition_score = 0.2
        
        # Tính điểm tổng
        overall_score = (wpm_score * 0.4 + pause_score * 0.3 + 
                        filler_score * 0.2 + repetition_score * 0.1)
        
        return {
            "overall_score": round(overall_score, 3),
            "breakdown": {
                "words_per_minute": round(words_per_minute, 1),
                "wpm_score": round(wpm_score, 3),
                "pause_frequency": round(pause_frequency, 1),
                "pause_score": round(pause_score, 3),
                "filler_word_count": filler_word_count,
                "filler_score": round(filler_score, 3),
                "repetition_count": repetition_count,
                "repetition_score": round(repetition_score, 3)
            },
            "level": "Fluent" if overall_score >= 0.7 else "Moderate" if overall_score >= 0.5 else "Needs Practice"
        }
    
    def calculate_overall_session_score(
        self,
        pronunciation_score: float,
        grammar_score: float,
        vocabulary_score: float,
        fluency_score: float,
        session_duration: float
    ) -> Dict:
        """Tính điểm tổng thể cho session"""
        
        # Trọng số có thể điều chỉnh
        weights = {
            "pronunciation": 0.3,
            "grammar": 0.25,
            "vocabulary": 0.2,
            "fluency": 0.25
        }
        
        overall_score = (
            pronunciation_score * weights["pronunciation"] +
            grammar_score * weights["grammar"] +
            vocabulary_score * weights["vocabulary"] +
            fluency_score * weights["fluency"]
        )
        
        # Đánh giá level
        if overall_score >= 0.9:
            level = "Excellent"
            grade = "A"
        elif overall_score >= 0.8:
            level = "Very Good"
            grade = "B"
        elif overall_score >= 0.7:
            level = "Good"
            grade = "C"
        elif overall_score >= 0.6:
            level = "Satisfactory"
            grade = "D"
        else:
            level = "Needs Improvement"
            grade = "F"
        
        return {
            "overall_score": round(overall_score, 3),
            "grade": grade,
            "level": level,
            "weighted_scores": {
                "pronunciation": round(pronunciation_score * weights["pronunciation"], 3),
                "grammar": round(grammar_score * weights["grammar"], 3),
                "vocabulary": round(vocabulary_score * weights["vocabulary"], 3),
                "fluency": round(fluency_score * weights["fluency"], 3)
            }
        }
    
    def _identify_difficult_words(self, text: str) -> List[Dict]:
        """Xác định từ khó phát âm"""
        difficult_words_list = [
            "thorough", "rural", "sixth", "phenomenon", "anemone",
            "specific", "statistics", "ethnic", "linguistic", "queue",
            "entrepreneur", "mischievous", "colonel", "epitome", "hyperbole"
        ]
        
        words = text.lower().split()
        found = []
        
        for word in words:
            if word in difficult_words_list:
                found.append({
                    "word": word,
                    "difficulty": "high",
                    "tip": f"Practice saying '{word}' slowly, breaking it into syllables"
                })
        
        return found
    
    def _get_pronunciation_suggestions(self, score: float, difficult_words: List[Dict]) -> List[str]:
        """Đưa ra gợi ý cải thiện phát âm"""
        suggestions = []
        
        if score < 0.6:
            suggestions.append("Focus on basic vowel and consonant sounds")
            suggestions.append("Practice minimal pairs (ship/sheep, bit/beat)")
        
        if score < 0.8:
            suggestions.append("Work on word stress patterns")
            suggestions.append("Record yourself and compare with native speakers")
        
        if difficult_words:
            suggestions.append(f"Practice these difficult words: {', '.join([w['word'] for w in difficult_words])}")
        
        suggestions.append("Use our pronunciation drills for daily practice")
        
        return suggestions[:3]  # Giới hạn 3 gợi ý
    
    def _get_vocabulary_suggestions(self, score: float, lexical_density: float, complexity_ratio: float) -> List[str]:
        """Đưa ra gợi ý cải thiện từ vựng"""
        suggestions = []
        
        if lexical_density < 0.5:
            suggestions.append("Try to use more varied vocabulary instead of repeating words")
        
        if complexity_ratio < 0.2:
            suggestions.append("Incorporate more complex words and phrases")
        
        if score < 0.6:
            suggestions.append("Learn 5 new words daily and use them in sentences")
            suggestions.append("Read English articles on topics that interest you")
        
        suggestions.append("Use the vocabulary builder exercises in our app")
        
        return suggestions[:3]