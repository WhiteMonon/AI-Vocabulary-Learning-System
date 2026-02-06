"""
SRS (Spaced Repetition System) Engine Module.

Pure Python module implementing hybrid SM-2 simplified algorithm.
Testable independently without database or FastAPI dependencies.

Algorithm: Hybrid SM-2 Simplified
- Based on SuperMemo 2 (SM-2) algorithm
- Simplified for easier understanding and maintenance
- Hybrid approach combining quality-based and performance-based adjustments
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple
from enum import IntEnum


class ReviewQuality(IntEnum):
    """
    Chất lượng review theo SM-2 algorithm.
    
    Values:
        AGAIN (0): Hoàn toàn quên, cần review lại ngay
        HARD (1): Nhớ khó khăn, cần review sớm
        GOOD (2): Nhớ tốt, review theo schedule bình thường
        EASY (3): Nhớ rất dễ, có thể kéo dài interval
    """
    AGAIN = 0
    HARD = 1
    GOOD = 2
    EASY = 3


@dataclass
class SRSState:
    """
    Trạng thái SRS của một vocabulary item.
    
    Attributes:
        easiness_factor: Hệ số dễ dàng (EF), range [1.3, 2.5], default 2.5
        interval: Khoảng thời gian đến lần review tiếp theo (ngày)
        repetitions: Số lần review thành công liên tiếp
        next_review_date: Ngày review tiếp theo
        last_review_date: Ngày review lần cuối (optional)
    """
    easiness_factor: float = 2.5
    interval: int = 0
    repetitions: int = 0
    next_review_date: datetime = None
    last_review_date: datetime = None
    
    def __post_init__(self):
        """Validate và set defaults."""
        if self.easiness_factor < 1.3:
            self.easiness_factor = 1.3
        if self.easiness_factor > 2.5:
            self.easiness_factor = 2.5
        if self.next_review_date is None:
            self.next_review_date = datetime.utcnow()


class SRSEngine:
    """
    SRS Engine implementing hybrid SM-2 simplified algorithm.
    
    Pure Python class, không phụ thuộc vào external dependencies.
    """
    
    # Constants cho algorithm
    MIN_EASINESS_FACTOR = 1.3
    MAX_EASINESS_FACTOR = 2.5
    DEFAULT_EASINESS_FACTOR = 2.5
    
    # Interval multipliers cho different qualities
    AGAIN_MULTIPLIER = 0.0  # Reset về 0
    HARD_MULTIPLIER = 0.5   # Giảm interval
    GOOD_MULTIPLIER = 1.0   # Giữ nguyên
    EASY_MULTIPLIER = 1.3   # Tăng interval
    
    @staticmethod
    def calculate_memory_strength(
        easiness_factor: float,
        repetitions: int,
        interval: int
    ) -> float:
        """
        Tính memory strength (độ mạnh của memory) dựa trên SRS state.
        
        Memory strength là một metric để đánh giá mức độ "thuộc" của vocabulary.
        Range: 0.0 (chưa học) đến 1.0 (thuộc rất vững)
        
        Formula:
            strength = min(1.0, (repetitions * easiness_factor * log(interval + 1)) / 100)
        
        Args:
            easiness_factor: Hệ số dễ dàng (1.3 - 2.5)
            repetitions: Số lần review thành công
            interval: Interval hiện tại (ngày)
            
        Returns:
            Memory strength (0.0 - 1.0)
            
        Examples:
            >>> SRSEngine.calculate_memory_strength(2.5, 0, 0)
            0.0
            >>> SRSEngine.calculate_memory_strength(2.5, 5, 30)
            0.425...
        """
        if repetitions == 0:
            return 0.0
        
        # Sử dụng logarithm để smooth growth
        import math
        log_interval = math.log(interval + 1)
        
        # Calculate raw strength
        raw_strength = (repetitions * easiness_factor * log_interval) / 100.0
        
        # Clamp to [0.0, 1.0]
        return min(1.0, max(0.0, raw_strength))
    
    @staticmethod
    def calculate_next_review(
        current_state: SRSState,
        review_quality: ReviewQuality,
        review_time: datetime = None
    ) -> datetime:
        """
        Tính next review date dựa trên current state và review quality.
        
        Đây là helper function để preview next review date mà không update state.
        
        Args:
            current_state: SRS state hiện tại
            review_quality: Chất lượng review (0-3)
            review_time: Thời điểm review (default: now)
            
        Returns:
            Next review datetime
            
        Examples:
            >>> state = SRSState(easiness_factor=2.5, interval=0, repetitions=0)
            >>> quality = ReviewQuality.GOOD
            >>> next_date = SRSEngine.calculate_next_review(state, quality)
            >>> # next_date sẽ là 1 ngày sau review_time
        """
        if review_time is None:
            review_time = datetime.utcnow()
        
        # Tính repetitions mới (giống logic trong update_after_review)
        if review_quality.value < ReviewQuality.GOOD:
            new_repetitions = 0
        else:
            new_repetitions = current_state.repetitions + 1
            
        # Tính easiness factor mới (giống logic trong update_after_review)
        new_ef = SRSEngine._calculate_new_easiness_factor(
            current_ef=current_state.easiness_factor,
            quality=review_quality
        )
        
        # Calculate new interval (không update state)
        new_interval = SRSEngine._calculate_new_interval(
            current_interval=current_state.interval,
            repetitions=new_repetitions,
            easiness_factor=new_ef,
            quality=review_quality
        )
        
        # Calculate next review date
        next_review = review_time + timedelta(days=new_interval)
        
        return next_review
    
    @staticmethod
    def update_after_review(
        current_state: SRSState,
        review_quality: ReviewQuality,
        review_time: datetime = None,
        time_spent_seconds: int = 0
    ) -> SRSState:
        """
        Update SRS state sau khi review (core function).
        
        Implement hybrid SM-2 simplified algorithm:
        1. Adjust quality based on response time (Speed Bonus/Penalty)
        2. Update easiness factor dựa trên adjusted quality
        3. Update repetitions (reset nếu quality < GOOD)
        4. Calculate new interval
        5. Update next review date
        
        Response Time Logic:
        - Fast (< 5s) & Correct: Bonus (GOOD -> EASY)
        - Slow (> 15s) & Correct: Penalty (EASY -> GOOD, GOOD -> HARD)
        
        Args:
            current_state: SRS state hiện tại
            review_quality: Chất lượng review (0-3)
            review_time: Thời điểm review (default: now)
            time_spent_seconds: Thời gian trả lời (giây)
            
        Returns:
            SRS state mới sau khi update
        """
        if review_time is None:
            review_time = datetime.utcnow()
            
        # --- Speed Adjustment ---
        adjusted_quality = review_quality
        
        # Chỉ adjust nếu trả lời đúng (GOOD/EASY)
        if review_quality >= ReviewQuality.GOOD:
            if time_spent_seconds > 0: # Valid time
                if time_spent_seconds < 5:
                    # Siêu nhanh: Bonus GOOD -> EASY
                    if review_quality == ReviewQuality.GOOD:
                        adjusted_quality = ReviewQuality.EASY
                elif time_spent_seconds > 15:
                    # Chậm: Penalty
                    if review_quality == ReviewQuality.EASY:
                        adjusted_quality = ReviewQuality.GOOD
                    elif review_quality == ReviewQuality.GOOD:
                        adjusted_quality = ReviewQuality.HARD
        
        # Create new state (immutable pattern)
        new_state = SRSState(
            easiness_factor=current_state.easiness_factor,
            interval=current_state.interval,
            repetitions=current_state.repetitions,
            next_review_date=current_state.next_review_date,
            last_review_date=review_time
        )
        
        # Step 1: Update easiness factor (use adjusted_quality)
        new_state.easiness_factor = SRSEngine._calculate_new_easiness_factor(
            current_ef=current_state.easiness_factor,
            quality=adjusted_quality
        )
        
        # Step 2: Update repetitions
        if adjusted_quality.value < ReviewQuality.GOOD:
            # Reset nếu quality < GOOD (AGAIN hoặc HARD)
            new_state.repetitions = 0
        else:
            # Increment nếu quality >= GOOD
            new_state.repetitions = current_state.repetitions + 1
        
        # Step 3: Calculate new interval
        new_state.interval = SRSEngine._calculate_new_interval(
            current_interval=current_state.interval,
            repetitions=new_state.repetitions,
            easiness_factor=new_state.easiness_factor,
            quality=adjusted_quality
        )
        
        # Step 4: Update next review date
        new_state.next_review_date = review_time + timedelta(days=new_state.interval)
        
        return new_state
    
    @staticmethod
    def _calculate_new_easiness_factor(
        current_ef: float,
        quality: ReviewQuality
    ) -> float:
        """
        Tính easiness factor mới dựa trên quality.
        
        Formula (SM-2):
            EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        
        Simplified:
            - AGAIN (0): EF -= 0.2
            - HARD (1): EF -= 0.15
            - GOOD (2): EF không đổi (0)
            - EASY (3): EF += 0.15 (Modified: Slightly higher reward for Easy)
        
        Args:
            current_ef: Easiness factor hiện tại
            quality: Review quality (0-3)
            
        Returns:
            New easiness factor (clamped to [1.3, 2.5])
        """
        q = quality.value
        
        # Logic simplified cho thang điểm 0-3:
        # AGAIN (0): EF -= 0.2
        # HARD (1): EF -= 0.15
        # GOOD (2): EF không đổi (0)
        # EASY (3): EF += 0.1
        
        if q == 0:
            new_ef = current_ef - 0.2
        elif q == 1:
            new_ef = current_ef - 0.15
        elif q == 2:
            new_ef = current_ef
        else:  # q == 3 (EASY)
            new_ef = current_ef + 0.15  # Tăng bonus cho Easy lên 0.15
        
        # Clamp to valid range
        new_ef = max(SRSEngine.MIN_EASINESS_FACTOR, new_ef)
        new_ef = min(SRSEngine.MAX_EASINESS_FACTOR, new_ef)
        
        return new_ef
    
    @staticmethod
    def _calculate_new_interval(
        current_interval: int,
        repetitions: int,
        easiness_factor: float,
        quality: ReviewQuality
    ) -> int:
        """
        Tính interval mới dựa trên repetitions và quality.
        
        Logic:
            - AGAIN: interval = 0 (review ngay)
            - HARD: interval = max(1, current_interval * 0.5) nếu reps > 0, else 0
            - GOOD/EASY:
                - First review (reps=1): interval = 1
                - Second review (reps=2): interval = 6
                - Subsequent: interval = previous_interval * EF * quality_multiplier
        
        Args:
            current_interval: Interval hiện tại
            repetitions: Số repetitions MỚI (đã được update)
            easiness_factor: Easiness factor
            quality: Review quality
            
        Returns:
            New interval (days)
        """
        # AGAIN: reset về 0
        if quality == ReviewQuality.AGAIN:
            return 0
        
        # HARD: giảm interval hoặc reset
        if quality == ReviewQuality.HARD:
            if repetitions == 0:
                return 0
            else:
                # Giảm interval xuống 50%
                return max(1, int(current_interval * SRSEngine.HARD_MULTIPLIER))
        
        # GOOD hoặc EASY
        if repetitions == 0:
            # Shouldn't happen (vì GOOD/EASY sẽ increment reps)
            # Nhưng handle edge case
            return 0
        elif repetitions == 1:
            # First successful review
            return 1
        elif repetitions == 2:
            # Second successful review
            return 6
        else:
            # Subsequent reviews: apply SM-2 formula
            multiplier = (
                SRSEngine.EASY_MULTIPLIER 
                if quality == ReviewQuality.EASY 
                else SRSEngine.GOOD_MULTIPLIER
            )
            
            new_interval = current_interval * easiness_factor * multiplier
            
            # Round và ensure minimum 1 day
            return max(1, round(new_interval))
    
    @staticmethod
    def is_due_for_review(
        next_review_date: datetime,
        current_time: datetime = None
    ) -> bool:
        """
        Kiểm tra xem vocabulary có cần review không.
        
        Args:
            next_review_date: Ngày review tiếp theo
            current_time: Thời điểm hiện tại (default: now)
            
        Returns:
            True nếu cần review, False nếu chưa đến lúc
            
        Examples:
            >>> from datetime import timedelta
            >>> past_date = datetime.utcnow() - timedelta(days=1)
            >>> SRSEngine.is_due_for_review(past_date)
            True
            >>> future_date = datetime.utcnow() + timedelta(days=1)
            >>> SRSEngine.is_due_for_review(future_date)
            False
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        return next_review_date <= current_time
    
    @staticmethod
    def get_retention_rate(
        total_reviews: int,
        successful_reviews: int
    ) -> float:
        """
        Tính retention rate (tỷ lệ nhớ).
        
        Args:
            total_reviews: Tổng số lần review
            successful_reviews: Số lần review thành công (quality >= GOOD)
            
        Returns:
            Retention rate (0.0 - 1.0)
            
        Examples:
            >>> SRSEngine.get_retention_rate(10, 8)
            0.8
            >>> SRSEngine.get_retention_rate(0, 0)
            0.0
        """
        if total_reviews == 0:
            return 0.0
        
        return successful_reviews / total_reviews


# ============= Helper Functions =============

def create_initial_state(initial_review_date: datetime = None) -> SRSState:
    """
    Tạo initial SRS state cho vocabulary mới.
    
    Args:
        initial_review_date: Ngày có thể review lần đầu (default: now)
        
    Returns:
        SRSState với defaults
        
    Examples:
        >>> state = create_initial_state()
        >>> state.easiness_factor
        2.5
        >>> state.repetitions
        0
    """
    if initial_review_date is None:
        initial_review_date = datetime.utcnow()
    
    return SRSState(
        easiness_factor=SRSEngine.DEFAULT_EASINESS_FACTOR,
        interval=0,
        repetitions=0,
        next_review_date=initial_review_date,
        last_review_date=None
    )


def simulate_review_sequence(
    initial_state: SRSState,
    qualities: list[ReviewQuality],
    start_time: datetime = None
) -> list[SRSState]:
    """
    Simulate một chuỗi reviews để test algorithm.
    
    Useful cho testing và visualization.
    
    Args:
        initial_state: SRS state ban đầu
        qualities: List các review qualities
        start_time: Thời điểm bắt đầu (default: now)
        
    Returns:
        List các SRS states sau mỗi review
        
    Examples:
        >>> state = create_initial_state()
        >>> qualities = [ReviewQuality.GOOD, ReviewQuality.GOOD, ReviewQuality.EASY]
        >>> states = simulate_review_sequence(state, qualities)
        >>> len(states)
        3
        >>> states[-1].repetitions
        3
    """
    if start_time is None:
        start_time = datetime.utcnow()
    
    states = []
    current_state = initial_state
    current_time = start_time
    
    for quality in qualities:
        # Review tại next_review_date
        current_time = current_state.next_review_date
        
        # Update state
        new_state = SRSEngine.update_after_review(
            current_state=current_state,
            review_quality=quality,
            review_time=current_time
        )
        
        states.append(new_state)
        current_state = new_state
    
    return states
