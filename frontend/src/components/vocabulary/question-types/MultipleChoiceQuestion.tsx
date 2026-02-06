import React from 'react';

interface MultipleChoiceQuestionProps {
    options: string[];
    onSelect: (answer: string) => void;
    disabled?: boolean;
}

const MultipleChoiceQuestion: React.FC<MultipleChoiceQuestionProps> = ({
    options,
    onSelect,
    disabled = false
}) => {
    // Local state to track selection for UI effect before submission (optional) or just direct submit
    // Here we'll do direct submit on click for speed, or we can add a "selected" state.
    // For "speed review", direct click is usually better.

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl mx-auto">
            {options.map((option, index) => (
                <button
                    key={index}
                    onClick={() => onSelect(option)}
                    disabled={disabled}
                    className="
                        p-6 rounded-2xl border-2 border-gray-100 bg-white 
                        hover:border-indigo-500 hover:bg-indigo-50 hover:shadow-md
                        active:scale-[0.98] transition-all duration-200
                        text-lg font-medium text-gray-700 text-left
                        flex items-center gap-3
                        disabled:opacity-60 disabled:hover:bg-white disabled:hover:border-gray-100 disabled:active:scale-100
                    "
                >
                    <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-gray-100 text-gray-500 text-sm font-bold group-hover:bg-indigo-200 group-hover:text-indigo-700">
                        {String.fromCharCode(65 + index)}
                    </span>
                    <span className="flex-grow">{option}</span>
                </button>
            ))}
        </div>
    );
};

export default MultipleChoiceQuestion;
