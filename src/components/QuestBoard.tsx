
import React, { useState } from 'react';
import { CheckCircle2, Sparkles, Loader2, Plus } from 'lucide-react';
import { Quest, DifficultyTier } from '../types';

interface QuestBoardProps {
  quests: Quest[];
  addQuest: (text: string, isDaily: boolean) => Promise<void>;
  toggleQuest: (id: number) => void;
  deleteQuest: (id: number) => void;
}

export const QuestBoard: React.FC<QuestBoardProps> = ({ quests, addQuest, toggleQuest, deleteQuest }) => {
  const [newQuestText, setNewQuestText] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  // Calendar Logic
  const today = new Date();
  const weekDays = Array.from({length: 5}, (_, i) => {
      const d = new Date();
      d.setDate(today.getDate() - 2 + i);
      return d;
  });

  const handleAdd = async () => {
    if (newQuestText.trim()) {
      setIsAnalyzing(true);
      // Defaulting to Daily=true as this board is now exclusively for Daily Rituals
      await addQuest(newQuestText, true);
      setIsAnalyzing(false);
      setNewQuestText("");
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Calendar Strip */}
      <div className="bg-[#2c1e12] p-2 rounded-lg border border-[#c5a059]/30 mb-4 flex justify-between items-center shadow-inner">
          {weekDays.map((d, i) => {
              const isToday = d.toDateString() === today.toDateString();
              return (
                  <div key={i} className={`flex flex-col items-center p-2 rounded ${isToday ? 'bg-[#c5a059] text-[#1a1a1a]' : 'text-gray-500'}`}>
                      <span className="text-[9px] font-bold uppercase">{d.toLocaleDateString('en-US', {weekday: 'short'})}</span>
                      <span className="text-xs font-bold font-cinzel">{d.getDate()}</span>
                  </div>
              )
          })}
      </div>

      {/* Input Area */}
      <div className="flex gap-2 mb-4">
        <div className="flex-1 relative">
            <input
                type="text"
                value={newQuestText}
                onChange={(e) => setNewQuestText(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
                disabled={isAnalyzing}
                className="w-full p-3 pr-10 rounded-lg border border-[#c5a059]/50 bg-white text-[#2c1e12] placeholder-gray-400 focus:outline-none focus:border-[#c5a059] shadow-sm text-sm"
                placeholder="새로운 데일리 루틴 입력..."
            />
        </div>
        <button
            onClick={handleAdd}
            disabled={isAnalyzing}
            className="bg-[#2c1e12] text-[#c5a059] p-3 rounded-lg shadow-md font-bold min-w-[50px] flex items-center justify-center hover:bg-[#3e2b1b] disabled:opacity-50"
        >
            {isAnalyzing ? <Loader2 className="animate-spin" /> : <Plus size={20} />}
        </button>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto custom-scroll space-y-2 pb-4">
          {quests.map((q) => (
            <div key={q.id} onClick={() => toggleQuest(q.id)} className={`flex items-center p-4 rounded-xl border-2 transition-all cursor-pointer group shadow-sm ${q.completed ? 'bg-gray-100 border-gray-200 opacity-60' : 'bg-white border-[#c5a059]/20 hover:border-[#c5a059]'}`}>
                <div className={`p-1.5 rounded-full mr-3 transition-colors ${q.completed ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-300'}`}>
                    <CheckCircle2 size={20} />
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-2">
                         <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold text-white ${q.difficulty === 'S' ? 'bg-purple-600' : q.difficulty === 'A' ? 'bg-red-500' : 'bg-blue-500'}`}>{q.difficulty}</span>
                         <span className={`font-bold text-sm ${q.completed ? 'line-through text-gray-400' : 'text-[#2c1e12]'}`}>{q.title}</span>
                    </div>
                    <div className="text-[10px] text-gray-400 mt-1 flex gap-2">
                        <span className="text-[#b08d45] font-bold">+{q.reward} G</span>
                        <span className="text-blue-500">+{q.xpReward} XP</span>
                    </div>
                </div>
                <button onClick={(e) => { e.stopPropagation(); deleteQuest(q.id); }} className="text-gray-300 hover:text-red-400 px-2">×</button>
            </div>
          ))}
          
          {quests.length === 0 && (
              <div className="text-center text-gray-400 text-xs py-10 font-serif italic">
                  "규칙적인 삶이 귀족의 품격입니다."<br/>수행할 루틴을 추가하거나 집사에게 추천을 받아보세요.
              </div>
          )}
      </div>
    </div>
  );
};
