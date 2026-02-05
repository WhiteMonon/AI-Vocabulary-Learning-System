import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getQuizSession, submitQuizAnswer } from '../../api/vocabulary';
import { QuizSubmit } from '../../types/vocabulary';
import MultipleChoiceQuiz from '../../components/vocabulary/MultipleChoiceQuiz';

const Quiz: React.FC = () => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [currentIndex, setCurrentIndex] = useState(0);
    const [startTime, setStartTime] = useState<number>(Date.now());
    const [sessionFinished, setSessionFinished] = useState(false);

    const { data: quizResponse, isLoading, error } = useQuery({
        queryKey: ['quiz-session'],
        queryFn: () => getQuizSession(10),
        staleTime: 0, // Always get a fresh session
    });

    const quizList = quizResponse?.questions || [];
    const currentQuestion = quizList[currentIndex];

    const submitMutation = useMutation({
        mutationFn: (submit: QuizSubmit) => submitQuizAnswer(submit),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vocabularies'] });
            queryClient.invalidateQueries({ queryKey: ['vocabulary-stats'] });
        },
    });

    const handleNext = (isCorrect: boolean) => {
        const timeSpent = Math.floor((Date.now() - startTime) / 1000);

        submitMutation.mutate({
            vocabulary_id: currentQuestion.id,
            is_correct: isCorrect,
            time_spent_seconds: timeSpent,
        });

        if (currentIndex < quizList.length - 1) {
            setCurrentIndex(currentIndex + 1);
            setStartTime(Date.now());
        } else {
            setSessionFinished(true);
        }
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
                <p className="text-gray-600">AI đang soạn câu hỏi cho bạn...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <div className="text-6xl mb-6">🏜️</div>
                <p className="text-red-500 mb-4 font-medium">Đã có lỗi xảy ra khi kết nối với AI.</p>
                <button onClick={() => navigate('/')} className="px-6 py-2 bg-indigo-600 text-white rounded-xl">
                    Quay lại Dashboard
                </button>
            </div>
        );
    }

    if (quizList.length === 0 || sessionFinished) {
        return (
            <div className="max-w-md mx-auto text-center py-12 bg-white rounded-3xl shadow-xl shadow-indigo-100/50 border border-indigo-50 p-10 animate-in zoom-in-95 duration-500">
                <div className="text-6xl mb-6">🏁</div>
                <h2 className="text-3xl font-bold text-gray-800 mb-4">Hoàn thành!</h2>
                <p className="text-gray-600 mb-8 leading-relaxed">
                    Chúc mừng bạn đã hoàn thành bài Quiz hôm nay. AI đã ghi nhận sự tiến bộ của bạn!
                </p>
                <button
                    onClick={() => navigate('/')}
                    className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold text-lg hover:bg-indigo-700 transition-all shadow-lg"
                >
                    Quay lại Dashboard
                </button>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto py-8 px-4">
            <div className="flex justify-between items-center mb-8">
                <button
                    onClick={() => navigate('/')}
                    className="group text-gray-500 hover:text-gray-700 flex items-center gap-2 font-medium transition-colors"
                >
                    <div className="p-2 rounded-xl bg-gray-50 group-hover:bg-gray-100 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
                        </svg>
                    </div>
                    Thoát
                </button>
                <div className="px-4 py-2 rounded-2xl bg-indigo-50 text-indigo-700 font-bold text-sm">
                    Câu {currentIndex + 1} / {quizList.length}
                </div>
            </div>

            <div className="bg-white rounded-[2rem] shadow-2xl shadow-indigo-100/40 border border-indigo-50 overflow-hidden">
                <div className="w-full bg-gray-100 h-2">
                    <div
                        className="bg-indigo-500 h-full transition-all duration-700 ease-out"
                        style={{ width: `${(currentIndex / quizList.length) * 100}%` }}
                    ></div>
                </div>

                <div className="p-8 md:p-12">
                    <MultipleChoiceQuiz
                        key={currentQuestion.id} // Reset state on each question
                        question={currentQuestion}
                        onNext={handleNext}
                    />
                </div>
            </div>
        </div>
    );
};

export default Quiz;
