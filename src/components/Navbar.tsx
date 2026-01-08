
import React from 'react';
import { Home, Feather, Heart, Coins, Book } from 'lucide-react';
import { TabId } from '../types';

interface NavbarProps {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const navItems: { id: TabId; label: string; icon: React.ReactNode }[] = [
    { id: 'love', label: 'Love', icon: <Heart size={20} /> },
    { id: 'writing', label: 'Writing', icon: <Feather size={20} /> },
    { id: 'home', label: 'Main', icon: <Home size={24} /> },
    { id: 'ledger', label: 'Ledger', icon: <Coins size={20} /> },
    { id: 'diary', label: 'Diary', icon: <Book size={20} /> },
  ];

  return (
    <nav className="absolute bottom-0 w-full z-30 px-4 pb-6 pointer-events-none">
      <div className="bg-[#1a1a1a]/90 backdrop-blur-xl border border-[#c5a059] rounded-2xl shadow-[0_10px_40px_rgba(0,0,0,0.8)] flex justify-between items-center px-2 py-2 pointer-events-auto max-w-sm mx-auto">
      {navItems.map((item) => {
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`flex flex-col items-center justify-center transition-all duration-300 relative group w-14 h-14 rounded-xl ${
              isActive ? 'bg-[#c5a059] text-[#1a1a1a] -translate-y-3 shadow-[0_5px_15px_#c5a059]' : 'text-gray-500 hover:text-[#f4e4bc]'
            }`}
          >
            {item.icon}
            {isActive && <span className="text-[9px] font-bold mt-1 font-cinzel">{item.label}</span>}
          </button>
        );
      })}
      </div>
    </nav>
  );
};
