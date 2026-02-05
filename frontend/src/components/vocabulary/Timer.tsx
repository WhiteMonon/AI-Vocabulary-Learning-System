import React, { useState, useEffect } from 'react';

interface TimerProps {
    duration: number; // seconds
    onTimeUp: () => void;
    isActive: boolean;
}

const Timer: React.FC<TimerProps> = ({ duration, onTimeUp, isActive }) => {
    const [timeLeft, setTimeLeft] = useState(duration);

    useEffect(() => {
        setTimeLeft(duration);
    }, [duration]);

    useEffect(() => {
        let intervalId: ReturnType<typeof setInterval>;

        if (isActive && timeLeft > 0) {
            intervalId = setInterval(() => {
                setTimeLeft((prev) => prev - 1);
            }, 1000);
        } else if (timeLeft === 0) {
            onTimeUp();
        }

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [isActive, timeLeft, onTimeUp]);

    const progress = (timeLeft / duration) * 100;
    const color = timeLeft < 5 ? 'bg-red-500' : 'bg-blue-500';

    return (
        <div className="w-full">
            <div className="flex justify-between items-center mb-1">
                <span className="text-sm font-medium text-gray-700">Thời gian còn lại</span>
                <span className={`text-sm font-bold ${timeLeft < 5 ? 'text-red-600 animate-pulse' : 'text-blue-600'}`}>
                    {timeLeft}s
                </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                <div
                    className={`${color} h-2.5 rounded-full transition-all duration-1000 ease-linear`}
                    style={{ width: `${progress}%` }}
                ></div>
            </div>
        </div>
    );
};

export default Timer;
