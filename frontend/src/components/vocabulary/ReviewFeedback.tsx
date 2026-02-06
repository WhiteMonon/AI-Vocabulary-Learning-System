import React, { useEffect, useRef } from 'react';
import { ReviewQuality } from '../../types/vocabulary';
import { CheckCircle, XCircle, FastForward, Clock } from 'lucide-react';

interface ReviewFeedbackProps {
    isCorrect: boolean;
    correctAnswer: string;
    autoGrade: ReviewQuality;
    timeSpent: number;
    onNext: (quality: ReviewQuality) => void;
}

const ReviewFeedback: React.FC<ReviewFeedbackProps> = ({
    isCorrect,
    correctAnswer,
    autoGrade,
    timeSpent,
    onNext
}) => {
    const nextButtonRef = useRef<HTMLButtonElement>(null);

    // Auto-focus next button
    useEffect(() => {
        if (nextButtonRef.current) {
            nextButtonRef.current.focus();
        }
    }, []);

    const getGradeLabel = (quality: ReviewQuality) => {
        switch (quality) {
            case ReviewQuality.AGAIN: return { text: "Cần học lại", color: "text-red-700", bg: "bg-red-100" };
            case ReviewQuality.HARD: return { text: "Khó", color: "text-orange-700", bg: "bg-orange-100" };
            case ReviewQuality.GOOD: return { text: "Tốt", color: "text-blue-700", bg: "bg-blue-100" };
            case ReviewQuality.EASY: return { text: "Dễ dàng", color: "text-green-700", bg: "bg-green-100" };
            default: return { text: "???", color: "text-gray-700", bg: "bg-gray-100" };
        }
    };

    const gradeInfo = getGradeLabel(autoGrade);

    return (
        <div className={`p-8 rounded-3xl border-2 ${isCorrect ? 'bg-green-50/50 border-green-200' : 'bg-red-50/50 border-red-200'} transition-all duration-300 animate-in fade-in zoom-in slide-in-from-bottom-4 shadow-xl`}>

            {/* Status Header */}
            <div className="text-center mb-8">
                <div className="flex items-center justify-center gap-3 mb-4">
                    {isCorrect ? (
                        <CheckCircle className="w-12 h-12 text-green-600 drop-shadow-sm" />
                    ) : (
                        <XCircle className="w-12 h-12 text-red-600 drop-shadow-sm" />
                    )}
                </div>

                <h3 className={`text-3xl font-black mb-2 ${isCorrect ? 'text-green-800' : 'text-red-800'}`}>
                    {isCorrect ? 'Chính xác!' : 'Chưa đúng'}
                </h3>

                {!isCorrect && (
                    <div className="mt-4 p-4 bg-white rounded-xl border border-red-100 shadow-sm">
                        <p className="text-gray-500 text-sm font-medium uppercase tracking-wide mb-1">Đáp án đúng</p>
                        <p className="text-2xl font-bold text-gray-800">{correctAnswer}</p>
                    </div>
                )}
            </div>

            {/* Auto-Grade Info */}
            <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-gray-100 shadow-sm mb-8">
                <div className="flex items-center gap-3">
                    <Clock className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-600 font-medium">{timeSpent}s</span>
                </div>
                <div className="h-8 w-px bg-gray-200"></div>
                <div className={`px-4 py-1.5 rounded-lg font-bold text-sm flex items-center gap-2 ${gradeInfo.bg} ${gradeInfo.color}`}>
                    <span>Đánh giá:</span>
                    <span className="uppercase tracking-wider">{gradeInfo.text}</span>
                </div>
            </div>

            {/* Primary Action */}
            <button
                ref={nextButtonRef}
                onClick={() => onNext(autoGrade)}
                className={`w-full py-4 text-white rounded-2xl font-bold text-lg shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2 ${isCorrect ? 'bg-green-600 hover:bg-green-700 shadow-green-200' : 'bg-red-600 hover:bg-red-700 shadow-red-200'
                    }`}
            >
                <span>Tiếp tục</span>
                <FastForward className="w-5 h-5 opacity-80" />
            </button>
            <div className="text-center mt-3 text-gray-400 text-xs font-medium">Nhấn Enter để tiếp tục</div>

            {/* Overrides (Collapsed/Small) */}
            <div className="mt-8 pt-6 border-t border-gray-200/50">
                <p className="text-center text-xs text-gray-400 font-medium mb-3 uppercase tracking-wider">Hoặc chọn thủ công</p>
                <div className="flex justify-center gap-3">
                    <button onClick={() => onNext(ReviewQuality.AGAIN)} className="px-3 py-2 rounded-lg bg-white border border-gray-200 text-xs font-bold text-gray-500 hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors">
                        Quên (Again)
                    </button>
                    <button onClick={() => onNext(ReviewQuality.HARD)} className="px-3 py-2 rounded-lg bg-white border border-gray-200 text-xs font-bold text-gray-500 hover:bg-orange-50 hover:text-orange-600 hover:border-orange-200 transition-colors">
                        Khó (Hard)
                    </button>
                    <button onClick={() => onNext(ReviewQuality.EASY)} className="px-3 py-2 rounded-lg bg-white border border-gray-200 text-xs font-bold text-gray-500 hover:bg-green-50 hover:text-green-600 hover:border-green-200 transition-colors">
                        Dễ (Easy)
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ReviewFeedback;
