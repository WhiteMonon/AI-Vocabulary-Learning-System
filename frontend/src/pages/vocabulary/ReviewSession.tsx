import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getVocabularies, batchReviewVocabularies, BatchReviewRequest } from '../../api/vocabulary';
import { ReviewQuality, Vocabulary } from '../../types/vocabulary';
import TypingQuestion from '../../components/vocabulary/question-types/TypingQuestion';
import MultipleChoiceQuestion from '../../components/vocabulary/question-types/MultipleChoiceQuestion';
import ComboCounter from '../../components/gamification/ComboCounter';
import { ReviewResultItem } from './ReviewResults';
import useReviewTimer from '../../hooks/useReviewTimer';

type QuestionType = 'TYPING' | 'MULTIPLE_CHOICE';

interface QuestionItem {
    vocab: Vocabulary;
    type: QuestionType;
    distractors: string[]; // For MCQ
}

const ReviewSession: React.FC = () => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    // Game State
    const [currentIndex, setCurrentIndex] = useState(0);
    const [combo, setCombo] = useState(0);
    const [score, setScore] = useState(0);
    const [userAnswer, setUserAnswer] = useState('');

    // Internal State for Evaluation
    const [reviewResults, setReviewResults] = useState<ReviewResultItem[]>([]);
    const [reviewItems, setReviewItems] = useState<{ vocabulary_id: number, review_quality: ReviewQuality, time_spent_seconds: number }[]>([]);

    // Time Tracking
    const { elapsed, reset: resetTimer, stop: stopTimer } = useReviewTimer(true);
    const [sessionStartTime] = useState<number>(Date.now());

    // Data
    const [questions, setQuestions] = useState<QuestionItem[]>([]);

    // Fetch due vocabularies
    const { data: vocabResponse, isLoading, error } = useQuery({
        queryKey: ['vocabularies', 'due'],
        queryFn: () => getVocabularies({ status: 'DUE', page_size: 20 }),
        refetchOnWindowFocus: false,
    });

    const vocabList = vocabResponse?.items || [];

    // Prepare Questions (Randomize Type & Distractors)
    useEffect(() => {
        if (vocabList.length > 0 && questions.length === 0) {
            const newQuestions: QuestionItem[] = vocabList.map(vocab => {
                let type: QuestionType = 'TYPING';
                const isNew = vocab.repetitions === 0;

                if (isNew) {
                    type = Math.random() > 0.3 ? 'MULTIPLE_CHOICE' : 'TYPING';
                } else {
                    type = Math.random() > 0.7 ? 'MULTIPLE_CHOICE' : 'TYPING';
                }

                const otherWords = vocabList
                    .filter(v => v.id !== vocab.id)
                    .map(v => v.word);

                const shuffled = otherWords.sort(() => 0.5 - Math.random());
                const distractors = shuffled.slice(0, 3);

                while (distractors.length < 3) {
                    distractors.push("apple"); // Fallback
                }

                return {
                    vocab,
                    type,
                    distractors
                };
            });
            setQuestions(newQuestions);
            resetTimer(true);
        }
    }, [vocabList, questions.length, resetTimer]);

    // Current Question
    const currentQuestion = questions[currentIndex];

    // MCQ Options
    const mcqOptions = useMemo(() => {
        if (!currentQuestion) return [];
        const opts = [...currentQuestion.distractors, currentQuestion.vocab.word];
        return opts.sort(() => 0.5 - Math.random());
    }, [currentQuestion]);


    // Batch Review mutation
    const batchMutation = useMutation({
        mutationFn: (data: BatchReviewRequest) => batchReviewVocabularies(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vocabularies'] });
            queryClient.invalidateQueries({ queryKey: ['vocabulary-stats'] });
        },
    });

    // Handle Submission/Next
    const handleNext = useCallback((answer: string) => {
        if (!currentQuestion) return;

        // 1. Capture Data
        const timeSpent = elapsed;
        const correct = answer.trim().toLowerCase() === currentQuestion.vocab.word.toLowerCase();

        // 2. Calculate Quality Internal
        let quality = ReviewQuality.GOOD;
        if (!correct) {
            quality = ReviewQuality.AGAIN;
        } else {
            if (timeSpent < 5) quality = ReviewQuality.EASY;
            else if (timeSpent > 15) quality = ReviewQuality.HARD;
            else quality = ReviewQuality.GOOD;
        }

        // 3. Update Game State (Combo/Score) - Internal Feedback Only
        if (correct) {
            setCombo(prev => prev + 1);
            setScore(prev => prev + 10 + (combo * 2));
        } else {
            setCombo(0);
        }

        // 4. Store Result
        const resultItem: ReviewResultItem = {
            id: currentQuestion.vocab.id,
            word: currentQuestion.vocab.word,
            definition: currentQuestion.vocab.meanings?.[0]?.definition || '',
            userAnswer: answer,
            isCorrect: correct,
            timeSpent: timeSpent,
        };

        const reviewItem = {
            vocabulary_id: currentQuestion.vocab.id,
            review_quality: quality,
            time_spent_seconds: timeSpent
        };

        const nextResults = [...reviewResults, resultItem];
        const nextReviewItems = [...reviewItems, reviewItem];

        setReviewResults(nextResults);
        setReviewItems(nextReviewItems);

        // 5. Navigate or Finish
        if (currentIndex < questions.length - 1) {
            setCurrentIndex(prev => prev + 1);
            setUserAnswer('');
            resetTimer(true); // STRICT RESET
        } else {
            // Finish Session
            stopTimer();
            const totalTime = Math.floor((Date.now() - sessionStartTime) / 1000);

            // Submitting to backend implicitly? 
            // The requirement says "Review Screen... sau khi user làm xong". 
            // Ideally we submit in background or show a loading state on the Results screen.
            // Let's call mutation here and navigate on success or pass data to results page to submit?
            // To ensure data consistency, let's submit here.

            const batchRequest: BatchReviewRequest = {
                items: nextReviewItems
            };

            batchMutation.mutate(batchRequest, {
                onSuccess: () => {
                    navigate('/vocabulary/review/results', {
                        state: {
                            results: nextResults,
                            totalTime: totalTime,
                            score: score + (correct ? 10 + (combo * 2) : 0) // Include last question score update logic approximation
                        }
                    });
                },
                onError: () => {
                    // Fallback: still go to results but show error? 
                    // Or just go to results and let results page handle retry?
                    // For now, let's just go to results with local data so user doesn't lose progress visually
                    navigate('/vocabulary/review/results', {
                        state: {
                            results: nextResults,
                            totalTime: totalTime,
                            score: score,
                            error: "Submission failed"
                        }
                    });
                }
            });
        }
    }, [currentQuestion, elapsed, reviewResults, reviewItems, currentIndex, questions.length, sessionStartTime, combo, score, resetTimer, stopTimer, batchMutation, navigate]);


    // ----- Render States -----

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
                <p className="text-gray-600">Đang chuẩn bị phiên ôn tập...</p>
            </div>
        );
    }

    if (error) return <div className="text-red-500 text-center py-12">Lỗi tải dữ liệu.</div>;

    if (vocabList.length === 0) {
        return (
            <div className="max-w-md mx-auto text-center py-12 bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
                <div className="text-5xl mb-6">🎉</div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Tuyệt vời!</h2>
                <p className="text-gray-600 mb-8">Bạn đã hoàn thành hết tất cả các từ cần ôn tập.</p>
                <button onClick={() => navigate('/')} className="w-full py-3 px-4 bg-indigo-600 text-white rounded-xl font-semibold">
                    Quay lại Dashboard
                </button>
            </div>
        );
    }

    if (!currentQuestion) return null;

    const progress = ((currentIndex) / questions.length) * 100;

    return (
        <div className="max-w-3xl mx-auto py-6 px-4 relative">

            {/* Combo Counter Overlay */}
            <ComboCounter combo={combo} />

            {/* Header */}
            <div className="flex justify-between items-center mb-6">
                <button onClick={() => navigate('/')} className="text-gray-400 hover:text-gray-600 transition-colors">
                    ✕ Thoát
                </button>
                <div className="flex flex-col items-end">
                    <span className="text-sm font-bold text-gray-600">
                        {currentIndex + 1} / {questions.length}
                    </span>
                    <span className="text-xs text-indigo-500 font-medium">Score: {score}</span>
                </div>
            </div>

            {/* Main Card */}
            <div className="bg-white rounded-3xl shadow-2xl shadow-indigo-100 overflow-hidden relative min-h-[500px] flex flex-col">
                {/* Progress Bar */}
                <div className="h-1.5 bg-gray-100 w-full">
                    <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-300 ease-out"
                        style={{ width: `${progress}%` }}
                    />
                </div>

                {/* Submitting Overlay */}
                {batchMutation.isPending && (
                    <div className="absolute inset-0 bg-white/80 z-50 flex items-center justify-center backdrop-blur-sm">
                        <div className="flex flex-col items-center">
                            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mb-4"></div>
                            <p className="text-gray-600 font-medium">Đang lưu kết quả...</p>
                        </div>
                    </div>
                )}

                <div className="p-8 md:p-12 flex-grow flex flex-col items-center justify-center">

                    {/* Timer (Visual Only - Logic is via hook) */}
                    <div className="mb-8">
                        {/* We use a key to force re-mounting timer visual if needed, 
                            but the hook controls validation logic. 
                            The visual Timer component might have its own internal state, 
                            so passing `elapsed` or key is important to sync visuals.
                        */}
                        <div className="relative font-mono text-2xl font-bold text-indigo-600 bg-indigo-50 w-16 h-16 rounded-full flex items-center justify-center border-4 border-indigo-100">
                            {elapsed}
                        </div>
                    </div>

                    {/* Question Content */}
                    <div className="text-center mb-10 w-full">
                        <span className="inline-block px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-[10px] font-bold uppercase tracking-wider mb-4">
                            {currentQuestion.type === 'MULTIPLE_CHOICE' ? 'Chọn Nghĩa Đúng' : 'Gõ Từ Vựng'}
                        </span>

                        <h2 className="text-2xl md:text-3xl font-bold text-gray-800 leading-snug mx-auto max-w-2xl">
                            {currentQuestion.vocab.meanings?.[0]?.definition || "N/A"}
                        </h2>
                    </div>

                    {/* Interactive Area */}
                    <div className="w-full">
                        {currentQuestion.type === 'TYPING' && (
                            <TypingQuestion
                                key={`typing-${currentIndex}`}
                                word={currentQuestion.vocab.word}
                                userAnswer={userAnswer}
                                setUserAnswer={setUserAnswer}
                                onSubmit={handleNext} // Direct submit, no feedback step
                            />
                        )}
                        {currentQuestion.type === 'MULTIPLE_CHOICE' && (
                            <MultipleChoiceQuestion
                                key={`mcq-${currentIndex}`}
                                options={mcqOptions}
                                onSelect={handleNext} // Direct select
                            />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReviewSession;
