import React from 'react';

interface ComboCounterProps {
    combo: number;
}

const ComboCounter: React.FC<ComboCounterProps> = ({ combo }) => {
    if (combo < 2) return null;

    return (
        <div className="absolute top-4 right-4 flex flex-col items-center animate-in zoom-in slide-in-from-top-4 duration-300">
            <div className="relative">
                <span className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-600 drop-shadow-sm animate-pulse">
                    x{combo}
                </span>
                <span className="absolute -top-3 -right-3 text-2xl">🔥</span>
            </div>
            <span className="text-xs font-bold text-orange-500 uppercase tracking-widest mt-1">
                Combo!
            </span>
        </div>
    );
};

export default ComboCounter;
