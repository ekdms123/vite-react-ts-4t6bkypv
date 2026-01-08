
import React from 'react';
import { Coins, Star, Settings, Heart, Zap } from 'lucide-react';
import { GameState } from '../types';

interface GameHeaderProps {
  state: GameState;
  setShowSettings: (v: any) => void;
}

export const GameHeader: React.FC<GameHeaderProps> = ({ state, setShowSettings }) => {
  return (
    <header className="fixed top-0 left-0 right-0 h-[70px] z-30 px-4 flex justify-between items-center w-full max-w-md mx-auto pointer-events-none">
        
        {/* Left: Soul Records (Interactive) */}
        <div className="pointer-events-auto cursor-pointer group transition-transform hover:scale-105 active:scale-95">
            <div className="flex items-center gap-3 bg-black/60 backdrop-blur-md rounded-full pr-4 border border-[#c5a059]/50 shadow-[0_4px_15px_rgba(0,0,0,0.3)]">
                {/* Crest - Simplified layout (Crown Removed) */}
                <div className="w-14 h-14 rounded-full border-2 border-[#c5a059] bg-[#1a1a1a] flex flex-col items-center justify-center relative -ml-1 shadow-lg overflow-hidden">
                    <div className="flex flex-col items-center justify-center leading-none mt-1">
                        <span className="text-[8px] text-[#c5a059] font-bold uppercase tracking-widest mb-0.5">LV.</span>
                        <span className="text-xl font-cinzel font-bold text-white">{state.level}</span>
                    </div>
                </div>

                {/* Bars */}
                <div className="flex flex-col gap-1.5 py-1">
                    <div className="flex items-center gap-2 w-24">
                        <Heart size={10} className="text-red-500 fill-current shrink-0" />
                        <div className="flex-1 h-1.5 bg-gray-700/50 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-red-500 to-red-600" style={{width: `${(state.hp / state.maxHp) * 100}%`}}></div>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 w-24">
                        <Zap size={10} className="text-blue-500 fill-current shrink-0" />
                        <div className="flex-1 h-1.5 bg-gray-700/50 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-blue-400 to-blue-600" style={{width: `${(state.xp / state.maxXp) * 100}%`}}></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        {/* Right: Treasury (Static Display) & Settings */}
        <div className="pointer-events-auto flex items-center gap-2">
             <div className="bg-black/60 backdrop-blur-md rounded-full px-4 py-2 border border-[#c5a059]/30 shadow-lg flex flex-col items-end">
                 <div className="flex items-center gap-1.5">
                     <span className="text-xs font-bold font-cinzel text-[#ffd700]">{state.gold.toLocaleString()}</span>
                     <Coins size={12} className="text-[#ffd700] fill-current"/>
                 </div>
                 <div className="flex items-center gap-1.5">
                     <span className="text-[10px] font-bold font-cinzel text-blue-400">{state.skillPoints} SP</span>
                     <Star size={10} className="text-blue-500 fill-current"/>
                 </div>
             </div>
             
             <button 
                onClick={setShowSettings}
                className="w-10 h-10 rounded-full bg-black/60 backdrop-blur-md border border-[#c5a059]/30 flex items-center justify-center text-[#c5a059] hover:bg-black hover:text-white transition-all shadow-lg"
             >
                 <Settings size={18}/>
             </button>
        </div>
    </header>
  );
};
