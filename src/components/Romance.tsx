
import React, { useState } from 'react';
import { Heart, Gift, Lock, ImagePlus, Loader2, MessageCircle, X, ChevronLeft, Play, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { MaleLead, ShopItem, Season, StoryChapter, Choice } from '../types';
import { getVNDialogue } from '../services/geminiService';

interface RomanceProps {
  leads: MaleLead[];
  inventory: string[];
  shopItems: ShopItem[];
  chapters: StoryChapter[];
  onGift: (leadId: string, itemId: string) => void;
  onGeneratePortrait: (leadId: string, size: '1K' | '2K' | '4K') => Promise<void>;
  season: Season;
  onLockPortrait: (leadId: string) => void;
  onPlayChapter: (chapterId: string) => void;
  onChoiceMade: (choice: Choice) => void;
}

export const Romance: React.FC<RomanceProps> = ({ 
    leads, inventory, shopItems, chapters, onGift, onGeneratePortrait, 
    season, onLockPortrait, onPlayChapter
}) => {
  const [activeLeadId, setActiveLeadId] = useState<string | null>(null);
  const [vnDialogue, setVnDialogue] = useState<string | null>(null);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [generatingId, setGeneratingId] = useState<string | null>(null);

  const activeLead = leads.find(l => l.id === activeLeadId);
  const giftsInInventory = shopItems.filter(item => inventory.includes(item.id) && item.type === 'gift');
  
  // Get Routes specifically for this Lead
  const routeStories = chapters.filter(c => c.type === 'Route' && c.relatedLeadId === activeLeadId);

  const handleGenClick = async (leadId: string) => {
      setGeneratingId(leadId);
      await onGeneratePortrait(leadId, '2K'); 
      setGeneratingId(null);
  };

  const handleChat = async () => {
      if(!activeLead) return;
      setIsChatLoading(true);
      const discoveredSecret = activeLead.secrets.find(s => s.isDiscovered);
      const context = discoveredSecret 
        ? `User knows your secret: ${discoveredSecret.title}. You are nervous but relieved.` 
        : `Season: ${season}. Private conversation in his room.`;
      const text = await getVNDialogue(activeLead.name, activeLead.affection, context);
      setVnDialogue(text);
      setIsChatLoading(false);
  };

  if (!activeLead) {
      return (
          <div className="h-full p-6 animate-fade-in flex flex-col gap-4 pb-24 overflow-y-auto custom-scroll">
              <div className="text-center mb-4">
                  <h2 className="text-2xl font-cinzel font-bold text-[#c5a059]">LOVERS</h2>
                  <p className="text-xs text-gray-500">운명의 상대를 선택하여 공략을 진행하십시오.</p>
              </div>
              
              <div className="grid grid-cols-1 gap-6">
                  {leads.map(lead => (
                      <div key={lead.id} onClick={() => setActiveLeadId(lead.id)} className="relative h-64 rounded-xl overflow-hidden border-2 border-[#c5a059]/30 group cursor-pointer shadow-lg hover:border-[#c5a059] transition-all">
                          {lead.imageUrl ? (
                              <img src={lead.imageUrl} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                          ) : (
                              <div className="w-full h-full bg-[#1a1a1a] flex items-center justify-center text-[#c5a059] font-cinzel">NO PORTRAIT</div>
                          )}
                          <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-80"></div>
                          <div className="absolute bottom-0 left-0 right-0 p-5">
                              <h3 className="text-2xl font-cinzel font-bold text-white mb-1 flex items-center gap-2">
                                  {lead.name} <Heart size={16} className={`${lead.isVillain ? 'text-red-600' : 'text-pink-500'} fill-current`}/> <span className="text-sm">{lead.affection}</span>
                              </h3>
                              <p className="text-xs text-gray-300 line-clamp-1">{lead.desc}</p>
                          </div>
                      </div>
                  ))}
              </div>
          </div>
      );
  }

  return (
      <div className="h-full flex flex-col animate-fade-in relative bg-[#1a1212]">
          {/* Header */}
          <div className="absolute top-0 left-0 right-0 p-4 z-20 flex justify-between items-center bg-gradient-to-b from-black/80 to-transparent">
              <button onClick={() => setActiveLeadId(null)} className="text-white hover:text-[#c5a059] flex items-center gap-1 font-bold">
                  <ChevronLeft/> BACK
              </button>
              <div className="flex gap-2">
                 <button onClick={() => onLockPortrait(activeLead.id)} className={`p-2 rounded-full backdrop-blur ${activeLead.isImageLocked ? 'bg-[#c5a059] text-black' : 'bg-black/50 text-white'}`}><Lock size={16}/></button>
                 {!activeLead.isImageLocked && (
                    <button onClick={() => handleGenClick(activeLead.id)} disabled={!!generatingId} className="p-2 bg-black/50 text-white rounded-full hover:bg-[#c5a059] hover:text-black">
                        {generatingId ? <Loader2 size={16} className="animate-spin"/> : <ImagePlus size={16}/>}
                    </button>
                 )}
              </div>
          </div>

          {/* Character Visual */}
          <div className="h-[55%] relative overflow-hidden">
               {activeLead.imageUrl ? (
                   <img src={activeLead.imageUrl} className="w-full h-full object-cover object-top" />
               ) : (
                   <div className="w-full h-full bg-gray-900 flex items-center justify-center text-gray-600">초상화 없음</div>
               )}
               <div className="absolute inset-0 bg-gradient-to-t from-[#1a1212] via-transparent to-transparent"></div>
               
               {/* Dialogue Overlay */}
               {(vnDialogue || isChatLoading) && (
                   <div className="absolute bottom-4 left-4 right-4 bg-black/90 border border-[#c5a059] p-4 rounded-lg animate-slide-up shadow-2xl">
                       <button onClick={() => setVnDialogue(null)} className="absolute top-2 right-2 text-gray-500"><X size={14}/></button>
                       <h4 className="text-[#c5a059] font-bold text-sm mb-2">{activeLead.name}</h4>
                       {isChatLoading ? <Loader2 className="animate-spin text-white"/> : <p className="text-white text-sm font-serif leading-relaxed">"{vnDialogue}"</p>}
                   </div>
               )}
          </div>

          {/* Interaction Area */}
          <div className="flex-1 bg-[#1a1212] p-5 rounded-t-3xl -mt-6 relative z-10 overflow-y-auto custom-scroll pb-24">
               {/* Affection Bar */}
               <div className="flex justify-between items-center mb-2">
                   <span className="text-[#c5a059] text-xs font-bold tracking-widest">AFFECTION</span>
                   <span className="text-white font-cinzel">{activeLead.affection} / 100</span>
               </div>
               <div className="w-full bg-gray-900 h-2 rounded-full mb-6 overflow-hidden">
                   <div className="h-full bg-gradient-to-r from-[#c5a059] to-red-500 transition-all duration-1000" style={{width: `${activeLead.affection}%`}}></div>
               </div>

               {/* Secrets Section */}
               {activeLead.secrets.length > 0 && (
                   <div className="mb-6 bg-black/40 p-3 rounded border border-red-900/50">
                       <h4 className="text-red-500 font-bold text-xs mb-2 flex items-center gap-2"><EyeOff size={12}/> HIDDEN TRUTHS</h4>
                       {activeLead.secrets.map(sec => (
                           <div key={sec.id} className="flex items-start gap-2 mb-2">
                               {sec.isDiscovered ? (
                                   <>
                                       <Eye size={14} className="text-[#c5a059] mt-1 shrink-0"/>
                                       <div>
                                           <div className="text-[#c5a059] text-xs font-bold">{sec.title}</div>
                                           <div className="text-gray-400 text-[10px]">{sec.description}</div>
                                       </div>
                                   </>
                               ) : (
                                   <>
                                       <Lock size={14} className="text-gray-600 mt-1 shrink-0"/>
                                       <div className="text-gray-600 text-xs italic">??? (특수 아이템 필요)</div>
                                   </>
                               )}
                           </div>
                       ))}
                   </div>
               )}

               {/* Actions */}
               <div className="grid grid-cols-2 gap-3 mb-8">
                   <button onClick={handleChat} className="bg-[#2c1e12] border border-[#c5a059]/30 p-3 rounded-lg flex items-center justify-center gap-2 text-[#f4e4bc] hover:bg-[#c5a059] hover:text-[#1a1212] transition-colors">
                       <MessageCircle size={18}/> 대화하기
                   </button>
                   <div className="relative group">
                        <button className="w-full bg-[#2c1e12] border border-[#c5a059]/30 p-3 rounded-lg flex items-center justify-center gap-2 text-[#f4e4bc] hover:bg-[#c5a059] hover:text-[#1a1212] transition-colors">
                            <Gift size={18}/> 선물하기
                        </button>
                        <div className="absolute bottom-full left-0 w-full bg-[#2a2a2a] border border-gray-600 rounded mb-2 hidden group-hover:block z-50">
                            {giftsInInventory.length > 0 ? giftsInInventory.map(g => (
                                <div key={g.id} onClick={() => onGift(activeLead.id, g.id)} className="p-2 text-xs text-white hover:bg-[#c5a059] hover:text-black cursor-pointer border-b border-gray-700">
                                    {g.name}
                                </div>
                            )) : <div className="p-2 text-[10px] text-gray-500 text-center">선물 없음</div>}
                        </div>
                   </div>
               </div>

               {/* Route Stories List */}
               <h3 className="text-white font-cinzel font-bold mb-4 flex items-center gap-2"><Play size={16} className="text-[#c5a059]"/> ROUTE EPISODES</h3>
               <div className="space-y-3">
                   {routeStories.map((story, idx) => {
                       // Logic Check: Unlocked based on Affection (if defined)
                       const isLocked = story.reqAffection && activeLead.affection < story.reqAffection.min;
                       
                       return (
                           <div key={story.id} className={`p-4 rounded border flex justify-between items-center transition-all ${
                               !isLocked ? 'bg-[#2c1e12] border-[#c5a059]/50' : 'bg-gray-900 border-gray-800 opacity-60'
                           }`}>
                               <div>
                                   <div className="text-[10px] text-[#c5a059] font-bold mb-1">EPISODE {idx + 1}</div>
                                   <h4 className="text-sm font-bold text-white">{story.title}</h4>
                                   <p className="text-[10px] text-gray-400 mt-1">{story.description}</p>
                                   {isLocked && (
                                       <div className="text-[10px] text-red-400 mt-1 flex items-center gap-1">
                                           <AlertCircle size={10}/> 호감도 {story.reqAffection?.min} 필요
                                       </div>
                                   )}
                                   {story.reqItem && !inventory.includes(story.reqItem) && (
                                       <div className="text-[10px] text-red-400 mt-1 flex items-center gap-1">
                                           <AlertCircle size={10}/> 특수 아이템 필요
                                       </div>
                                   )}
                               </div>
                               
                               {!isLocked && !story.isCompleted && (
                                   <button onClick={() => onPlayChapter(story.id)} className="px-3 py-1 bg-[#c5a059] text-black text-xs font-bold rounded hover:bg-white transition-colors">START</button>
                               )}
                               {story.isCompleted && <span className="text-xs text-green-500 font-bold border border-green-500 px-2 py-0.5 rounded">CLEAR</span>}
                               {isLocked && <Lock size={14} className="text-gray-600"/>}
                           </div>
                       );
                   })}
                   {routeStories.length === 0 && <div className="text-gray-500 text-xs text-center py-4">아직 공개된 에피소드가 없습니다.</div>}
               </div>
          </div>
      </div>
  );
};
