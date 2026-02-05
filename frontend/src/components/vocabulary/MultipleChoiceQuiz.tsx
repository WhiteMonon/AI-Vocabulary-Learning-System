import React, { useState } from 'react';
import { QuizQuestion } from '../../types/vocabulary';

interface MultipleChoiceQuizProps {
    question: QuizQuestion;
    onNext: (isCorrect: boolean) => void;
}

const MultipleChoiceQuiz: React.FC<MultipleChoiceQuizProps> = ({ question, onNext }) => {
    const [selectedOption, setSelectedOption] = useState<string | null>(null);
    const [showFeedback, setShowFeedback] = useState(false);

    const handleOptionSelect = (key: string) => {
        if (showFeedback) return;
        setSelectedOption(key);
    };

    const handleSubmit = () => {
        if (!selectedOption) return;
        setShowFeedback(true);
    };

    const isCorrect = selectedOption === question.correct_answer;

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Question Text */}
            <div className="text-center">
                <span className="inline-block px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-xs font-bold uppercase tracking-wider mb-4">
                    Câu hỏi trắc nghiệm
                </span>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-800 leading-tight">
                    {question.question_text}
                </h2>
            </div>

            {/* Options Grid */}
            <div className="grid grid-cols-1 gap-4">
                {Object.entries(question.options).map(([key, value]) => {
                    const isSelected = selectedOption === key;
                    const isAnswerCorrect = key === question.correct_answer;

                    let bgColor = 'bg-gray-50';
                    let borderColor = 'border-gray-100';
                    let textColor = 'text-gray-700';

                    if (showFeedback) {
                        if (isAnswerCorrect) {
                            bgColor = 'bg-green-50';
                            borderColor = 'border-green-500';
                            textColor = 'text-green-700';
                        } else if (isSelected && !isAnswerCorrect) {
                            bgColor = 'bg-red-50';
                            borderColor = 'border-red-500';
                            textColor = 'text-red-700';
                        }
                    } else if (isSelected) {
                        bgColor = 'bg-indigo-50';
                        borderColor = 'border-indigo-500';
                        textColor = 'text-indigo-700';
                    }

                    return (
                        <button
                            key={key}
                            onClick={() => handleOptionSelect(key)}
                            disabled={showFeedback}
                            className={`
                                flex items-center p-5 rounded-2xl border-2 transition-all text-left
                                ${bgColor} ${borderColor} ${textColor}
                                ${!showFeedback ? 'hover:border-indigo-300 hover:bg-indigo-50/30' : ''}
                                ${isSelected ? 'ring-4 ring-indigo-500/10' : ''}
                            `}
                        >
                            <span className={`
                                w-10 h-10 rounded-xl flex items-center justify-center font-bold mr-4 text-lg
                                ${isSelected ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-200'}
                                ${showFeedback && isAnswerCorrect ? 'bg-green-600 text-white' : ''}
                                ${showFeedback && isSelected && !isAnswerCorrect ? 'bg-red-600 text-white' : ''}
                            `}>
                                {key}
                            </span>
                            <span className="text-lg font-medium">{value}</span>
                        </button>
                    );
                })}
            </div>

            {/* AI Explanation & Grammar */}
            {showFeedback && (
                <div className="space-y-6 animate-in zoom-in-95 fade-in duration-500">
                    <div className={`p-6 rounded-3xl border-2 ${isCorrect ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
                        <div className="flex items-start gap-4">
                            <div className={`p-2 rounded-xl ${isCorrect ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                                {isCorrect ? (
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                    </svg>
                                ) : (
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                )}
                            </div>
                            <div>
                                <h3 className={`font-bold text-lg mb-1 ${isCorrect ? 'text-green-800' : 'text-red-800'}`}>
                                    {isCorrect ? 'Tuyệt vời, bạn đã chọn đúng!' : 'Cố gắng lên, đáp án chưa chính xác.'}
                                </h3>
                                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                                    {question.explanation}
                                </p>
                            </div>
                        </div>
                    </div>

                    {question.grammar_explanation && (
                        <div className="p-6 rounded-3xl bg-indigo-50 border-2 border-indigo-100">
                            <div className="flex items-start gap-4">
                                <div className="p-2 rounded-xl bg-indigo-100 text-indigo-600 text-xl">
                                    💡
                                </div>
                                <div>
                                    <h3 className="font-bold text-indigo-900 text-lg mb-1">Ghi chú ngữ pháp</h3>
                                    <p className="text-indigo-800 leading-relaxed whitespace-pre-wrap">
                                        {question.grammar_explanation}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    <button
                        onClick={() => onNext(isCorrect)}
                        className="w-full py-5 bg-indigo-600 text-white rounded-2xl font-bold text-xl hover:bg-indigo-700 active:scale-[0.98] transition-all shadow-xl shadow-indigo-200"
                    >
                        Tiếp tục
                    </button>
                </div>
            )}

            {!showFeedback && (
                <button
                    onClick={handleSubmit}
                    disabled={!selectedOption}
                    className="w-full py-5 bg-indigo-600 text-white rounded-2xl font-bold text-xl hover:bg-indigo-700 active:scale-[0.98] transition-all shadow-xl shadow-indigo-200 disabled:opacity-50"
                >
                    Kiểm tra đáp án
                </button>
            )}
        </div>
    );
};

export default MultipleChoiceQuiz;
