import React from 'react';
import { QuestionType, QuestionResponse } from '../../../types/review';
import TypingQuestion from './TypingQuestion';
import MultipleChoiceQuestion from './MultipleChoiceQuestion';
import FillBlankQuestion from './FillBlankQuestion';

interface QuestionRendererProps {
    question: QuestionResponse;
    onSubmit: (answer: string) => void;
    onAnswerChange?: (changeCount: number) => void;
}

const QuestionRenderer: React.FC<QuestionRendererProps> = ({
    question,
    onSubmit,
    onAnswerChange,
}) => {
    switch (question.question_type) {
        case QuestionType.MEANING_INPUT:
            return (
                <div>
                    <div className="text-center mb-10">
                        <span className="inline-block px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-[10px] font-bold uppercase tracking-wider mb-4">
                            Gõ Từ Vựng
                        </span>
                        <h2 className="text-2xl md:text-3xl font-bold text-gray-800 leading-snug mx-auto max-w-2xl">
                            {question.question_text}
                        </h2>
                    </div>
                    <TypingQuestion
                        onSubmit={onSubmit}
                        onAnswerChange={onAnswerChange}
                    />
                </div>
            );

        case QuestionType.FILL_BLANK:
            return (
                <div>
                    <div className="text-center mb-6">
                        <span className="inline-block px-3 py-1 rounded-full bg-green-50 text-green-600 text-[10px] font-bold uppercase tracking-wider">
                            Điền Chỗ Trống
                        </span>
                    </div>
                    <FillBlankQuestion
                        contextSentence={question.context_sentence || ''}
                        onSubmit={onSubmit}
                        onAnswerChange={onAnswerChange}
                    />
                </div>
            );

        case QuestionType.MULTIPLE_CHOICE:
            return (
                <div>
                    <div className="text-center mb-6">
                        <span className="inline-block px-3 py-1 rounded-full bg-purple-50 text-purple-600 text-[10px] font-bold uppercase tracking-wider">
                            Chọn Đáp Án Đúng
                        </span>
                    </div>
                    <MultipleChoiceQuestion
                        options={question.options || []}
                        contextSentence={question.context_sentence}
                        onSelect={onSubmit}
                        onAnswerChange={onAnswerChange}
                    />
                </div>
            );

        case QuestionType.ERROR_DETECTION:
            return (
                <div className="text-center p-12">
                    <p className="text-gray-500">Error Detection - Coming Soon</p>
                </div>
            );

        default:
            return (
                <div className="text-center p-12">
                    <p className="text-red-500">Unknown question type</p>
                </div>
            );
    }
};

export default QuestionRenderer;
