
import React from 'react';
import { Sparkles, Heart, Crown, BookOpen, Key, AlertCircle, Skull } from 'lucide-react';
import { GameState } from '../types';

interface StatusCardProps {
  state: GameState;
  onAskOracle: () => void;
  isOracleLoading: boolean;
  onSetName?: (name: string) => void;
}

export const StatusCard: React.FC<StatusCardProps> = ({ state, onAskOracle, isOracleLoading, onSetName }) => {
  const currentChapter = state.storyChapters.find(c => c.type === 'Main' && !c.isCompleted && c.isUnlocked) 
    || state.storyChapters.find(c => c.type === 'Main' && c.isCompleted) 
    || state.storyChapters[0];

  return (
    <div className="bg-[#1a1a1a] rounded-xl border-2 border-[#c5a059] shadow-2xl overflow-hidden flex flex-col w-full max-w-md animate-fade-in">
      
      {/* 1. Header: Protagonist Info */}
      <div className="bg-[#2c1e12] p-5 border-b border-[#c5a059] relative overflow-hidden">
           <div className="absolute -right-6 -top-6 text-[#c5a059]/10"><Crown size={120}/></div>
           <div className="relative z-10 flex items-center gap-4">
                <div className="w-16 h-16 rounded-full border-2 border-[#c5a059] overflow-hidden bg-black">
                    {state.userImageUrl ? <img src={state.userImageUrl} className="w-full h-full object-cover"/> : <div className="w-full h-full flex items-center justify-center text-[#c5a059]">No IMG</div>}
                </div>
                <div>
                    <div className="text-[#c5a059] text-[10px] font-bold tracking-[0.2em] mb-1">PROTAGONIST</div>
                    <h2 className="text-2xl font-bold text-white font-cinzel">{state.name}</h2>
                    <div className="text-gray-400 text-xs mt-1 font-serif italic">Lv.{state.level} {state.title}</div>
                </div>
           </div>
           
           {/* Corruption Meter */}
           <div className="mt-4 flex items-center gap-2">
               <Skull size={12} className={state.corruption > 50 ? "text-red-500" : "text-gray-500"}/>
               <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                   <div className="h-full bg-purple-600 transition-all duration-500" style={{width: `${Math.min(state.corruption, 100)}%`}}></div>
               </div>
               <span className="text-[9px] text-gray-400">KARMA: {state.corruption}</span>
           </div>
      </div>

      <div className="p-5 space-y-6 flex-1 overflow-y-auto custom-scroll">
          
          {/* 2. Main Story Progress */}
          <div>
              <h3 className="text-[#c5a059] font-bold text-xs mb-3 flex items-center gap-2 uppercase tracking-wider">
                  <BookOpen size={14}/> Main Scenario
              </h3>
              <div className="bg-[#2c1e12] p-4 rounded-lg border border-[#c5a059]/30">
                  <div className="flex justify-between items-start mb-2">
                      <span className="text-white font-bold text-sm">Now: {currentChapter.title}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded ${currentChapter.isCompleted ? 'bg-green-900 text-green-400' : 'bg-blue-900 text-blue-400'}`}>
                          {currentChapter.isCompleted ? 'COMPLETED' : 'IN PROGRESS'}
                      </span>
                  </div>
                  <p className="text-gray-400 text-xs mb-3 line-clamp-2">{currentChapter.description}</p>
                  
                  {/* Next Objective Items */}
                  <div className="flex items-center gap-2 text-xs bg-black/40 p-2 rounded">
                      <Key size={12} className="text-[#ffd700]"/> 
                      <span className="text-gray-500">필요 아이템:</span>
                      <span className="text-white font-bold">{currentChapter.reqItem || "없음 (None)"}</span>
                  </div>
              </div>
          </div>

          {/* 3. Love Interest Status */}
          <div>
              <h3 className="text-[#c5a059] font-bold text-xs mb-3 flex items-center gap-2 uppercase tracking-wider">
                  <Heart size={14}/> Target Affection
              </h3>
              <div className="space-y-2">
                  {state.maleLeads.map(lead => (
                      <div key={lead.id} className="bg-white/5 p-2 rounded flex items-center justify-between border border-white/10">
                          <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-full bg-black overflow-hidden border border-gray-600">
                                  {lead.imageUrl && <img src={lead.imageUrl} className="w-full h-full object-cover"/>}
                              </div>
                              <div>
                                  <div className="text-white text-xs font-bold">{lead.name}</div>
                                  <div className="text-[10px] text-gray-500">{lead.affection >= 100 ? "운명의 반려" : lead.affection >= 50 ? "호감" : "관심 없음"}</div>
                              </div>
                          </div>
                          <div className="flex items-center gap-2">
                              <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                                  <div className="h-full bg-pink-500" style={{width: `${Math.min(lead.affection, 100)}%`}}></div>
                              </div>
                              <span className="text-[#c5a059] text-xs font-cinzel w-6 text-right">{lead.affection}</span>
                          </div>
                      </div>
                  ))}
              </div>
          </div>

          {/* 4. Oracle Hint */}
          <div>
              <h3 className="text-[#c5a059] font-bold text-xs mb-3 flex items-center gap-2 uppercase tracking-wider">
                  <Sparkles size={14}/> Akashic Records (Hint)
              </h3>
              <button 
                onClick={onAskOracle} 
                disabled={isOracleLoading}
                className="w-full py-4 bg-gradient-to-r from-[#2c1e12] to-[#1a1a1a] border border-[#c5a059] text-[#c5a059] rounded-lg hover:brightness-125 transition-all flex flex-col items-center justify-center gap-1 group"
              >
                  <span className="font-bold text-sm group-hover:scale-105 transition-transform">시스템 힌트 열람</span>
                  <span className="text-[10px] text-gray-500">다음 전개를 위한 조언을 확인합니다.</span>
              </button>
          </div>
      </div>
    </div>
  );
};
