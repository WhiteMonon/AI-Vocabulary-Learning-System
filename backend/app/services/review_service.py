"""
Review Service Layer - Business logic cho review session management.
Hỗ trợ context-based review với question snapshots và telemetry tracking.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models.vocabulary import Vocabulary
from app.models.review_session import ReviewSession
from app.models.generated_question import GeneratedQuestion
from app.models.enums import QuestionDifficulty, WordType
from app.services.question_generator.factory import QuestionGeneratorFactory
from app.core.logging import get_logger
from app.core.srs_engine import SRSEngine, SRSState, ReviewQuality as SRSReviewQuality

logger = get_logger(__name__)


class ReviewService:
    """
    Service layer cho review session management.
    Implement business logic cho session creation, question generation, và evaluation.
    """
    
    def __init__(self, session: Session):
        """
        Initialize review service.
        
        Args:
            session: Database session
        """
        self.session = session
        self.srs_engine = SRSEngine()
    
    def create_session(
        self,
        user_id: int,
        mode: str = "due",
        max_vocabularies: int = 4,
        questions_per_vocab: int = 5
    ) -> ReviewSession:
        """
        Tạo review session mới với pre-generated questions.
        
        Args:
            user_id: ID của user
            mode: Mode review ('due' hoặc 'new')
            max_vocabularies: Số từ vựng tối đa (default 4)
            questions_per_vocab: Số câu hỏi cho mỗi từ (default 5)
            
        Returns:
            ReviewSession đã được tạo với questions (shuffled)
        """
        import random
        
        # 1. Lấy vocabularies phù hợp (limit 4)
        vocabularies = self._get_vocabularies_for_review(user_id, mode, max_vocabularies)
        
        if not vocabularies:
            logger.info(f"No vocabularies available for review (user={user_id}, mode={mode})")
            # Tạo empty session
            empty_session = ReviewSession(
                user_id=user_id,
                status="completed",
                total_questions=0,
                correct_count=0
            )
            self.session.add(empty_session)
            self.session.commit()
            self.session.refresh(empty_session)
            return empty_session
        
        # 2. Tạo ReviewSession
        total_questions = len(vocabularies) * questions_per_vocab
        review_session = ReviewSession(
            user_id=user_id,
            status="in_progress",
            total_questions=total_questions,
            correct_count=0
        )
        self.session.add(review_session)
        self.session.flush()  # Lấy session.id
        
        # 3. Lấy hoặc generate questions cho mỗi vocabulary
        all_questions = []
        distractors = vocabularies  # Dùng toàn bộ list làm distractor pool
        
        for vocab in vocabularies:
            questions = self._get_questions_for_vocabulary(
                session_id=review_session.id,
                user_id=user_id,
                vocabulary=vocab,
                count=questions_per_vocab,
                distractors=distractors
            )
            all_questions.extend(questions)
        
        # 4. Shuffle tất cả questions
        random.shuffle(all_questions)
        
        # 5. Lưu questions
        for question in all_questions:
            self.session.add(question)
        
        # 6. Commit
        self.session.commit()
        self.session.refresh(review_session)
        
        logger.info(f"Created review session {review_session.id} with {len(all_questions)} questions for user {user_id}")
        return review_session
    
    def _get_questions_for_vocabulary(
        self,
        session_id: int,
        user_id: int,
        vocabulary: Vocabulary,
        count: int,
        distractors: List[Vocabulary]
    ) -> List[GeneratedQuestion]:
        """
        Lấy questions từ pre-generated pool hoặc generate realtime nếu thiếu.
        
        Args:
            session_id: ID của session
            user_id: ID của user
            vocabulary: Vocabulary cần lấy questions
            count: Số lượng questions cần lấy
            distractors: Danh sách vocabularies khác làm distractors
            
        Returns:
            List GeneratedQuestion (đã mark session_id)
        """
        from sqlmodel import select
        
        # 1. Thử lấy từ pool (pre-generated, chưa dùng)
        statement = select(GeneratedQuestion).where(
            GeneratedQuestion.vocabulary_id == vocabulary.id,
            GeneratedQuestion.session_id == None,
            GeneratedQuestion.is_used == False
        ).limit(count)
        
        pool_questions = list(self.session.exec(statement))
        
        # 2. Mark những questions từ pool
        for q in pool_questions:
            q.session_id = session_id
            q.is_used = True
        
        # 3. Nếu thiếu, generate realtime
        remaining = count - len(pool_questions)
        if remaining > 0:
            logger.info(f"Pool thiếu {remaining} questions cho vocab {vocabulary.id}, generating realtime...")
            
            # Generate bổ sung với đa dạng question types
            difficulty = self._calculate_difficulty(vocabulary)
            new_question_data_list = QuestionGeneratorFactory.generate_multiple_questions(
                vocabulary=vocabulary,
                count=remaining,
                difficulty=difficulty,
                distractors=distractors
            )
            
            # Tạo GeneratedQuestion objects
            for question_data in new_question_data_list:
                question = GeneratedQuestion(
                    session_id=session_id,
                    user_id=user_id,
                    vocabulary_id=vocabulary.id,
                    question_type=question_data["question_type"],
                    difficulty=difficulty,
                    question_data=question_data,
                    confusion_pair_group=question_data.get("confusion_pair_group"),
                    is_used=True
                )
                pool_questions.append(question)
        
        return pool_questions
    

    
    def _get_vocabularies_for_review(
        self,
        user_id: int,
        mode: str,
        max_questions: int
    ) -> List[Vocabulary]:
        """
        Lấy danh sách vocabularies cần review.
        
        Args:
            user_id: ID của user
            mode: 'due' (cần ôn) hoặc 'new' (từ mới)
            max_questions: Số câu hỏi tối đa
            
        Returns:
            List vocabularies với meanings eager loaded
        """
        query = select(Vocabulary).where(
            Vocabulary.user_id == user_id
        ).options(
            selectinload(Vocabulary.meanings),
            selectinload(Vocabulary.audios)
        )
        
        if mode == "due":
            # Lấy vocabularies cần ôn (next_review_date <= now)
            query = query.where(Vocabulary.next_review_date <= datetime.utcnow())
        elif mode == "new":
            # Lấy vocabularies mới (repetitions == 0)
            query = query.where(Vocabulary.repetitions == 0)
        
        # Order by next_review_date và limit
        query = query.order_by(Vocabulary.next_review_date.asc()).limit(max_questions)
        
        vocabularies = list(self.session.exec(query).all())
        return vocabularies
    
    def _generate_question(
        self,
        session_id: int,
        user_id: int,
        vocabulary: Vocabulary,
        distractors: List[Vocabulary]
    ) -> GeneratedQuestion:
        """
        Generate một question cho vocabulary.
        
        Args:
            session_id: ID của review session
            user_id: ID của user
            vocabulary: Vocabulary cần generate câu hỏi
            distractors: Danh sách vocabularies khác làm distractor
            
        Returns:
            GeneratedQuestion với snapshot đầy đủ
        """
        # 1. Xác định difficulty dựa trên SRS state
        difficulty = self._calculate_difficulty(vocabulary)
        
        # 2. Chọn strategy
        strategy = QuestionGeneratorFactory.get_strategy(vocabulary, difficulty)
        
        # 3. Generate question data
        question_data = strategy.generate(vocabulary, difficulty, distractors)
        
        # 4. Tạo GeneratedQuestion với snapshot
        question = GeneratedQuestion(
            session_id=session_id,
            user_id=user_id,
            vocabulary_id=vocabulary.id,
            question_type=strategy.get_question_type(),
            difficulty=difficulty,
            question_data=question_data,
            confusion_pair_group=question_data.get("confusion_pair_group"),
        )
        
        return question
    
    def _calculate_difficulty(self, vocabulary: Vocabulary) -> QuestionDifficulty:
        """
        Tính difficulty dựa trên SRS state.
        
        Args:
            vocabulary: Vocabulary cần tính difficulty
            
        Returns:
            QuestionDifficulty
        """
        if vocabulary.repetitions == 0:
            return QuestionDifficulty.EASY
        elif vocabulary.repetitions < 3:
            return QuestionDifficulty.MEDIUM
        else:
            return QuestionDifficulty.HARD
    
    def submit_answer(
        self,
        question_instance_id: str,
        user_answer: str,
        time_spent_ms: int,
        answer_change_count: int
    ) -> Dict[str, Any]:
        """
        Submit câu trả lời cho một question.
        
        Args:
            question_instance_id: UUID của question instance
            user_answer: Câu trả lời của user
            time_spent_ms: Thời gian trả lời (ms)
            answer_change_count: Số lần thay đổi câu trả lời
            
        Returns:
            Dict chứa kết quả evaluation
        """
        # 1. Lấy question
        query = select(GeneratedQuestion).where(
            GeneratedQuestion.question_instance_id == question_instance_id
        )
        question = self.session.exec(query).first()
        
        if not question:
            raise ValueError(f"Question instance {question_instance_id} not found")
        
        # 2. Evaluate answer
        correct_answer = question.question_data["correct_answer"]
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        
        # 3. Update question với answer data
        question.user_answer = user_answer
        question.is_correct = is_correct
        question.time_spent_ms = time_spent_ms
        question.answer_change_count = answer_change_count
        
        self.session.add(question)
        self.session.commit()
        
        # 4. Return result
        result = {
            "question_instance_id": question_instance_id,
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "explanation": question.question_data.get("explanation"),
        }
        
        logger.info(f"Submitted answer for question {question_instance_id}: {'correct' if is_correct else 'incorrect'}")
        return result
    
    def complete_session(self, session_id: int) -> Dict[str, Any]:
        """
        Hoàn thành review session và update SRS cho tất cả vocabularies.
        
        Args:
            session_id: ID của review session
            
        Returns:
            Dict chứa session summary
        """
        # 1. Lấy session với questions
        query = select(ReviewSession).where(
            ReviewSession.id == session_id
        ).options(selectinload(ReviewSession.questions))
        
        session = self.session.exec(query).first()
        
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # 2. Tính toán summary
        total_questions = len(session.questions)
        correct_count = sum(1 for q in session.questions if q.is_correct)
        
        # 3. Update SRS cho từng vocabulary
        for question in session.questions:
            if question.is_correct is not None:  # Đã được answer
                self._update_vocabulary_srs(question)
        
        # 4. Update session status
        session.status = "completed"
        session.correct_count = correct_count
        session.completed_at = datetime.utcnow()
        
        self.session.add(session)
        self.session.commit()
        
        # 5. Return summary
        summary = {
            "session_id": session_id,
            "total_questions": total_questions,
            "correct_count": correct_count,
            "accuracy": correct_count / total_questions if total_questions > 0 else 0,
            "completed_at": session.completed_at,
        }
        
        logger.info(f"Completed session {session_id}: {correct_count}/{total_questions} correct")
        return summary
    
    def _update_vocabulary_srs(self, question: GeneratedQuestion):
        """
        Update SRS state cho vocabulary dựa trên question result.
        
        Args:
            question: GeneratedQuestion đã được answer
        """
        # Lấy vocabulary
        vocab = self.session.get(Vocabulary, question.vocabulary_id)
        if not vocab:
            return
        
        # Map is_correct sang ReviewQuality
        # Dựa vào time_spent để xác định quality
        time_seconds = (question.time_spent_ms or 0) / 1000
        
        if question.is_correct:
            if time_seconds < 5:
                quality = SRSReviewQuality.EASY
            elif time_seconds > 15:
                quality = SRSReviewQuality.HARD
            else:
                quality = SRSReviewQuality.GOOD
        else:
            quality = SRSReviewQuality.AGAIN
        
        # Create SRS state object
        current_state = SRSState(
            easiness_factor=vocab.easiness_factor,
            interval=vocab.interval,
            repetitions=vocab.repetitions,
            next_review_date=vocab.next_review_date
        )
        
        # Update SRS state
        new_state = self.srs_engine.update_after_review(
            current_state=current_state,
            review_quality=quality,
            time_spent_seconds=time_seconds
        )
        
        # Apply new state
        vocab.easiness_factor = new_state.easiness_factor
        vocab.interval = new_state.interval
        vocab.repetitions = new_state.repetitions
        vocab.next_review_date = new_state.next_review_date
        vocab.last_review_date = datetime.utcnow()
        
        self.session.add(vocab)
