import React, { useState } from 'react';

import { stripThinkTags } from '../../../utils/textUtils';

interface MultipleChoiceQuestionProps {
    options: string[];
    contextSentence?: string;
    onSelect: (answer: string) => void;
    onAnswerChange?: (changeCount: number) => void;
    disabled?: boolean;
}

const MultipleChoiceQuestion: React.FC<MultipleChoiceQuestionProps> = ({
    options,
    contextSentence: rawContextSentence,
    onSelect,
    onAnswerChange,
    disabled = false
}) => {
    // Filter out <think> blocks
    const contextSentence = rawContextSentence ? stripThinkTags(rawContextSentence) : undefined;

    const [selectedOption, setSelectedOption] = useState<string | null>(null);
    const [changeCount, setChangeCount] = useState(0);

    const handleSelect = (option: string) => {
        if (disabled) return;

        // Track change if user changes selection
        if (selectedOption !== null && selectedOption !== option) {
            const newChangeCount = changeCount + 1;
            setChangeCount(newChangeCount);
            if (onAnswerChange) {
                onAnswerChange(newChangeCount);
            }
        }

        setSelectedOption(option);
        onSelect(option);
    };

    return (
        <div className="w-full max-w-2xl mx-auto">
            {/* Context Sentence (nếu có) */}
            {contextSentence && (
                <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-100">
                    <p className="text-xl md:text-2xl text-gray-800 leading-relaxed text-center font-medium">
                        {contextSentence}
                    </p>
                </div>
            )}

            {/* Options Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {options.map((option, index) => (
                    <button
                        key={index}
                        onClick={() => handleSelect(option)}
                        disabled={disabled}
                        className={`
                            p-6 rounded-2xl border-2 bg-white 
                            hover:border-indigo-500 hover:bg-indigo-50 hover:shadow-md
                            active:scale-[0.98] transition-all duration-200
                            text-lg font-medium text-left
                            flex items-center gap-3
                            disabled:opacity-60 disabled:hover:bg-white disabled:hover:border-gray-100 disabled:active:scale-100
                            ${selectedOption === option ? 'border-indigo-500 bg-indigo-50' : 'border-gray-100'}
                        `}
                    >
                        <span className={`
                            flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg text-sm font-bold
                            ${selectedOption === option ? 'bg-indigo-200 text-indigo-700' : 'bg-gray-100 text-gray-500'}
                        `}>
                            {String.fromCharCode(65 + index)}
                        </span>
                        <span className="flex-grow text-gray-700">{option}</span>
                    </button>
                ))}
            </div>
        </div>
    );
};

export default MultipleChoiceQuestion;
