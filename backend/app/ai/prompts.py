"""
Module chứa các prompt templates cho AI.
Đảm bảo output luôn là JSON định dạng theo schemas.
"""

MULTIPLE_CHOICE_GEN = """
Tạo một câu hỏi trắc nghiệm (Multiple Choice) cho từ vựng sau:
Từ: {word}
Định nghĩa: {definition}

Yêu cầu trả về định dạng JSON:
{{
    "question_text": "Nội dung câu hỏi yêu cầu người dùng chọn đáp án đúng để hoàn thành câu hoặc giải nghĩa từ.",
    "options": {{
        "A": "Lựa chọn 1",
        "B": "Lựa chọn 2",
        "C": "Lựa chọn 3",
        "D": "Lựa chọn 4"
    }},
    "correct_answer": "A/B/C/D",
    "explanation": "Giải thích tại sao đáp án đó đúng và tại sao các lỗi khác sai.",
    "practice_type": "multiple_choice"
}}
"""

FILL_BLANK_GEN = """
Tạo một câu hỏi điền vào chỗ trống (Fill in the Blank) cho từ vựng sau:
Từ: {word}
Định nghĩa: {definition}

Yêu cầu trả về định dạng JSON:
{{
    "question_text": "Một câu ví dụ tiếng Anh có chứa dấu '____' thay thế cho từ '{word}'.",
    "options": null,
    "correct_answer": "{word}",
    "explanation": "Giải thích ngữ cảnh sử dụng của từ trong câu này.",
    "practice_type": "fill_blank"
}}
"""

GRAMMAR_EVAL = """
Đánh giá ngữ pháp cho câu trả lời sau:
Câu hỏi: {question}
Đáp án mong đợi: {expected}
Người dùng trả lời: {answer}

Yêu cầu trả về định dạng JSON:
{{
    "is_correct": true/false (đúng nếu ý nghĩa và ngữ pháp chấp nhận được),
    "feedback": "Phản hồi chi tiết về lỗi ngữ pháp hoặc dùng từ (nếu có).",
    "score": 0.0 đến 1.0 (mức độ chính xác)
}}
"""

VOCAB_EXPLANATION = """
Giải thích chi tiết về từ vựng sau cho người học tiếng Anh:
Từ: {word}
Định nghĩa: {definition}

Yêu cầu trả về định dạng JSON:
{{
    "word": "{word}",
    "phonetic": "Phiên âm IPA",
    "part_of_speech": "Từ loại",
    "simple_definition": "Định nghĩa dễ hiểu",
    "examples": ["Ví dụ 1", "Ví dụ 2"],
    "synonyms": ["Từ đồng nghĩa 1", "2"],
    "antonyms": ["Từ trái nghĩa 1", "2"],
    "usage_note": "Lưu ý đặc biệt khi sử dụng từ này."
}}
"""
