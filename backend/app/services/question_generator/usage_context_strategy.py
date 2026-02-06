"""
Strategy cho Content Word - Usage in Context MCQ.
Tạo câu hỏi về cách sử dụng từ trong ngữ cảnh.
"""
import random
from typing import Dict, Any, List
from app.models.vocabulary import Vocabulary
from app.models.enums import QuestionType, QuestionDifficulty
from app.services.question_generator.base import QuestionGeneratorStrategy


class UsageContextStrategy(QuestionGeneratorStrategy):
    """
    Strategy cho Content Words.
    Generate câu hỏi về usage in context: chọn câu sử dụng từ đúng.
    """
    
    def generate(
        self,
        vocabulary: Vocabulary,
        difficulty: QuestionDifficulty,
        distractors: List[Vocabulary]
    ) -> Dict[str, Any]:
        """
        Generate usage in context MCQ question.
        
        Args:
            vocabulary: Vocabulary cần generate câu hỏi
            difficulty: Mức độ khó
            distractors: Danh sách vocabularies khác để tạo fake sentences
            
        Returns:
            Question data snapshot
        """
        word = vocabulary.word
        
        if vocabulary.contexts and len(vocabulary.contexts) > 0:
            # Có context: Tạo câu hỏi "Which sentence uses '{word}' correctly?"
            correct_sentence = vocabulary.contexts[0].sentence
            
            # Tạo fake sentences từ distractors
            options = [correct_sentence]
            
            for dist in distractors:
                if dist.id != vocabulary.id and len(options) < 4:
                    if dist.contexts and len(dist.contexts) > 0:
                        # Thay thế từ trong câu của distractor bằng từ hiện tại
                        # Tạo câu sai ngữ nghĩa
                        fake_sentence = dist.contexts[0].sentence.replace(dist.word, word)
                        if fake_sentence != correct_sentence:
                            options.append(fake_sentence)
            
            # Nếu không đủ options từ distractors, tạo fake sentences đơn giản
            while len(options) < 4:
                fake_templates = [
                    f"The {word} is very important.",
                    f"I like to {word} every day.",
                    f"This is a good {word}.",
                    f"She has a beautiful {word}.",
                ]
                fake = fake_templates[len(options) - 1]
                if fake not in options:
                    options.append(fake)
            
            question_text = f"Which sentence uses '{word}' CORRECTLY?"
            
        else:
            # Không có context: Tạo câu hỏi đơn giản hơn
            # Sử dụng definition để tạo câu
            definition = vocabulary.meanings[0].definition if vocabulary.meanings else "something"
            
            correct_sentence = f"The {word} is {definition}."
            
            # Tạo fake sentences
            options = [correct_sentence]
            for i in range(3):
                fake_defs = ["incorrect", "wrong", "not right"]
                options.append(f"The {word} is {fake_defs[i]}.")
            
            question_text = f"Which sentence describes '{word}' correctly?"
        
        random.shuffle(options)
        
        question_data = {
            "question_type": QuestionType.MULTIPLE_CHOICE.value,  # Sử dụng existing type
            "question_text": question_text,
            "correct_answer": correct_sentence,
            "word": word,
            "options": options,
            "context_sentence": None,
            "explanation": f"Câu đúng là: {correct_sentence}",
        }
        
        return question_data
    
    def get_question_type(self) -> QuestionType:
        """Trả về MULTIPLE_CHOICE."""
        return QuestionType.MULTIPLE_CHOICE
