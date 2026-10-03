import React, { useState } from 'react';
import { Mail, KeyRound, Loader2, LogIn, UserPlus } from 'lucide-react';
import { logIn, signUp, MIN_PASSWORD_LENGTH } from '../services/authService';

interface AuthScreenProps {
  onAuthenticated: (email: string) => void;
}

export const AuthScreen: React.FC<AuthScreenProps> = ({ onAuthenticated }) => {
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (mode === 'signup' && password !== passwordConfirm) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }
    setLoading(true);
    try {
      const user = mode === 'signup' ? await signUp(email, password) : await logIn(email, password);
      onAuthenticated(user);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setMode(m => (m === 'login' ? 'signup' : 'login'));
    setError(null);
    setPasswordConfirm("");
  };

  const inputClass = "w-full bg-transparent text-white placeholder-gray-500 outline-none text-sm";

  return (
    <div className="h-screen w-full max-w-md mx-auto flex flex-col items-center justify-center p-6 bg-[#1a1212] relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#2c1e12] via-[#1a1212] to-black"></div>
      <div className="relative z-10 w-full animate-fade-in">
        <div className="text-center mb-8">
          <div className="text-[#c5a059] text-[10px] font-bold tracking-[0.3em] mb-2">THE COUNTESS CHRONICLES</div>
          <h1 className="text-3xl font-cinzel font-bold text-[#c5a059]">GRIMOIRE</h1>
          <p className="text-gray-400 text-xs mt-2 font-serif">현실의 마도서</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-black/50 border border-[#c5a059]/50 rounded-xl p-6 flex flex-col gap-4 shadow-2xl backdrop-blur">
          <h2 className="text-white font-bold text-center">{mode === 'login' ? '로그인' : '회원가입'}</h2>

          <label className="flex items-center gap-3 border-b border-gray-600 focus-within:border-[#c5a059] pb-2">
            <Mail size={16} className="text-[#c5a059] shrink-0" />
            <input type="email" autoComplete="email" required placeholder="이메일" value={email} onChange={e => setEmail(e.target.value)} className={inputClass} />
          </label>
          <label className="flex items-center gap-3 border-b border-gray-600 focus-within:border-[#c5a059] pb-2">
            <KeyRound size={16} className="text-[#c5a059] shrink-0" />
            <input type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} required minLength={mode === 'signup' ? MIN_PASSWORD_LENGTH : undefined} placeholder={mode === 'signup' ? `비밀번호 (${MIN_PASSWORD_LENGTH}자 이상)` : '비밀번호'} value={password} onChange={e => setPassword(e.target.value)} className={inputClass} />
          </label>
          {mode === 'signup' && (
            <label className="flex items-center gap-3 border-b border-gray-600 focus-within:border-[#c5a059] pb-2">
              <KeyRound size={16} className="text-[#c5a059] shrink-0" />
              <input type="password" autoComplete="new-password" required placeholder="비밀번호 확인" value={passwordConfirm} onChange={e => setPasswordConfirm(e.target.value)} className={inputClass} />
            </label>
          )}

          {error && <p role="alert" className="text-red-400 text-xs text-center">{error}</p>}

          <button type="submit" disabled={loading} className="w-full py-3 bg-[#c5a059] text-[#1a1212] font-bold rounded-lg flex items-center justify-center gap-2 hover:brightness-110 disabled:opacity-50">
            {loading ? <Loader2 size={18} className="animate-spin" /> : mode === 'login' ? <LogIn size={18} /> : <UserPlus size={18} />}
            {mode === 'login' ? '로그인' : '가입하고 시작하기'}
          </button>

          <button type="button" onClick={switchMode} className="text-xs text-gray-400 hover:text-[#c5a059]">
            {mode === 'login' ? '처음이신가요? 회원가입' : '이미 계정이 있나요? 로그인'}
          </button>
        </form>

        <p className="text-[10px] text-gray-500 text-center mt-4 leading-relaxed">
          계정과 진행 상황은 이 브라우저에만 저장됩니다.<br />다른 기기와는 공유되지 않으니, 설정의 '내보내기'로 백업하세요.
        </p>
      </div>
    </div>
  );
};
