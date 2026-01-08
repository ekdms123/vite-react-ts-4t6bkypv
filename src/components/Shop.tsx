
import React, { useState } from 'react';
import { ShoppingBag, Coins, Gift, Zap, Ticket, Key, Lock, Sparkles, Clock, AlertTriangle } from 'lucide-react';
import { ShopItem } from '../types';

interface ShopProps {
  gold: number;
  items: ShopItem[];
  inventory: string[];
  buyItem: (item: ShopItem) => void;
}

export const Shop: React.FC<ShopProps> = ({ gold, items, inventory, buyItem }) => {
  const [filter, setFilter] = useState<'all' | 'key_item' | 'gift' | 'consumable'>('all');

  const filteredItems = items.filter(item => {
      if (filter === 'all') return true;
      if (filter === 'consumable') return item.type === 'consumable' || item.type === 'special';
      return item.type === filter;
  });

  const checkIsSoldOut = (item: ShopItem) => {
      if (item.maxStock && inventory.filter(id => id === item.id).length >= item.maxStock) return true;
      return false;
  };

  const getIcon = (item: ShopItem) => {
      if(item.id === 'item_hourglass') return <Clock size={16} className="text-cyan-600"/>;
      switch(item.type) {
          case 'gift': return <Gift size={16} className="text-pink-500"/>;
          case 'key_item': return <Key size={16} className="text-[#ffd700]"/>;
          default: return <Sparkles size={16} className="text-purple-600"/>;
      }
  }

  return (
    <div className="h-full flex flex-col animate-fade-in relative bg-[#f4e4bc]">
      {/* Scroll Background Effect */}
      <div className="absolute inset-0 pointer-events-none opacity-20" style={{backgroundImage: 'url("https://www.transparenttextures.com/patterns/aged-paper.png")'}}></div>

      {/* Royal Header */}
      <div className="bg-[#2c1e12] p-4 rounded-b-xl shadow-md border-b-4 border-[#c5a059] sticky top-0 z-20 relative">
          <div className="absolute top-2 left-1/2 -translate-x-1/2 w-16 h-1 bg-[#c5a059] rounded-full opacity-50"></div>
          <div className="flex justify-between items-center mb-2">
              <h2 className="font-bold font-cinzel text-xl text-[#f4e4bc] flex items-center gap-2">
                  <ShoppingBag size={20}/> ROYAL TREASURY
              </h2>
              <div className="bg-[#1a1a1a] px-4 py-1.5 rounded-full border border-[#c5a059] flex items-center gap-2 shadow-[0_0_10px_#c5a059]">
                  <Coins size={14} className="text-[#ffd700]"/>
                  <span className="text-[#f4e4bc] font-bold font-cinzel">{gold.toLocaleString()} G</span>
              </div>
          </div>
      </div>

      {/* Categories */}
      <div className="flex gap-2 p-3 overflow-x-auto scrollbar-hide sticky top-[76px] z-10 border-b border-[#c5a059]/30 bg-[#f4e4bc]/90 backdrop-blur-sm">
          {[
              {id: 'all', label: '전체 (All)'},
              {id: 'key_item', label: '필수 (Key)'},
              {id: 'gift', label: '선물 (Gifts)'},
              {id: 'consumable', label: '소모품 (Items)'}
          ].map(cat => (
              <button 
                key={cat.id}
                onClick={() => setFilter(cat.id as any)}
                className={`px-3 py-1.5 rounded text-xs font-bold transition-all whitespace-nowrap border-2 ${
                    filter === cat.id 
                    ? 'bg-[#2c1e12] text-[#c5a059] border-[#2c1e12] shadow-md transform -translate-y-0.5' 
                    : 'bg-transparent text-[#2c1e12] border-[#2c1e12]/30 hover:border-[#2c1e12]'
                }`}
              >
                  {cat.label}
              </button>
          ))}
      </div>

      {/* Items Grid */}
      <div className="p-3 grid grid-cols-2 gap-3 overflow-y-auto custom-scroll flex-1 relative z-0">
          {filteredItems.map(item => {
              const isSoldOut = checkIsSoldOut(item);
              const canAfford = gold >= item.price;
              const isSpecial = item.type === 'special' || item.type === 'key_item';

              return (
                  <div key={item.id} className={`bg-[#fffbf0] p-3 rounded-lg flex flex-col justify-between relative group overflow-hidden transition-transform border-2 ${isSpecial ? 'border-[#c5a059]' : 'border-[#d4c5a5]'} ${isSoldOut ? 'opacity-60 grayscale' : 'hover:scale-[1.02] shadow-sm'}`}>
                      
                      {/* Paper Texture Overlay */}
                      <div className="absolute inset-0 pointer-events-none opacity-50 bg-gradient-to-br from-white/0 to-[#d4c5a5]/30"></div>
                      
                      <div className="relative z-10">
                          <div className="flex justify-between items-start mb-2">
                              <div className="bg-[#f4e4bc] p-2 rounded border border-[#d4c5a5]">
                                  {getIcon(item)}
                              </div>
                              {item.type === 'key_item' && <span className="text-[9px] font-bold bg-[#8a0000] text-white px-1.5 py-0.5 rounded shadow-sm">필수</span>}
                          </div>
                          
                          <h4 className={`font-bold text-sm mb-1 leading-tight line-clamp-1 ${isSoldOut ? 'text-gray-400 line-through' : 'text-[#2c1e12]'}`}>{item.name}</h4>
                          <p className="text-[10px] text-[#5c4a35] h-8 overflow-hidden leading-snug line-clamp-2">{item.effectDesc}</p>
                      </div>

                      <div className="mt-3 relative z-10">
                          <button
                            disabled={isSoldOut || !canAfford}
                            onClick={() => buyItem(item)}
                            className={`w-full py-2 rounded text-xs font-bold flex items-center justify-center gap-1 transition-all border-b-2 ${
                                isSoldOut 
                                ? 'bg-gray-300 text-gray-500 border-gray-400 cursor-not-allowed' 
                                : !canAfford 
                                    ? 'bg-[#e0e0e0] text-gray-400 border-gray-300 cursor-not-allowed' 
                                    : 'bg-[#2c1e12] text-[#f4e4bc] border-[#1a120b] hover:bg-[#3e2b1b] active:border-t-2 active:border-b-0 active:translate-y-0.5'
                            }`}
                          >
                              {isSoldOut ? (
                                  <>품절</>
                              ) : (
                                  <>{item.price.toLocaleString()} G</>
                              )}
                          </button>
                      </div>
                  </div>
              );
          })}
      </div>
    </div>
  );
};
