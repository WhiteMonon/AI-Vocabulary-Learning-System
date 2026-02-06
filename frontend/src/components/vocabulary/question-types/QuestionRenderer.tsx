import React from 'react';
import { QuestionType, QuestionResponse } from '../../../types/review';
import TypingQuestion from './TypingQuestion';
import MultipleChoiceQuestion from './MultipleChoiceQuestion';
import FillBlankQuestion from './FillBlankQuestion';
import DictationQuestion from './DictationQuestion';

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
        // ============ TYPING TYPES ============
        case QuestionType.MEANING_INPUT:
        case QuestionType.WORD_FROM_MEANING:
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

        case QuestionType.MEANING_FROM_WORD:
            return (
                <div>
                    <div className="text-center mb-10">
                        <span className="inline-block px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-[10px] font-bold uppercase tracking-wider mb-4">
                            Nhập Nghĩa
                        </span>
                        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 leading-snug mx-auto mb-2">
                            {question.word || question.question_text.replace("What does '", "").replace("' mean?", "")}
                        </h2>
                        <p className="text-gray-500">Hãy nhập nghĩa của từ này</p>
                    </div>
                    <TypingQuestion
                        onSubmit={onSubmit}
                        onAnswerChange={onAnswerChange}
                    />
                </div>
            );

        case QuestionType.DICTATION:
            return (
                <div>
                    <div className="text-center mb-6">
                        <span className="inline-block px-3 py-1 rounded-full bg-pink-50 text-pink-600 text-[10px] font-bold uppercase tracking-wider mb-4">
                            Nghe & Chép Chính Tả
                        </span>
                    </div>
                    <DictationQuestion
                        audioUrl={question.audio_url || ''}
                        onSubmit={onSubmit}
                        onAnswerChange={onAnswerChange}
                    />
                </div>
            );

        // ============ FILL BLANK ============
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

        // ============ MCQ TYPES ============
        case QuestionType.MULTIPLE_CHOICE:
        case QuestionType.SYNONYM_ANTONYM_MCQ:
        case QuestionType.DEFINITION_MCQ:
            let badgeColor = "bg-purple-50 text-purple-600";
            let badgeText = "Chọn Đáp Án Đúng";

            if (question.question_type === QuestionType.SYNONYM_ANTONYM_MCQ) {
                badgeColor = "bg-orange-50 text-orange-600";
                badgeText = "Đồng Nghĩa / Trái Nghĩa";
            } else if (question.question_type === QuestionType.DEFINITION_MCQ) {
                badgeColor = "bg-teal-50 text-teal-600";
                badgeText = "Chọn Định Nghĩa";
            }

            return (
                <div>
                    <div className="text-center mb-6">
                        <span className={`inline-block px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${badgeColor}`}>
                            {badgeText}
                        </span>
                        {(question.question_type === QuestionType.SYNONYM_ANTONYM_MCQ || question.question_type === QuestionType.DEFINITION_MCQ) && (
                            <h2 className="text-xl md:text-2xl font-bold text-gray-800 mt-4 mb-2 max-w-2xl mx-auto">
                                {question.question_text}
                            </h2>
                        )}
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
                    <p className="text-red-500">Unknown question type: {question.question_type}</p>
                </div>
            );
    }
};

export default QuestionRenderer;
