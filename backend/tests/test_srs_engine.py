"""
Unit tests cho SRS Engine module.

Test coverage:
- SRSState dataclass
- calculate_memory_strength
- calculate_next_review
- update_after_review
- Helper functions
"""
import pytest
from datetime import datetime, timedelta
from app.core.srs_engine import (
    SRSEngine,
    SRSState,
    ReviewQuality,
    create_initial_state,
    simulate_review_sequence
)


class TestSRSState:
    """Test SRSState dataclass."""
    
    def test_default_initialization(self):
        """Test khởi tạo với defaults."""
        state = SRSState()
        
        assert state.easiness_factor == 2.5
        assert state.interval == 0
        assert state.repetitions == 0
        assert state.next_review_date is not None
        assert state.last_review_date is None
    
    def test_custom_initialization(self):
        """Test khởi tạo với custom values."""
        review_date = datetime(2026, 2, 5, 12, 0, 0)
        state = SRSState(
            easiness_factor=2.0,
            interval=5,
            repetitions=3,
            next_review_date=review_date
        )
        
        assert state.easiness_factor == 2.0
        assert state.interval == 5
        assert state.repetitions == 3
        assert state.next_review_date == review_date
    
    def test_easiness_factor_clamping_min(self):
        """Test EF bị clamp về minimum 1.3."""
        state = SRSState(easiness_factor=1.0)
        assert state.easiness_factor == 1.3
    
    def test_easiness_factor_clamping_max(self):
        """Test EF bị clamp về maximum 2.5."""
        state = SRSState(easiness_factor=3.0)
        assert state.easiness_factor == 2.5


class TestCalculateMemoryStrength:
    """Test calculate_memory_strength function."""
    
    def test_zero_repetitions(self):
        """Test với repetitions = 0 (chưa học)."""
        strength = SRSEngine.calculate_memory_strength(
            easiness_factor=2.5,
            repetitions=0,
            interval=0
        )
        assert strength == 0.0
    
    def test_first_review(self):
        """Test sau first review."""
        strength = SRSEngine.calculate_memory_strength(
            easiness_factor=2.5,
            repetitions=1,
            interval=1
        )
        assert 0.0 < strength < 0.1
    
    def test_multiple_reviews(self):
        """Test sau nhiều reviews."""
        strength = SRSEngine.calculate_memory_strength(
            easiness_factor=2.5,
            repetitions=5,
            interval=30
        )
        assert 0.3 < strength < 0.6
    
    def test_strength_increases_with_repetitions(self):
        """Test strength tăng theo repetitions."""
        strength1 = SRSEngine.calculate_memory_strength(2.5, 1, 10)
        strength2 = SRSEngine.calculate_memory_strength(2.5, 5, 10)
        strength3 = SRSEngine.calculate_memory_strength(2.5, 10, 10)
        
        assert strength1 < strength2 < strength3
    
    def test_strength_capped_at_one(self):
        """Test strength không vượt quá 1.0."""
        strength = SRSEngine.calculate_memory_strength(
            easiness_factor=2.5,
            repetitions=100,
            interval=1000
        )
        assert strength <= 1.0


class TestCalculateNextReview:
    """Test calculate_next_review function."""
    
    def test_first_review_good(self):
        """Test first review với quality GOOD."""
        state = SRSState(
            easiness_factor=2.5,
            interval=0,
            repetitions=0
        )
        review_time = datetime(2026, 2, 5, 12, 0, 0)
        
        next_review = SRSEngine.calculate_next_review(
            current_state=state,
            review_quality=ReviewQuality.GOOD,
            review_time=review_time
        )
        
        # First review interval = 1 day
        expected = review_time + timedelta(days=1)
        assert next_review == expected
    
    def test_review_again(self):
        """Test review với quality AGAIN (reset)."""
        state = SRSState(
            easiness_factor=2.0,
            interval=10,
            repetitions=5
        )
        review_time = datetime(2026, 2, 5, 12, 0, 0)
        
        next_review = SRSEngine.calculate_next_review(
            current_state=state,
            review_quality=ReviewQuality.AGAIN,
            review_time=review_time
        )
        
        # AGAIN interval = 0 days (review ngay)
        assert next_review == review_time
    
    def test_review_easy(self):
        """Test review với quality EASY."""
        state = SRSState(
            easiness_factor=2.5,
            interval=6,
            repetitions=2
        )
        review_time = datetime(2026, 2, 5, 12, 0, 0)
        
        next_review = SRSEngine.calculate_next_review(
            current_state=state,
            review_quality=ReviewQuality.EASY,
            review_time=review_time
        )
        
        # EASY multiplier = 1.3, so interval = 6 * 2.5 * 1.3 ≈ 20 days
        days_diff = (next_review - review_time).days
        assert 15 <= days_diff <= 25  # Approximate range


class TestUpdateAfterReview:
    """Test update_after_review function (core function)."""
    
    def test_first_review_good(self):
        """Test first review với GOOD quality."""
        state = create_initial_state(datetime(2026, 2, 5, 12, 0, 0))
        review_time = datetime(2026, 2, 5, 12, 0, 0)
        
        new_state = SRSEngine.update_after_review(
            current_state=state,
            review_quality=ReviewQuality.GOOD,
            review_time=review_time
        )
        
        # Check updates
        assert new_state.repetitions == 1
        assert new_state.interval == 1
        assert new_state.last_review_date == review_time
        assert new_state.next_review_date == review_time + timedelta(days=1)
        # GOOD làm giảm EF nhẹ theo SM-2 (q=2 -> EF giảm ~0.32)
        # Nhưng vẫn trong valid range [1.3, 2.5]
        assert 1.3 <= new_state.easiness_factor <= 2.5
    
    def test_second_review_good(self):
        """Test second review với GOOD quality."""
        state = SRSState(
            easiness_factor=2.5,
            interval=1,
            repetitions=1,
            next_review_date=datetime(2026, 2, 6, 12, 0, 0)
        )
        review_time = datetime(2026, 2, 6, 12, 0, 0)
        
        new_state = SRSEngine.update_after_review(
            current_state=state,
            review_quality=ReviewQuality.GOOD,
            review_time=review_time
        )
        
        # Check updates
        assert new_state.repetitions == 2
        assert new_state.interval == 6  # Second review interval = 6
        assert new_state.next_review_date == review_time + timedelta(days=6)
    
    def test_review_again_resets(self):
        """Test AGAIN quality resets progress."""
        state = SRSState(
            easiness_factor=2.0,
            interval=30,
            repetitions=5,
            next_review_date=datetime(2026, 3, 7, 12, 0, 0)
        )
        review_time = datetime(2026, 3, 7, 12, 0, 0)
        
        new_state = SRSEngine.update_after_review(
            current_state=state,
            review_quality=ReviewQuality.AGAIN,
            review_time=review_time
        )
        
        # Check reset
        assert new_state.repetitions == 0
        assert new_state.interval == 0
        assert new_state.next_review_date == review_time
        # EF should decrease
        assert new_state.easiness_factor < state.easiness_factor
    
    def test_review_hard_resets(self):
        """Test HARD quality resets progress."""
        state = SRSState(
            easiness_factor=2.0,
            interval=10,
            repetitions=3,
            next_review_date=datetime(2026, 2, 15, 12, 0, 0)
        )
        review_time = datetime(2026, 2, 15, 12, 0, 0)
        
        new_state = SRSEngine.update_after_review(
            current_state=state,
            review_quality=ReviewQuality.HARD,
            review_time=review_time
        )
        
        # Check reset
        assert new_state.repetitions == 0
        # Interval should be reduced or reset
        assert new_state.interval < state.interval
        # EF should decrease
        assert new_state.easiness_factor < state.easiness_factor
    
    def test_review_easy_increases_interval(self):
        """Test EASY quality increases interval more than GOOD."""
        state = SRSState(
            easiness_factor=2.0,  # Dùng 2.0 để tránh bị clamp ở 2.5 khi tăng
            interval=6,
            repetitions=2,
            next_review_date=datetime(2026, 2, 11, 12, 0, 0)
        )
        review_time = datetime(2026, 2, 11, 12, 0, 0)
        
        new_state_easy = SRSEngine.update_after_review(
            current_state=state,
            review_quality=ReviewQuality.EASY,
            review_time=review_time
        )
        
        new_state_good = SRSEngine.update_after_review(
            current_state=state,
            review_quality=ReviewQuality.GOOD,
            review_time=review_time
        )
        
        # EASY should have longer interval than GOOD
        assert new_state_easy.interval > new_state_good.interval
        # Theo logic mới: EASY (+0.1), GOOD (giữ nguyên)
        assert new_state_easy.easiness_factor > new_state_good.easiness_factor
        assert new_state_easy.easiness_factor > state.easiness_factor
        assert new_state_good.easiness_factor == state.easiness_factor
    
    def test_easiness_factor_bounds(self):
        """Test EF không vượt quá bounds."""
        # Test minimum bound
        state_min = SRSState(easiness_factor=1.3, interval=5, repetitions=2)
        new_state_min = SRSEngine.update_after_review(
            state_min,
            ReviewQuality.AGAIN
        )
        assert new_state_min.easiness_factor >= 1.3
        
        # Test maximum bound
        state_max = SRSState(easiness_factor=2.5, interval=5, repetitions=2)
        new_state_max = SRSEngine.update_after_review(
            state_max,
            ReviewQuality.EASY
        )
        assert new_state_max.easiness_factor <= 2.5
    
    def test_immutability(self):
        """Test update không modify original state."""
        original_state = SRSState(
            easiness_factor=2.0,
            interval=5,
            repetitions=2
        )
        original_ef = original_state.easiness_factor
        original_interval = original_state.interval
        original_reps = original_state.repetitions
        
        new_state = SRSEngine.update_after_review(
            original_state,
            ReviewQuality.GOOD
        )
        
        # Original state should not change
        assert original_state.easiness_factor == original_ef
        assert original_state.interval == original_interval
        assert original_state.repetitions == original_reps


class TestIsDueForReview:
    """Test is_due_for_review function."""
    
    def test_past_date_is_due(self):
        """Test với past date."""
        past_date = datetime.utcnow() - timedelta(days=1)
        assert SRSEngine.is_due_for_review(past_date) is True
    
    def test_future_date_not_due(self):
        """Test với future date."""
        future_date = datetime.utcnow() + timedelta(days=1)
        assert SRSEngine.is_due_for_review(future_date) is False
    
    def test_current_time_is_due(self):
        """Test với current time."""
        current_time = datetime.utcnow()
        assert SRSEngine.is_due_for_review(current_time, current_time) is True


class TestGetRetentionRate:
    """Test get_retention_rate function."""
    
    def test_perfect_retention(self):
        """Test với 100% retention."""
        rate = SRSEngine.get_retention_rate(10, 10)
        assert rate == 1.0
    
    def test_zero_retention(self):
        """Test với 0% retention."""
        rate = SRSEngine.get_retention_rate(10, 0)
        assert rate == 0.0
    
    def test_partial_retention(self):
        """Test với partial retention."""
        rate = SRSEngine.get_retention_rate(10, 8)
        assert rate == 0.8
    
    def test_no_reviews(self):
        """Test với no reviews."""
        rate = SRSEngine.get_retention_rate(0, 0)
        assert rate == 0.0


class TestHelperFunctions:
    """Test helper functions."""
    
    def test_create_initial_state(self):
        """Test create_initial_state."""
        state = create_initial_state()
        
        assert state.easiness_factor == 2.5
        assert state.interval == 0
        assert state.repetitions == 0
        assert state.next_review_date is not None
        assert state.last_review_date is None
    
    def test_create_initial_state_custom_date(self):
        """Test create_initial_state với custom date."""
        custom_date = datetime(2026, 2, 10, 12, 0, 0)
        state = create_initial_state(custom_date)
        
        assert state.next_review_date == custom_date
    
    def test_simulate_review_sequence(self):
        """Test simulate_review_sequence."""
        state = create_initial_state(datetime(2026, 2, 5, 12, 0, 0))
        qualities = [
            ReviewQuality.GOOD,
            ReviewQuality.GOOD,
            ReviewQuality.EASY
        ]
        
        states = simulate_review_sequence(state, qualities)
        
        assert len(states) == 3
        assert states[0].repetitions == 1
        assert states[1].repetitions == 2
        assert states[2].repetitions == 3
        
        # Intervals should increase
        assert states[0].interval == 1
        assert states[1].interval == 6
        assert states[2].interval > states[1].interval


class TestReviewSequenceScenarios:
    """Test realistic review scenarios."""
    
    def test_perfect_learner_sequence(self):
        """Test sequence của perfect learner (all EASY)."""
        state = create_initial_state(datetime(2026, 2, 1, 12, 0, 0))
        qualities = [ReviewQuality.EASY] * 5
        
        states = simulate_review_sequence(state, qualities)
        
        # Should have increasing intervals
        intervals = [s.interval for s in states]
        assert intervals == sorted(intervals)
        
        # EF sẽ giảm dần theo SM-2 (EASY q=3 vẫn làm giảm EF ~0.14 mỗi lần)
        # Nhưng vẫn trong valid range và cao hơn nếu dùng GOOD
        assert states[-1].easiness_factor >= 1.3
        
        # Should have 5 repetitions
        assert states[-1].repetitions == 5
    
    def test_struggling_learner_sequence(self):
        """Test sequence của struggling learner (mix AGAIN/HARD/GOOD)."""
        state = create_initial_state(datetime(2026, 2, 1, 12, 0, 0))
        qualities = [
            ReviewQuality.GOOD,
            ReviewQuality.AGAIN,  # Forgot
            ReviewQuality.GOOD,
            ReviewQuality.HARD,   # Difficult
            ReviewQuality.GOOD,
            ReviewQuality.GOOD
        ]
        
        states = simulate_review_sequence(state, qualities)
        
        # After AGAIN, repetitions should reset
        assert states[1].repetitions == 0
        
        # After HARD, repetitions should reset
        assert states[3].repetitions == 0
        
        # EF should decrease over time
        assert states[-1].easiness_factor < state.easiness_factor
    
    def test_gradual_improvement_sequence(self):
        """Test sequence với gradual improvement."""
        state = create_initial_state(datetime(2026, 2, 1, 12, 0, 0))
        qualities = [
            ReviewQuality.HARD,
            ReviewQuality.GOOD,
            ReviewQuality.GOOD,
            ReviewQuality.EASY,
            ReviewQuality.EASY
        ]
        
        states = simulate_review_sequence(state, qualities)
        
        # Should eventually build up repetitions
        assert states[-1].repetitions > 0
        
        # Should have reasonable interval
        assert states[-1].interval > 0


# ============= Integration Tests =============

class TestIntegration:
    """Integration tests cho toàn bộ workflow."""
    
    def test_full_learning_cycle(self):
        """Test full learning cycle từ new word đến mastered."""
        # Start with new word
        state = create_initial_state(datetime(2026, 2, 1, 12, 0, 0))
        
        # First review - GOOD
        state = SRSEngine.update_after_review(
            state,
            ReviewQuality.GOOD,
            datetime(2026, 2, 1, 12, 0, 0)
        )
        assert state.repetitions == 1
        assert state.interval == 1
        
        # Second review - GOOD (after 1 day)
        state = SRSEngine.update_after_review(
            state,
            ReviewQuality.GOOD,
            datetime(2026, 2, 2, 12, 0, 0)
        )
        assert state.repetitions == 2
        assert state.interval == 6
        
        # Third review - EASY (after 6 days)
        state = SRSEngine.update_after_review(
            state,
            ReviewQuality.EASY,
            datetime(2026, 2, 8, 12, 0, 0)
        )
        assert state.repetitions == 3
        assert state.interval > 6
        
        # Check memory strength
        strength = SRSEngine.calculate_memory_strength(
            state.easiness_factor,
            state.repetitions,
            state.interval
        )
        assert strength > 0.1
    
    def test_forgetting_and_relearning(self):
        """Test forgetting và relearning cycle."""
        # Build up some progress
        state = create_initial_state(datetime(2026, 2, 1, 12, 0, 0))
        state = SRSEngine.update_after_review(
            state, ReviewQuality.GOOD, datetime(2026, 2, 1, 12, 0, 0)
        )
        state = SRSEngine.update_after_review(
            state, ReviewQuality.GOOD, datetime(2026, 2, 2, 12, 0, 0)
        )
        
        # Forget it
        state = SRSEngine.update_after_review(
            state, ReviewQuality.AGAIN, datetime(2026, 2, 8, 12, 0, 0)
        )
        assert state.repetitions == 0
        assert state.interval == 0
        
        # Relearn
        state = SRSEngine.update_after_review(
            state, ReviewQuality.GOOD, datetime(2026, 2, 8, 12, 0, 0)
        )
        assert state.repetitions == 1
        assert state.interval == 1


class TestSRSEdgeCases:
    """Các trường hợp biên và đặc biệt của SRS Engine."""

    def test_extreme_ef_recovery(self):
        """Test khả năng hồi phục EF sau khi bị giảm xuống minimum."""
        # Tình huống: EF cực thấp (1.3)
        state = SRSState(easiness_factor=1.3, interval=1, repetitions=1)
        
        # Learner bắt đầu làm tốt (EASY) liên tục
        for _ in range(5):
            state = SRSEngine.update_after_review(state, ReviewQuality.EASY)
        
        # EF nên tăng trở lại (nhưng không vượt quá 2.5)
        assert state.easiness_factor > 1.3
        assert state.easiness_factor <= 2.5

    def test_very_large_interval(self):
        """Test xử lý với interval cực lớn (phòng trường hợp overflow hoặc lỗi ngày tháng)."""
        state = SRSState(easiness_factor=2.5, interval=365*10, repetitions=50) # 10 năm
        
        new_state = SRSEngine.update_after_review(state, ReviewQuality.GOOD)
        
        assert new_state.interval > state.interval
        assert (new_state.next_review_date - datetime.utcnow()).days > 3650

    def test_minimum_ef_clamping(self):
        """Xác minh EF không bao giờ thấp hơn 1.3 kể cả khi liên tục FAIL."""
        state = create_initial_state()
        for _ in range(10):
            state = SRSEngine.update_after_review(state, ReviewQuality.AGAIN)
        
        assert state.easiness_factor == 1.3
