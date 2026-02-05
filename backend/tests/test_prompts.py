from app.ai import prompts
from app.models.enums import PracticeType

def test_prompt_formatting():
    # Test Multiple Choice
    p1 = prompts.MULTIPLE_CHOICE_GEN.format(word="apple", definition="a fruit")
    assert "apple" in p1
    assert "a fruit" in p1
    
    # Test Fill Blank
    p2 = prompts.FILL_BLANK_GEN.format(word="banana", definition="long yellow fruit")
    assert "banana" in p2
    assert "long yellow fruit" in p2

    # Test Grammar Eval
    p3 = prompts.GRAMMAR_EVAL.format(question="Q", expected="E", answer="A")
    assert "Q" in p3
    assert "E" in p3
    assert "A" in p3

    # Test Explanation
    p4 = prompts.VOCAB_EXPLANATION.format(word="cherry", definition="small red fruit")
    assert "cherry" in p4
    assert "small red fruit" in p4

if __name__ == "__main__":
    test_prompt_formatting()
    print("All prompt formatting tests passed!")
