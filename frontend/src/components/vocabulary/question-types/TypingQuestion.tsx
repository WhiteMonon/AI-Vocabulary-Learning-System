import React, { useRef, useEffect, useState } from 'react';

interface TypingQuestionProps {
    onSubmit: (answer: string) => void;
    onAnswerChange?: (changeCount: number) => void;
    disabled?: boolean;
}

const TypingQuestion: React.FC<TypingQuestionProps> = ({
    onSubmit,
    onAnswerChange,
    disabled = false
}) => {
    const inputRef = useRef<HTMLInputElement>(null);
    const [answer, setAnswer] = useState('');
    const [changeCount, setChangeCount] = useState(0);

    useEffect(() => {
        if (!disabled && inputRef.current) {
            inputRef.current.focus();
        }
    }, [disabled]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setAnswer(newValue);

        // Track change count
        const newChangeCount = changeCount + 1;
        setChangeCount(newChangeCount);
        if (onAnswerChange) {
            onAnswerChange(newChangeCount);
        }
    };

    return (
        <div className="w-full max-w-lg mx-auto space-y-6">
            <div className="relative">
                <input
                    ref={inputRef}
                    type="text"
                    value={answer}
                    onChange={handleChange}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && answer.trim()) {
                            onSubmit(answer.trim());
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
                onClick={() => onSubmit(answer.trim())}
                disabled={disabled || !answer.trim()}
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
