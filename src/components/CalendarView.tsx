import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Star, CheckCircle2 } from 'lucide-react';
import { DailyRecord, Quest } from '../types';

interface CalendarViewProps {
  calendar: DailyRecord[];
  quests: Quest[]; // To look up quest titles
}

export const CalendarView: React.FC<CalendarViewProps> = ({ calendar, quests }) => {
  const [displayDate, setDisplayDate] = useState(new Date());
  const [selectedDateStr, setSelectedDateStr] = useState<string | null>(null);

  // KST Helpers
  const getKSTDate = (date: Date) => {
    return new Date(date.toLocaleString("en-US", { timeZone: "Asia/Seoul" }));
  };

  const getDaysInMonth = (year: number, month: number) => new Date(year, month + 1, 0).getDate();
  const getFirstDayOfMonth = (year: number, month: number) => new Date(year, month, 1).getDay();

  const year = displayDate.getFullYear();
  const month = displayDate.getMonth();

  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);
  
  const days = [];
  // Empty slots for start
  for (let i = 0; i < firstDay; i++) days.push(null);
  // Days
  for (let i = 1; i <= daysInMonth; i++) days.push(i);

  const prevMonth = () => setDisplayDate(new Date(year, month - 1, 1));
  const nextMonth = () => setDisplayDate(new Date(year, month + 1, 1));

  // Get record for a specific day
  const getRecord = (day: number) => {
      const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      return {
          str: dateStr,
          data: calendar.find(r => r.date === dateStr)
      };
  };

  const selectedRecord = selectedDateStr ? calendar.find(r => r.date === selectedDateStr) : null;

  return (
    <div className="h-full flex flex-col animate-fade-in pb-24">
       {/* Calendar Header */}
       <div className="flex justify-between items-center mb-4 bg-[#2c1e12] text-[#f4e4bc] p-3 rounded shadow border border-[#c5a059]">
           <button onClick={prevMonth} className="hover:text-white transition-colors"><ChevronLeft /></button>
           <h3 className="font-cinzel text-lg font-bold">{year}. {month + 1}</h3>
           <button onClick={nextMonth} className="hover:text-white transition-colors"><ChevronRight /></button>
       </div>

       {/* Grid */}
       <div className="bg-[#1a1a1a]/80 backdrop-blur-sm p-2 rounded-lg border border-[#c5a059] shadow-md mb-4">
           {/* Weekday Headers */}
           <div className="grid grid-cols-7 mb-2 text-center text-xs font-bold text-[#c5a059]">
               <div className="text-red-400">SUN</div>
               <div>MON</div>
               <div>TUE</div>
               <div>WED</div>
               <div>THU</div>
               <div>FRI</div>
               <div>SAT</div>
           </div>
           
           {/* Days */}
           <div className="grid grid-cols-7 gap-1">
               {days.map((day, idx) => {
                   if (!day) return <div key={`empty-${idx}`} className="aspect-square"></div>;
                   
                   const { str, data } = getRecord(day);
                   const isToday = str === getKSTDate(new Date()).toISOString().split('T')[0];
                   const isSelected = str === selectedDateStr;
                   
                   let bgClass = "bg-[#2c1e12]/50 hover:bg-[#3e2b1b]";
                   let textClass = "text-gray-400";

                   if (data && data.completionRate >= 100) { bgClass = "bg-[#c5a059] text-[#1a1a1a]"; textClass = "text-[#1a1a1a] font-bold"; }
                   else if (data && data.completionRate >= 50) { bgClass = "bg-[#8b6b3e] text-[#f4e4bc]"; textClass = "text-[#f4e4bc]"; }
                   else if (data) { bgClass = "bg-[#3e2b1b] text-[#c5a059]"; textClass = "text-[#c5a059]"; }
                   
                   if (isToday) {
                       bgClass += " border border-[#f4e4bc]";
                   }

                   return (
                       <button 
                            key={day} 
                            onClick={() => setSelectedDateStr(str)}
                            className={`aspect-square rounded flex flex-col items-center justify-center relative border transition-all ${
                                isSelected ? 'border-[#ff0000] ring-1 ring-[#ff0000] z-10' : 'border-transparent'
                            } ${bgClass}`}
                        >
                           <span className={`text-xs ${textClass}`}>{day}</span>
                           {data && data.completionRate >= 100 && <Star size={8} className="text-[#ffd700] mt-1 fill-current" />}
                       </button>
                   );
               })}
           </div>
       </div>

       {/* Details Panel - FIXED: Dark Theme */}
       <div className="flex-1 bg-[#1a1a1a]/90 border border-[#c5a059] rounded-lg p-4 shadow-inner overflow-y-auto custom-scroll text-[#f4e4bc]">
           {selectedDateStr ? (
               <>
                   <h4 className="font-bold text-[#c5a059] font-cinzel border-b border-[#c5a059]/50 pb-2 mb-3 flex justify-between items-center">
                       {selectedDateStr} 기록
                       {selectedRecord && <span className="text-xs text-[#ffd700]">{selectedRecord.completionRate}% 달성</span>}
                   </h4>
                   
                   {selectedRecord && selectedRecord.completedQuestIds ? (
                       <ul className="space-y-2">
                           {selectedRecord.completedQuestIds.map((qId, i) => {
                               const quest = quests.find(q => q.id === qId);
                               const title = quest ? quest.title : "완료된 임무 (기록됨)";
                               return (
                                   <li key={i} className="text-sm flex items-center gap-2 text-[#f4e4bc]/80">
                                       <CheckCircle2 size={14} className="text-green-500" />
                                       <span className="line-through decoration-gray-500">{title}</span>
                                   </li>
                               );
                           })}
                       </ul>
                   ) : (
                       <p className="text-sm text-gray-500 italic text-center py-4">
                           기록된 수행 내역이 없습니다.
                       </p>
                   )}
               </>
           ) : (
               <p className="text-sm text-gray-500 italic text-center py-10">
                   날짜를 선택하여 과거의 행적을 조회하십시오.
               </p>
           )}
       </div>
    </div>
  );
};