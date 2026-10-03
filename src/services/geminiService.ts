
import { GoogleGenAI, Content } from "@google/genai";
import { GameState, DifficultyTier, Quest } from "../types";

// --- Helper: JSON Cleaner ---
const cleanJson = (text: string): string => {
    let clean = text.replace(/```json/g, '').replace(/```/g, '').trim();
    const firstBrace = clean.indexOf('{');
    const lastBrace = clean.lastIndexOf('}');
    const firstBracket = clean.indexOf('[');
    const lastBracket = clean.lastIndexOf(']');

    if (firstBracket !== -1 && lastBracket !== -1 && (firstBrace === -1 || firstBracket < firstBrace)) {
         return clean.substring(firstBracket, lastBracket + 1);
    }
    
    if (firstBrace !== -1 && lastBrace !== -1) {
        return clean.substring(firstBrace, lastBrace + 1);
    }
    
    return clean;
};

// --- API Key ---
// AI Studio injects process.env.API_KEY; everywhere else (local, StackBlitz, deploys)
// the key is entered in Settings and kept in localStorage.
export const API_KEY_STORAGE = "gemini_api_key";

export const getStoredApiKey = (): string => {
    try { return localStorage.getItem(API_KEY_STORAGE) || ""; } catch { return ""; }
};

export const setStoredApiKey = (key: string) => {
    try {
        if (key) localStorage.setItem(API_KEY_STORAGE, key);
        else localStorage.removeItem(API_KEY_STORAGE);
    } catch { /* storage unavailable */ }
};

const getApiKey = (): string => {
    const stored = getStoredApiKey();
    if (stored) return stored;
    // @ts-ignore - only defined when AI Studio injects it
    if (typeof process !== "undefined" && process.env?.API_KEY) return process.env.API_KEY;
    return "";
};

const getAI = () => {
    const apiKey = getApiKey();
    if (!apiKey) throw new Error("Gemini API key is not set. Link it in Settings.");
    return new GoogleGenAI({ apiKey });
};

// --- 1. Quest Intelligence (Gemini 3 Flash) ---
export const evaluateQuestDifficulty = async (questTitle: string): Promise<{ tier: DifficultyTier, gold: number, xp: number, comment: string }> => {
  try {
    const ai = getAI();
    const prompt = `
      Role: Strict Royal Butler.
      Task: Analyze the difficulty of this user task: "${questTitle}".
      
      Rules:
      1. If it's a simple habit (drinking water), Tier C.
      2. If it requires focus (reading 30m), Tier B.
      3. If it's a major project step or hard workout, Tier A.
      4. If it's life-changing, Tier S.
      
      Output JSON only: { "tier": "S"|"A"|"B"|"C"|"F", "gold": number, "xp": number, "comment": "One short witty Korean sentence." }
    `;
    const response = await ai.models.generateContent({ model: 'gemini-3-flash-preview', contents: prompt });
    return JSON.parse(cleanJson(response.text || "{}"));
  } catch (error) {
    console.error("AI Error:", error);
    return { tier: 'C', gold: 30, xp: 20, comment: "기록되었습니다." };
  }
};

export const generateSideQuests = async (userState: GameState): Promise<Quest[]> => {
    try {
        const ai = getAI();
        const prompt = `
            Role: Loyal Royal Butler in a Fantasy Otome Game.
            User: A noble lady who needs to build good habits (daily rituals).
            Current Status: Level ${userState.level}, ${userState.title}.
            
            Task: Recommend 3 daily habits (rituals) that fit a noble lady's self-improvement.
            Mix of: Health (drinking water, stretching), Knowledge (reading), or Dignity (cleaning, planning).
            
            Format: JSON Array.
            [{"title": "Habit Name", "difficulty": "C", "reward": 30, "xpReward": 15, "butlerComment": "Reason"}]
        `;
        const response = await ai.models.generateContent({
            model: 'gemini-3-flash-preview',
            contents: prompt
        });