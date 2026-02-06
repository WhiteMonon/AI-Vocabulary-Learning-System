import pytest
from app.ai.utils import strip_reasoning

def test_strip_reasoning_basic():
    text = "Hello world <think>I should say hello</think> how are you?"
    expected = "Hello world  how are you?"
    assert strip_reasoning(text) == expected.strip()

def test_strip_reasoning_multiline():
    text = "Line 1\n<think>\nReasoning line 1\nReasoning line 2\n</think>\nLine 2"
    expected = "Line 1\n\nLine 2"
    assert strip_reasoning(text) == expected.strip()

def test_strip_reasoning_multiple():
    text = "<think>R1</think>Part 1<think>R2</think>Part 2"
    expected = "Part 1Part 2"
    assert strip_reasoning(text) == expected.strip()

def test_strip_reasoning_unclosed():
    # Bây giờ strip_reasoning xử lý được cả thẻ không đóng
    # Nó sẽ loại bỏ tất cả nội dung từ <think> đến cuối chuỗi
    text = "Hello <think> reasoning..."
    expected = "Hello"
    assert strip_reasoning(text) == expected.strip()

def test_strip_reasoning_none_empty():
    assert strip_reasoning(None) == ""
    assert strip_reasoning("") == ""
    assert strip_reasoning("   ") == ""
