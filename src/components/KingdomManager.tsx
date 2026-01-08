
import React, { useState } from 'react';
import { Castle, Utensils, Gift, Map, PlusCircle, Crown, Diamond, Coins, TrendingDown, TrendingUp } from 'lucide-react';
import { Expense } from '../types';

interface KingdomManagerProps {
  expenses: Expense[];
  addExpense: (amount: string, category: string, memo: string) => void;
  gold: number;
  onClaimWeeklyReward: () => void;
}

export const KingdomManager: React.FC<KingdomManagerProps> = ({ expenses, addExpense, gold, onClaimWeeklyReward }) => {
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("Food");
  const [memo, setMemo] = useState("");

  // Calculate Monthly Stats
  const now = new Date();
  const currentMonthExpenses = expenses.filter(e => {
      const d = new Date(e.date);
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear() && e.category !== 'Income';
  }).reduce((acc, cur) => acc + cur.amount, 0);

  const currentMonthIncome = expenses.filter(e => {
      const d = new Date(e.date);
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear() && e.category === 'Income';
  }).reduce((acc, cur) => acc + cur.amount, 0);

  const balance = currentMonthIncome - currentMonthExpenses;

  const handleSubmit = () => {
    addExpense(amount, category, memo);
    setAmount("");
    setMemo("");
  };

  const getIcon = (cat: string) => {
    switch (cat) {
      case 'Food': return <Utensils size={16} />;
      case 'Item': return <Gift size={16} />;
      case 'Luxury': return <Diamond size={16} />;
      case 'Income': return <Coins size={16} />;
      default: return <Map size={16} />;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in h-full flex flex-col pb-24 p-4">
      
      {/* Monthly Report Card */}
      <div className="bg-[#1a1a1a] p-5 rounded-xl border border-[#c5a059] shadow-2xl relative overflow-hidden">
          <div className="absolute -right-4 -top-4 text-[#c5a059]/10"><Crown size={100}/></div>
          <h2 className="text-[#c5a059] font-cinzel font-bold text-lg mb-4 flex items-center gap-2">
              <Castle size={20}/> ROYAL LEDGER ({now.getMonth() + 1}월)
          </h2>
          
          <div className="grid grid-cols-3 gap-2 text-center mb-4">
              <div className="bg-[#2c1e12] p-2 rounded border border-green-900/50">
                  <div className="text-[10px] text-green-400 font-bold mb-1 flex justify-center gap-1"><TrendingUp size={10}/> INCOME</div>
                  <div className="text-white font-bold text-sm">+{currentMonthIncome.toLocaleString()}</div>
              </div>
              <div className="bg-[#2c1e12] p-2 rounded border border-red-900/50">
                  <div className="text-[10px] text-red-400 font-bold mb-1 flex justify-center gap-1"><TrendingDown size={10}/> EXPENSE</div>
                  <div className="text-white font-bold text-sm">-{currentMonthExpenses.toLocaleString()}</div>
              </div>
              <div className="bg-[#2c1e12] p-2 rounded border border-[#c5a059]/30">
                  <div className="text-[10px] text-[#c5a059] font-bold mb-1">BALANCE</div>
                  <div className={`font-bold text-sm ${balance >= 0 ? 'text-[#c5a059]' : 'text-red-500'}`}>{balance.toLocaleString()}</div>
              </div>
          </div>
          
          <p className="text-[10px] text-gray-500 italic text-center">
             * 매일 자정, 업무 수행 평가(Daily Routine)에 따라 급여가 자동 입금됩니다.
          </p>
      </div>

      {/* Input Form */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
        <h4 className="font-bold mb-3 text-[#2c1e12] text-sm">장부 기록 (Manual Entry)</h4>
        <div className="space-y-3">
            <div className="flex gap-2">
                <input
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="w-2/3 border border-gray-300 p-2 rounded bg-gray-50 outline-none text-[#2c1e12] font-serif text-sm"
                    placeholder="금액 (G)"
                />
                <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-1/3 border border-gray-300 p-2 rounded bg-gray-50 outline-none text-[#2c1e12] text-sm"
                >
                    <option value="Food">식비</option>
                    <option value="Item">물품</option>
                    <option value="Luxury">사치</option>
                    <option value="Travel">교통</option>
                    <option value="Income">수입</option>
                </select>
            </div>
            <input
                type="text"
                value={memo}
                onChange={(e) => setMemo(e.target.value)}
                className="w-full border border-gray-300 p-2 rounded bg-gray-50 outline-none text-[#2c1e12] font-serif text-sm"
                placeholder="내역 메모..."
            />
            <button
                onClick={handleSubmit}
                className="w-full bg-[#2c1e12] text-[#f4e4bc] font-bold py-3 rounded shadow hover:bg-[#3e2b1b] transition-colors flex items-center justify-center gap-2 text-sm"
            >
                <PlusCircle size={16} /> 기록하기
            </button>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="flex-1 overflow-y-auto custom-scroll">
        <h4 className="font-bold text-[#8b4513] mb-2 text-xs border-b border-[#8b4513]/20 pb-1">최근 거래 내역</h4>
        <div className="space-y-2">
          {expenses.map((b) => (
            <div key={b.id} className="bg-white p-3 rounded border border-gray-100 shadow-sm flex justify-between items-center">
              <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-full ${b.category === 'Income' ? 'bg-green-100 text-green-700' : 'bg-[#f4e4bc] text-[#8b4513]'}`}>
                      {getIcon(b.category)}
                  </div>
                  <div>
                      <div className="font-bold text-sm text-[#2c1e12]">{b.memo || b.category}</div>
                      <div className="text-[10px] text-gray-400">{b.date}</div>
                  </div>
              </div>
              <div className={`text-sm font-bold font-cinzel ${b.category === 'Income' ? 'text-green-600' : 'text-[#8b0000]'}`}>
                  {b.category === 'Income' ? '+' : '-'}{parseInt(b.amount.toString()).toLocaleString()} G
              </div>
            </div>
          ))}
          {expenses.length === 0 && <p className="text-center text-gray-400 py-4 text-xs">내역이 없습니다.</p>}
        </div>
      </div>
    </div>
  );
};
