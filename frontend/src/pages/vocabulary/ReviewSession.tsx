import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getVocabularies, reviewVocabulary } from '../../api/vocabulary';
import { ReviewQuality, VocabularyReview } from '../../types/vocabulary';
import Timer from '../../components/vocabulary/Timer';
import ReviewFeedback from '../../components/vocabulary/ReviewFeedback';
import { ReviewResultItem } from './ReviewResults';

const ReviewSession: React.FC = () => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [currentIndex, setCurrentIndex] = useState(0);
    const [userAnswer, setUserAnswer] = useState('');
    const [showFeedback, setShowFeedback] = useState(false);
    const [isCorrect, setIsCorrect] = useState(false);
    const [startTime, setStartTime] = useState<number>(Date.now());
    const [sessionStartTime] = useState<number>(Date.now());
    const [reviewResults, setReviewResults] = useState<ReviewResultItem[]>([]);
    const inputRef = useRef<HTMLInputElement>(null);

    // Fetch due vocabularies
    const { data: vocabResponse, isLoading, error } = useQuery({
        queryKey: ['vocabularies', 'due'],
        queryFn: () => getVocabularies({ status: 'DUE', page_size: 50 }),
    });

    const vocabList = vocabResponse?.items || [];
    const currentVocab = vocabList[currentIndex];

    // Review mutation
    const reviewMutation = useMutation({
        mutationFn: ({ id, review }: { id: number; review: VocabularyReview }) =>
            reviewVocabulary(id, review),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vocabularies'] });
            queryClient.invalidateQueries({ queryKey: ['vocabulary-stats'] });
        },
    });

    useEffect(() => {
        if (!showFeedback && inputRef.current) {
            inputRef.current.focus();
        }
    }, [showFeedback, currentIndex]);

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
                <p className="text-gray-600">Đang chuẩn bị phiên ôn tập...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <p className="text-red-500 mb-4">Đã có lỗi xảy ra khi tải dữ liệu.</p>
                <button onClick={() => navigate('/')} className="text-indigo-600 hover:underline">
                    Quay lại Dashboard
                </button>
            </div>
        );
    }

    if (vocabList.length === 0) {
        return (
            <div className="max-w-md mx-auto text-center py-12 bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
                <div className="text-5xl mb-6">🎉</div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Tuyệt vời!</h2>
                <p className="text-gray-600 mb-8">Bạn đã hoàn thành hết tất cả các từ cần ôn tập cho hôm nay.</p>
                <button
                    onClick={() => navigate('/')}
                    className="w-full py-3 px-4 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition-colors"
                >
                    Quay lại Dashboard
                </button>
            </div>
        );
    }

    const handleSubmit = (e?: React.FormEvent) => {
        if (e) e.preventDefault();
        if (showFeedback || !userAnswer.trim()) return;

        const correct = userAnswer.trim().toLowerCase() === currentVocab.word.toLowerCase();
        setIsCorrect(correct);
        setShowFeedback(true);
    };

    const handleNext = (quality: ReviewQuality) => {
        const timeSpent = Math.floor((Date.now() - startTime) / 1000);

        // Lưu kết quả câu hiện tại
        const resultItem: ReviewResultItem = {
            id: currentVocab.id,
            word: currentVocab.word,
            definition: currentVocab.meanings?.[0]?.definition || '',
            userAnswer: userAnswer,
            isCorrect: isCorrect,
            timeSpent: timeSpent,
        };
        const updatedResults = [...reviewResults, resultItem];
        setReviewResults(updatedResults);

        reviewMutation.mutate({
            id: currentVocab.id,
            review: {
                review_quality: quality,
                time_spent_seconds: timeSpent
            }
        });

        if (currentIndex < vocabList.length - 1) {
            setCurrentIndex(currentIndex + 1);
            setUserAnswer('');
            setShowFeedback(false);
            setStartTime(Date.now());
        } else {
            // End of session - navigate đến trang kết quả
            const totalTime = Math.floor((Date.now() - sessionStartTime) / 1000);
            navigate('/vocabulary/review/results', {
                state: {
                    results: updatedResults,
                    totalTime: totalTime
                }
            });
        }
    };

    const progress = ((currentIndex) / vocabList.length) * 100;

    return (
        <div className="max-w-2xl mx-auto py-8 px-4">
            {/* Progress breadcrumbs/header */}
            <div className="flex justify-between items-center mb-8">
                <button
                    onClick={() => navigate('/')}
                    className="text-gray-500 hover:text-gray-700 flex items-center gap-1"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
                    </svg>
                    Thoát
                </button>
                <div className="text-sm font-medium text-gray-500">
                    Từ {currentIndex + 1} / {vocabList.length}
                </div>
            </div>

            {/* Main Review Card */}
            <div className="bg-white rounded-3xl shadow-xl shadow-indigo-100/50 border border-indigo-50 overflow-hidden transition-all duration-500">
                {/* Progress Bar */}
                <div className="w-full bg-gray-100 h-1.5">
                    <div
                        className="bg-indigo-500 h-full transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                    ></div>
                </div>

                <div className="p-8 md:p-12">
                    {/* Timer */}
                    <div className="mb-8">
                        <Timer
                            duration={20}
                            isActive={!showFeedback}
                            onTimeUp={() => {
                                if (!showFeedback) {
                                    setIsCorrect(false);
                                    setShowFeedback(true);
                                }
                            }}
                        />
                    </div>

                    {/* Word Display (Definition) */}
                    <div className="text-center mb-10">
                        <span className="inline-block px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 text-xs font-bold uppercase tracking-wider mb-4">
                            Định nghĩa
                        </span>
                        <h2 className="text-3xl md:text-4xl font-bold text-gray-800 leading-tight">
                            {currentVocab.meanings?.[0]?.definition || "N/A"}
                        </h2>
                        {currentVocab.meanings?.[0]?.example_sentence && (
                            <p className="mt-4 text-gray-500 italic">
                                "{currentVocab.meanings[0].example_sentence.replace(currentVocab.word, '_______')}"
                            </p>
                        )}
                    </div>

                    {/* Input or Feedback */}
                    {!showFeedback ? (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="relative">
                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={userAnswer}
                                    onChange={(e) => setUserAnswer(e.target.value)}
                                    placeholder="Nhập từ vựng..."
                                    className="w-full px-6 py-4 bg-gray-50 border-2 border-gray-100 rounded-2xl focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 transition-all outline-none text-xl text-center font-medium"
                                    autoComplete="off"
                                    autoFocus
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={!userAnswer.trim()}
                                className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold text-lg hover:bg-indigo-700 active:scale-[0.98] transition-all shadow-lg shadow-indigo-200 disabled:opacity-50 disabled:shadow-none disabled:active:scale-100"
                            >
                                Kiểm tra
                            </button>
                        </form>
                    ) : (
                        <ReviewFeedback
                            isCorrect={isCorrect}
                            correctAnswer={currentVocab.word}
                            onNext={handleNext}
                        />
                    )}
                </div>
            </div>

            {/* Shortcuts hint */}
            <div className="mt-8 text-center text-gray-400 text-sm">
                Tip: Nhấn <kbd className="px-2 py-1 bg-gray-100 rounded border border-gray-200">Enter</kbd> để kiểm tra nhanh
            </div>
        </div>
    );
};

export default ReviewSession;
