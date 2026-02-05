import React from 'react';
import { ReviewQuality } from '../../types/vocabulary';

interface ReviewFeedbackProps {
    isCorrect: boolean;
    correctAnswer: string;
    onNext: (quality: ReviewQuality) => void;
}

const ReviewFeedback: React.FC<ReviewFeedbackProps> = ({ isCorrect, correctAnswer, onNext }) => {
    return (
        <div className={`p-6 rounded-xl border-2 ${isCorrect ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'} transition-all duration-300 animate-in fade-in zoom-in slide-in-from-bottom-4`}>
            <div className="text-center mb-6">
                <h3 className={`text-2xl font-bold mb-2 ${isCorrect ? 'text-green-700' : 'text-red-700'}`}>
                    {isCorrect ? 'Chính xác! 🎉' : 'Chưa đúng rồi! 😅'}
                </h3>
                {!isCorrect && (
                    <p className="text-gray-600">
                        Đáp án đúng là: <span className="font-bold text-gray-800 underline decoration-red-400">{correctAnswer}</span>
                    </p>
                )}
            </div>

            <div className="grid grid-cols-2 gap-4">
                <button
                    onClick={() => onNext(ReviewQuality.AGAIN)}
                    className="flex flex-col items-center justify-center p-3 rounded-lg border border-red-300 bg-white hover:bg-red-50 text-red-600 transition-colors shadow-sm"
                >
                    <span className="font-bold">Học lại</span>
                    <span className="text-xs">Quên hẳn</span>
                </button>
                <button
                    onClick={() => onNext(ReviewQuality.HARD)}
                    className="flex flex-col items-center justify-center p-3 rounded-lg border border-orange-300 bg-white hover:bg-orange-50 text-orange-600 transition-colors shadow-sm"
                >
                    <span className="font-bold">Khó</span>
                    <span className="text-xs">Nhớ lờ mờ</span>
                </button>
                <button
                    onClick={() => onNext(ReviewQuality.GOOD)}
                    className="flex flex-col items-center justify-center p-3 rounded-lg border border-blue-300 bg-white hover:bg-blue-50 text-blue-600 transition-colors shadow-sm"
                >
                    <span className="font-bold">Tốt</span>
                    <span className="text-xs">Phải suy nghĩ</span>
                </button>
                <button
                    onClick={() => onNext(ReviewQuality.EASY)}
                    className="flex flex-col items-center justify-center p-3 rounded-lg border border-green-300 bg-white hover:bg-green-50 text-green-600 transition-colors shadow-sm"
                >
                    <span className="font-bold">Dễ</span>
                    <span className="text-xs">Nhớ ngay lập tức</span>
                </button>
            </div>
        </div>
    );
};

export default ReviewFeedback;
