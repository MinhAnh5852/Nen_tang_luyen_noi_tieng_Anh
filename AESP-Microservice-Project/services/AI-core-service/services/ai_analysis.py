import openai

def analyze_speaking(audio_file_path):
    # 1. Chuyển giọng nói thành văn bản (Speech-to-Text)
    audio_file = open(audio_file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    
    # 2. Phân tích ngữ pháp và phát âm qua GPT
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Analyze the grammar and pronunciation of this transcript. Return scores out of 100."},
            {"role": "user", "content": transcript['text']}
        ]
    )
    return transcript['text'], response