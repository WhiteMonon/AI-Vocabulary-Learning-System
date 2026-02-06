"""
Question Pre-Generator Service - Pre-generate questions khi vocabulary được tạo.
"""
from typing import List, Optional
from sqlmodel import Session

from app.core.logging import get_logger
from app.models.vocabulary import Vocabulary
from app.models.generated_question import GeneratedQuestion
from app.models.enums import QuestionDifficulty
from app.services.question_generator.factory import QuestionGeneratorFactory

logger = get_logger(__name__)

# Số questions pre-generate cho mỗi vocabulary
QUESTIONS_PER_VOCAB = 10


class QuestionPreGeneratorService:
    """
    Service để pre-generate questions cho vocabulary.
    Chạy trong background task sau khi vocabulary được tạo.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def pre_generate_for_vocabulary(
        self,
        vocabulary: Vocabulary,
        count: int = QUESTIONS_PER_VOCAB
    ) -> List[GeneratedQuestion]:
        """
        Pre-generate questions cho 1 vocabulary.
        
        Args:
            vocabulary: Vocabulary cần generate
            count: Số lượng questions cần generate
            
        Returns:
            List các GeneratedQuestion đã được tạo
        """
        try:
            # Lấy distractors từ các vocabulary khác của user
            distractors = self._get_distractors(vocabulary.user_id, vocabulary.id)
            
            # Generate multiple questions
            question_data_list = QuestionGeneratorFactory.generate_multiple_questions(
                vocabulary=vocabulary,
                count=count,
                difficulty=QuestionDifficulty.MEDIUM,
                distractors=distractors
            )
            
            # Lưu vào database
            generated_questions = []
            for question_data in question_data_list:
                question = GeneratedQuestion(
                    session_id=None,  # Pre-generated, chưa dùng
                    user_id=vocabulary.user_id,
                    vocabulary_id=vocabulary.id,
                    question_type=question_data.get("question_type"),
                    difficulty=QuestionDifficulty.MEDIUM,
                    question_data=question_data,
                    is_used=False
                )
                self.db.add(question)
                generated_questions.append(question)
            
            self.db.commit()
            
            logger.info(f"Pre-generated {len(generated_questions)} questions for vocabulary '{vocabulary.word}' (ID: {vocabulary.id})")
            return generated_questions
            
        except Exception as e:
            logger.error(f"Failed to pre-generate questions for vocabulary {vocabulary.id}: {e}")
            self.db.rollback()
            return []
    
    async def pre_generate_for_vocab_id(self, vocab_id: int) -> List[GeneratedQuestion]:
        """
        Pre-generate questions cho vocabulary by ID.
        """
        from sqlalchemy.orm import selectinload
        from sqlmodel import select
        
        statement = select(Vocabulary).where(Vocabulary.id == vocab_id).options(
            selectinload(Vocabulary.audios),
            selectinload(Vocabulary.meanings),
            selectinload(Vocabulary.contexts)
        )
        
        vocabulary = self.db.exec(statement).first()
        if not vocabulary:
            logger.warning(f"Vocabulary {vocab_id} not found")
            return []
        
        return await self.pre_generate_for_vocabulary(vocabulary)
    
    def _get_distractors(self, user_id: int, exclude_vocab_id: int, limit: int = 20) -> List[Vocabulary]:
        """
        Lấy danh sách vocabulary khác của user để làm distractors.
        """
        from sqlmodel import select
        
        statement = select(Vocabulary).where(
            Vocabulary.user_id == user_id,
            Vocabulary.id != exclude_vocab_id
        ).limit(limit)
        
        results = self.db.exec(statement)
        return list(results)
    
    def get_pregenerated_questions(
        self,
        vocabulary_id: int,
        count: int = 5
    ) -> List[GeneratedQuestion]:
        """
        Lấy N questions chưa dùng từ pool cho vocabulary.
        
        Args:
            vocabulary_id: ID của vocabulary
            count: Số lượng questions cần lấy
            
        Returns:
            List các GeneratedQuestion chưa dùng
        """
        from sqlmodel import select
        
        statement = select(GeneratedQuestion).where(
            GeneratedQuestion.vocabulary_id == vocabulary_id,
            GeneratedQuestion.session_id == None,
            GeneratedQuestion.is_used == False
        ).limit(count)
        
        results = self.db.exec(statement)
        return list(results)
    
    def mark_questions_used(
        self,
        questions: List[GeneratedQuestion],
        session_id: int
    ):
        """
        Mark questions với session_id và is_used = True.
        """
        for question in questions:
            question.session_id = session_id
            question.is_used = True
            self.db.add(question)
        
        self.db.commit()
