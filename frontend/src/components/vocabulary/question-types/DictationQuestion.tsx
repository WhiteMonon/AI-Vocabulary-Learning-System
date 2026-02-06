import React, { useRef, useEffect, useState } from 'react';
import { HiSpeakerWave } from 'react-icons/hi2';

interface DictationQuestionProps {
    audioUrl: string;
    onSubmit: (answer: string) => void;
    onAnswerChange?: (changeCount: number) => void;
    disabled?: boolean;
}

const DictationQuestion: React.FC<DictationQuestionProps> = ({
    audioUrl,
    onSubmit,
    onAnswerChange,
    disabled = false
}) => {
    const inputRef = useRef<HTMLInputElement>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [answer, setAnswer] = useState('');
    const [changeCount, setChangeCount] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);

    useEffect(() => {
        if (!disabled && inputRef.current) {
            inputRef.current.focus();
        }
    }, [disabled]);

    // Auto-play audio when url changes or component mounts
    useEffect(() => {
        if (audioUrl) {
            playAudio();
        }
    }, [audioUrl]);

    const playAudio = () => {
        if (audioUrl) {
            // Construct full URL if relative path
            const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const fullUrl = audioUrl.startsWith('http') ? audioUrl : `${baseUrl}${audioUrl}`;

            const audio = new Audio(fullUrl);
            audioRef.current = audio;
            setIsPlaying(true);

            audio.play().catch(err => {
                console.error("Audio playback failed:", err);
                setIsPlaying(false);
            });

            audio.onended = () => setIsPlaying(false);
            audio.onerror = () => setIsPlaying(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setAnswer(newValue);

        const newChangeCount = changeCount + 1;
        setChangeCount(newChangeCount);
        if (onAnswerChange) {
            onAnswerChange(newChangeCount);
        }
    };

    return (
        <div className="w-full max-w-lg mx-auto space-y-8">
            {/* Audio Player */}
            <div className="flex justify-center">
                <button
                    onClick={playAudio}
                    disabled={isPlaying}
                    className={`
                        w-24 h-24 rounded-full flex items-center justify-center
                        transition-all duration-300 shadow-xl
                        ${isPlaying
                            ? 'bg-indigo-100 text-indigo-400 scale-95 ring-4 ring-indigo-50'
                            : 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white hover:scale-110 hover:shadow-indigo-300'
                        }
                    `}
                >
                    <HiSpeakerWave className={`w-10 h-10 ${isPlaying ? 'animate-pulse' : ''}`} />
                </button>
            </div>

            <div className="text-center text-gray-500 text-sm font-medium">
                {isPlaying ? 'Đang phát audio...' : 'Nhấn vào loa để nghe lại'}
            </div>

            {/* Input */}
            <div className="relative">
                <input
                    ref={inputRef}
                    type="text"
                    value={answer}
                    onChange={handleChange}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && answer.trim()) {
                            onSubmit(answer.trim());
                        }
                    }}
                    placeholder="Gõ từ bạn nghe được..."
                    disabled={disabled}
                    className="w-full px-6 py-4 bg-gray-50 border-2 border-gray-100 rounded-2xl focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-500/10 transition-all outline-none text-xl text-center font-medium disabled:opacity-60 disabled:bg-gray-100"
                    autoComplete="off"
                    autoFocus
                />
            </div>

            <button
                onClick={() => onSubmit(answer.trim())}
                disabled={disabled || !answer.trim()}
                className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold text-lg hover:bg-indigo-700 active:scale-[0.98] transition-all shadow-lg shadow-indigo-200 disabled:opacity-50 disabled:shadow-none disabled:active:scale-100"
            >
                Kiểm tra
            </button>

            <div className="text-center text-gray-400 text-sm">
                Nhấn <kbd className="font-sans px-2 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs mx-1">Enter</kbd> để nộp bài
            </div>
        </div>
    );
};

export default DictationQuestion;
