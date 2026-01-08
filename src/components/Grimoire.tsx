
import React, { useState } from 'react';
import { PenTool, TrendingUp, Save } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Skill, WritingLog } from '../types';

interface GrimoireProps {
  writingLogs: WritingLog[];
  onAddLog: (count: number) => void;
  skills: Skill[];
  skillPoints: number;
  onUnlockSkill: (id: string) => void;
}

export const Grimoire: React.FC<GrimoireProps> = ({ 
  writingLogs, onAddLog 
}) => {
  const [todayCount, setTodayCount] = useState<string>("");

  // Prepare Chart Data (Last 7 Days)
  const chartData = writingLogs.slice(-7).map(log => ({
      date: log.date.slice(5), // MM-DD
      count: log.wordCount
  }));

  const totalWords = writingLogs.reduce((acc, cur) => acc + cur.wordCount, 0);
  const averageWords = writingLogs.length > 0 ? Math.floor(totalWords / writingLogs.length) : 0;

  const handleSave = () => {
      const count = parseInt(todayCount);
      if (!isNaN(count)) {
          onAddLog(count);
          setTodayCount("");
          alert("오늘의 집필량이 마도서에 기록되었습니다.");
      }
  };

  return (
    <div className="h-full flex flex-col animate-fade-in relative p-1 space-y-6">
       {/* Input Section */}
       <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex flex-col items-center gap-4 mt-4">
           <h3 className="text-gray-600 font-bold text-sm flex items-center gap-2"><PenTool size={16}/> 오늘의 집필량 기록</h3>
           <div className="relative w-full max-w-[200px]">
               <input 
                  type="number" 
                  value={todayCount}
                  onChange={(e) => setTodayCount(e.target.value)}
                  placeholder="0"
                  className="w-full bg-[#fdfbf7] border-2 border-[#c5a059] rounded-xl p-3 text-center text-3xl text-[#2c1e12] font-cinzel focus:outline-none focus:ring-4 focus:ring-[#c5a059]/20 placeholder-gray-300"
               />
               <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-xs font-bold">자</span>
           </div>
           <button 
              onClick={handleSave}
              className="w-full flex items-center justify-center gap-2 bg-[#2c1e12] text-[#c5a059] px-6 py-3 rounded-xl font-bold hover:bg-[#3e2b1b] transition-all shadow-md active:scale-95"
            >
               <Save size={18} /> 기록하기
           </button>
       </div>

       {/* Stats Grid */}
       <div className="grid grid-cols-2 gap-3">
           <div className="bg-white p-3 rounded-lg border border-gray-200 text-center shadow-sm">
               <div className="text-gray-400 text-[10px] mb-1 font-bold">TOTAL WORDS</div>
               <div className="text-[#c5a059] text-xl font-bold font-cinzel">{totalWords.toLocaleString()}</div>
           </div>
           <div className="bg-white p-3 rounded-lg border border-gray-200 text-center shadow-sm">
               <div className="text-gray-400 text-[10px] mb-1 font-bold">DAILY AVG</div>
               <div className="text-[#c5a059] text-xl font-bold font-cinzel">{averageWords.toLocaleString()}</div>
           </div>
       </div>

       {/* Chart */}
       <div className="h-64 bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex-1">
           <h4 className="text-gray-400 text-xs font-bold mb-4 flex items-center gap-2"><TrendingUp size={14}/> 주간 통계</h4>
           <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
                  <XAxis dataKey="date" stroke="#9ca3af" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#9ca3af" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip 
                      contentStyle={{ backgroundColor: '#fff', borderColor: '#c5a059', color: '#2c1e12', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                      cursor={{fill: 'rgba(197, 160, 89, 0.1)'}}
                  />
                  <Bar dataKey="count" fill="#c5a059" radius={[4, 4, 0, 0]} barSize={24} />
              </BarChart>
           </ResponsiveContainer>
       </div>
    </div>
  );
};
