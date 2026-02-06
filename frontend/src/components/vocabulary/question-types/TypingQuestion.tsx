import React, { useRef, useEffect } from 'react';

interface TypingQuestionProps {
    word: string; // The word to type (needed for validation logic if moved here, but currently just for display if needed)
    userAnswer: string;
    setUserAnswer: (value: string) => void;
    onSubmit: (answer: string) => void;
    disabled?: boolean;
}

const TypingQuestion: React.FC<TypingQuestionProps> = ({
    userAnswer,
    setUserAnswer,
    onSubmit,
    disabled = false
}) => {
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (!disabled && inputRef.current) {
            inputRef.current.focus();
        }
    }, [disabled]);

    return (
        <div className="w-full max-w-lg mx-auto space-y-6">
            <div className="relative">
                <input
                    ref={inputRef}
                    type="text"
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && userAnswer.trim()) {
                            onSubmit(userAnswer);
                        }
                    }}
                    placeholder="Nhập từ vựng..."
                    disabled={disabled}
                    className="w-full px-6 py-4 bg-gray-50 border-2 border-gray-100 rounded-2xl focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 transition-all outline-none text-xl text-center font-medium disabled:opacity-60 disabled:bg-gray-100"
                    autoComplete="off"
                    autoFocus
                />
            </div>

            <button
                onClick={() => onSubmit(userAnswer)}
                disabled={disabled || !userAnswer.trim()}
                className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold text-lg hover:bg-indigo-700 active:scale-[0.98] transition-all shadow-lg shadow-indigo-200 disabled:opacity-50 disabled:shadow-none disabled:active:scale-100"
            >
                Kiểm tra
            </button>

            <div className="text-center text-gray-400 text-sm">
                Nhấn <kbd className="font-sans px-2 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs mx-1">Enter</kbd> để nộp bài
            </div>
        </div>
    );
};

export default TypingQuestion;
