import React from 'react';
import { Lock, Unlock, Zap, Coins, Heart, Star } from 'lucide-react';
import { Skill } from '../types';

interface SkillTreeProps {
  skills: Skill[];
  skillPoints: number;
  onUnlock: (id: string) => void;
}

export const SkillTree: React.FC<SkillTreeProps> = ({ skills, skillPoints, onUnlock }) => {
  const getIcon = (type: Skill['effectType']) => {
    switch (type) {
      case 'gold_boost': return <Coins size={18} />;
      case 'xp_boost': return <Zap size={18} />;
      case 'charm': return <Heart size={18} />;
      default: return <Star size={18} />;
    }
  };

  return (
    <div className="h-full flex flex-col animate-fade-in pb-24">
      <div className="flex justify-between items-center mb-4 px-1">
        <h3 className="font-bold text-[#2c1e12] font-cinzel text-lg flex items-center gap-2">
          <Star size={18} /> 특성 (Skills)
        </h3>
        <span className="bg-[#2c1e12] text-[#f4e4bc] px-3 py-1 rounded-full text-xs font-bold shadow">
          SP: {skillPoints}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto custom-scroll space-y-3 p-1">
        {skills.map((skill) => {
          const parent = skills.find(s => s.id === skill.parentId);
          const isLocked = !skill.unlocked;
          const canUnlock = !skill.unlocked && (!parent || parent.unlocked) && skillPoints >= skill.cost;

          return (
            <div 
              key={skill.id}
              className={`relative p-4 rounded-lg border-2 transition-all duration-300 ${
                skill.unlocked 
                  ? 'bg-white border-[#c5a059] shadow-md' 
                  : canUnlock 
                    ? 'bg-gray-100 border-gray-400 border-dashed cursor-pointer hover:bg-white hover:border-[#c5a059]' 
                    : 'bg-gray-200 border-gray-300 opacity-60 grayscale'
              }`}
              onClick={() => canUnlock && onUnlock(skill.id)}
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${skill.unlocked ? 'bg-[#fff9e6] text-[#c5a059]' : 'bg-gray-300 text-gray-500'}`}>
                    {getIcon(skill.effectType)}
                  </div>
                  <div>
                    <h4 className="font-bold text-[#2c1e12] text-sm">{skill.name}</h4>
                    <p className="text-xs text-gray-500 mt-0.5">{skill.description}</p>
                  </div>
                </div>
                <div className="flex flex-col items-end">
                   {skill.unlocked ? (
                     <Unlock size={16} className="text-[#c5a059]" />
                   ) : (
                     <div className="flex items-center gap-1 text-gray-600 font-bold text-xs bg-gray-300 px-2 py-1 rounded">
                       <Lock size={12} /> {skill.cost} SP
                     </div>
                   )}
                </div>
              </div>
              
              {/* Connection Line Visual (Simple) */}
              {skill.parentId && (
                <div className="absolute -top-3 left-6 w-0.5 h-3 bg-gray-300 -z-10"></div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};