import React, { useState } from 'react';

import { stripThinkTags } from '../../../utils/textUtils';

interface FillBlankQuestionProps {
    contextSentence: string;
    onSubmit: (answer: string) => void;
    onAnswerChange?: (changeCount: number) => void;
}

const FillBlankQuestion: React.FC<FillBlankQuestionProps> = ({
    contextSentence: rawContextSentence,
    onSubmit,
    onAnswerChange,
}) => {
    // Filter out <think> blocks
    const contextSentence = stripThinkTags(rawContextSentence);

    const [answer, setAnswer] = useState('');
    const [changeCount, setChangeCount] = useState(0);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newAnswer = e.target.value;
        setAnswer(newAnswer);

        // Track change count
        const newChangeCount = changeCount + 1;
        setChangeCount(newChangeCount);
        if (onAnswerChange) {
            onAnswerChange(newChangeCount);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (answer.trim()) {
            onSubmit(answer.trim());
        }
    };

    return (
        <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
            {/* Context Sentence */}
            <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-100">
                <p className="text-xl md:text-2xl text-gray-800 leading-relaxed text-center font-medium">
                    {contextSentence.split('___').map((part, index, array) => (
                        <React.Fragment key={index}>
                            {part}
                            {index < array.length - 1 && (
                                <span className="inline-block mx-2 px-4 py-1 bg-white border-2 border-dashed border-indigo-300 rounded-lg text-indigo-600 font-bold">
                                    ___
                                </span>
                            )}
                        </React.Fragment>
                    ))}
                </p>
            </div>

            {/* Input Field */}
            <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-600 mb-2">
                    Điền từ vào chỗ trống:
                </label>
                <input
                    type="text"
                    value={answer}
                    onChange={handleChange}
                    placeholder="Nhập từ..."
                    className="w-full px-6 py-4 text-lg border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all"
                    autoFocus
                />
            </div>

            {/* Submit Button */}
            <button
                type="submit"
                disabled={!answer.trim()}
                className="w-full py-4 px-6 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold rounded-xl hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
            >
                Xác nhận
            </button>
        </form>
    );
};

export default FillBlankQuestion;
