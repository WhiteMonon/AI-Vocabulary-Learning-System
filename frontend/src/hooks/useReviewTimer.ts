import { useState, useRef, useEffect, useCallback } from 'react';

/**
 * useReviewTimer
 * Custom hook to track time spent per question precisely.
 * Independent of UI renders.
 */
export const useReviewTimer = (autoStart: boolean = true) => {
    const [elapsed, setElapsed] = useState(0);
    const [isActive, setIsActive] = useState(autoStart);

    // Use refs for accurate tracking without re-renders dependency hell
    const startTimeRef = useRef<number | null>(null);
    const accumulatedRef = useRef(0);
    const frameRef = useRef<number | null>(null);

    const start = useCallback(() => {
        if (isActive) return;
        setIsActive(true);
        startTimeRef.current = Date.now();

        const tick = () => {
            if (startTimeRef.current) {
                const now = Date.now();
                const currentSession = Math.floor((now - startTimeRef.current) / 1000);
                setElapsed(accumulatedRef.current + currentSession);
                frameRef.current = requestAnimationFrame(tick);
            }
        };
        frameRef.current = requestAnimationFrame(tick);
    }, [isActive]);

    const stop = useCallback(() => {
        if (!isActive) return;
        setIsActive(false);
        if (startTimeRef.current && frameRef.current) {
            cancelAnimationFrame(frameRef.current);
            const now = Date.now();
            // Accumulate the time from this session
            accumulatedRef.current += Math.floor((now - startTimeRef.current) / 1000);
            setElapsed(accumulatedRef.current); // Sync state
            startTimeRef.current = null;
        }
    }, [isActive]);

    const reset = useCallback((shouldStart: boolean = true) => {
        if (frameRef.current) cancelAnimationFrame(frameRef.current);
        accumulatedRef.current = 0;
        setElapsed(0);
        startTimeRef.current = shouldStart ? Date.now() : null;
        setIsActive(shouldStart);

        if (shouldStart) {
            const tick = () => {
                if (startTimeRef.current) {
                    const now = Date.now();
                    const currentSession = Math.floor((now - startTimeRef.current) / 1000);
                    setElapsed(accumulatedRef.current + currentSession);
                    frameRef.current = requestAnimationFrame(tick);
                }
            };
            frameRef.current = requestAnimationFrame(tick);
        }
    }, []);

    // Cleanup
    useEffect(() => {
        if (autoStart) {
            reset(true);
        }
        return () => {
            if (frameRef.current) cancelAnimationFrame(frameRef.current);
        };
    }, []);

    return { elapsed, isActive, start, stop, reset };
};

export default useReviewTimer;
