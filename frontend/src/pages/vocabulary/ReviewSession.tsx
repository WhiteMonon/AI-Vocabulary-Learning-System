import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { createReviewSession, submitReviewAnswers } from '../../api/review';
import { QuestionResponse, QuestionSubmission } from '../../types/review';
import QuestionRenderer from '../../components/vocabulary/question-types/QuestionRenderer';
import ComboCounter from '../../components/gamification/ComboCounter';
import { ReviewResultItem } from './ReviewResults';

const ReviewSession: React.FC = () => {
    const navigate = useNavigate();

    // Session State
    const [sessionId, setSessionId] = useState<number | null>(null);
    const [questions, setQuestions] = useState<QuestionResponse[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);

    // Tracking State
    const [submissions, setSubmissions] = useState<QuestionSubmission[]>([]);
    const [reviewResults, setReviewResults] = useState<ReviewResultItem[]>([]);
    const [questionStartTime, setQuestionStartTime] = useState<number>(Date.now());
    const [sessionStartTime] = useState<number>(Date.now());
    const answerChangeCountRef = useRef(0);

    // Game State
    const [combo, setCombo] = useState(0);
    const [score, setScore] = useState(0);

    // Create Session Mutation
    const createSessionMutation = useMutation({
        mutationFn: createReviewSession,
        onSuccess: (data) => {
            setSessionId(data.session_id);
            setQuestions(data.questions);
            setQuestionStartTime(Date.now());
        },
    });

    // Submit Answers Mutation
    const submitMutation = useMutation({
        mutationFn: (data: { sessionId: number; submissions: QuestionSubmission[] }) =>
            submitReviewAnswers(data.sessionId, { submissions: data.submissions }),
        onSuccess: (response) => {
            const totalTime = Math.floor((Date.now() - sessionStartTime) / 1000);

            // Cập nhật kết quả với data thực tế từ backend
            const finalResults = reviewResults.map((res, index) => {
                const backendRes = response.results[index];
                if (backendRes) {
                    return {
                        ...res,
                        isCorrect: backendRes.is_correct,
                        word: backendRes.correct_answer, // Hiển thị từ đúng nếu user trả lời sai
                    };
                }
                return res;
            });

            navigate('/vocabulary/review/results', {
                state: {
                    results: finalResults,
                    totalTime: totalTime,
                    score: score,
                    summary: response.session_summary,
                },
            });
        },
        onError: () => {
            // Fallback: go to results with local data
            const totalTime = Math.floor((Date.now() - sessionStartTime) / 1000);
            navigate('/vocabulary/review/results', {
                state: {
                    results: reviewResults,
                    totalTime: totalTime,
                    score: score,
                    error: 'Submission failed',
                },
            });
        },
    });

    // Initialize Session
    useEffect(() => {
        createSessionMutation.mutate({ mode: 'due', max_questions: 20 });
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Current Question
    const currentQuestion = questions[currentIndex];

    // Handle Answer Change (for telemetry)
    const handleAnswerChange = useCallback((changeCount: number) => {
        answerChangeCountRef.current = changeCount;
    }, []);

    // Handle Submit Answer
    const handleSubmit = useCallback(
        (answer: string) => {
            if (!currentQuestion || !sessionId) return;

            // Calculate time spent
            const timeSpentMs = Date.now() - questionStartTime;

            // Create submission
            const submission: QuestionSubmission = {
                question_instance_id: currentQuestion.question_instance_id,
                user_answer: answer,
                time_spent_ms: timeSpentMs,
                answer_change_count: answerChangeCountRef.current,
            };

            // Store submission (will be sent in batch at the end)
            const newSubmissions = [...submissions, submission];
            setSubmissions(newSubmissions);

            // For local feedback, we need to know if correct
            // Backend will evaluate, but we can show immediate feedback
            // For now, we'll just move to next question
            // (In production, you might want to show feedback before moving)

            // Update game state (placeholder - we don't know correctness yet)
            // We'll update this after backend response
            // For now, assume correct for combo/score
            setCombo((prev) => prev + 1);
            setScore((prev) => prev + 10 + combo * 2);

            // Store result for display (we'll update with backend result later)
            const resultItem: ReviewResultItem = {
                id: currentQuestion.vocabulary_id,
                word: answer, // Placeholder
                definition: currentQuestion.question_text,
                userAnswer: answer,
                isCorrect: true, // Placeholder
                timeSpent: Math.floor(timeSpentMs / 1000),
            };

            const newResults = [...reviewResults, resultItem];
            setReviewResults(newResults);

            // Move to next question or finish
            if (currentIndex < questions.length - 1) {
                setCurrentIndex((prev) => prev + 1);
                setQuestionStartTime(Date.now());
                answerChangeCountRef.current = 0;
            } else {
                // Finish session - submit all answers
                if (sessionId) {
                    submitMutation.mutate({
                        sessionId,
                        submissions: newSubmissions,
                    });
                }
            }
        },
        [
            currentQuestion,
            sessionId,
            questionStartTime,

            submissions,
            reviewResults,
            currentIndex,
            questions.length,
            combo,
            submitMutation,
        ]
    );

    // ----- Render States -----

    if (createSessionMutation.isPending) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
                <p className="text-gray-600">Đang chuẩn bị phiên ôn tập...</p>
            </div>
        );
    }

    if (createSessionMutation.isError) {
        return <div className="text-red-500 text-center py-12">Lỗi tải dữ liệu.</div>;
    }

    if (questions.length === 0) {
        return (
            <div className="max-w-md mx-auto text-center py-12 bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
                <div className="text-5xl mb-6">🎉</div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Tuyệt vời!</h2>
                <p className="text-gray-600 mb-8">Bạn đã hoàn thành hết tất cả các từ cần ôn tập.</p>
                <button
                    onClick={() => navigate('/')}
                    className="w-full py-3 px-4 bg-indigo-600 text-white rounded-xl font-semibold"
                >
                    Quay lại Dashboard
                </button>
            </div>
        );
    }

    if (!currentQuestion) return null;

    const progress = ((currentIndex + 1) / questions.length) * 100;
    const elapsed = Math.floor((Date.now() - questionStartTime) / 1000);

    return (
        <div className="max-w-3xl mx-auto py-6 px-4 relative">
            {/* Combo Counter Overlay */}
            <ComboCounter combo={combo} />

            {/* Header */}
            <div className="flex justify-between items-center mb-6">
                <button
                    onClick={() => navigate('/')}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                >
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
                {submitMutation.isPending && (
                    <div className="absolute inset-0 bg-white/80 z-50 flex items-center justify-center backdrop-blur-sm">
                        <div className="flex flex-col items-center">
                            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mb-4"></div>
                            <p className="text-gray-600 font-medium">Đang lưu kết quả...</p>
                        </div>
                    </div>
                )}

                <div className="p-8 md:p-12 flex-grow flex flex-col items-center justify-center">
                    {/* Timer */}
                    <div className="mb-8">
                        <div className="relative font-mono text-2xl font-bold text-indigo-600 bg-indigo-50 w-16 h-16 rounded-full flex items-center justify-center border-4 border-indigo-100">
                            {elapsed}
                        </div>
                    </div>

                    {/* Question Content */}
                    <div className="w-full">
                        <QuestionRenderer
                            key={currentQuestion.question_instance_id}
                            question={currentQuestion}
                            onSubmit={handleSubmit}
                            onAnswerChange={handleAnswerChange}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReviewSession;
