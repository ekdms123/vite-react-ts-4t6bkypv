import { GameState, DifficultyTier, Quest } from "../types";

// Offline stand-ins for the former Gemini features: rule-based, no network.

const pick = <T,>(list: T[]): T => list[Math.floor(Math.random() * list.length)];

// --- 1. Quest Difficulty ---
const TIER_KEYWORDS: { tier: DifficultyTier; words: string[] }[] = [
    { tier: 'S', words: ['이직', '창업', '출간', '완주', '마라톤', '합격', '시험', '자격증', '이사'] },
    { tier: 'A', words: ['프로젝트', '마감', '운동', '헬스', '러닝', '보고서', '발표', '원고', '대청소', '시간'] },
    { tier: 'B', words: ['독서', '공부', '글쓰기', '집필', '정리', '청소', '요리', '복습', '산책', '30분'] },
];

const TIER_REWARDS: Record<DifficultyTier, { gold: number; xp: number; comments: string[] }> = {
    S: { gold: 300, xp: 200, comments: ["가문의 운명이 걸린 과업이군요. 무운을 빕니다.", "이것을 해낸다면 백작가가 아가씨를 다시 보게 될 겁니다."] },
    A: { gold: 120, xp: 80, comments: ["쉽지 않은 일입니다. 끝까지 해내시길.", "귀족의 품격은 이런 데서 드러나지요."] },
    B: { gold: 60, xp: 40, comments: ["집중력이 필요한 일이군요. 차를 준비해 두겠습니다.", "꾸준함이야말로 최고의 무기입니다."] },
    C: { gold: 30, xp: 20, comments: ["작은 습관이 생존을 만듭니다.", "기록되었습니다. 잊지 마시길."] },
    F: { gold: 10, xp: 5, comments: ["기록은 해두겠습니다만..."] },
};

export const evaluateQuestDifficulty = (questTitle: string): { tier: DifficultyTier, gold: number, xp: number, comment: string } => {
    const tier = TIER_KEYWORDS.find(t => t.words.some(w => questTitle.includes(w)))?.tier || 'C';
    const reward = TIER_REWARDS[tier];
    return { tier, gold: reward.gold, xp: reward.xp, comment: pick(reward.comments) };
};

// --- 2. Daily Ritual Suggestions ---
const RITUALS: { title: string; difficulty: DifficultyTier; butlerComment: string }[] = [
    { title: "물 8잔 마시기", difficulty: 'C', butlerComment: "독이 든 차보다는 맑은 물이 낫지요." },
    { title: "아침 스트레칭 10분", difficulty: 'C', butlerComment: "굳은 몸으로는 암살자를 피할 수 없습니다." },
    { title: "책 30분 읽기", difficulty: 'B', butlerComment: "지식은 가장 날카로운 검입니다." },
    { title: "오늘의 지출 기록하기", difficulty: 'C', butlerComment: "새어머니처럼 장부를 비우셔서는 안 됩니다." },
    { title: "책상 정리하기", difficulty: 'C', butlerComment: "정돈된 서재가 정돈된 머리를 만듭니다." },
    { title: "산책 20분", difficulty: 'B', butlerComment: "영지를 둘러보는 것도 가주의 일입니다." },
    { title: "내일 일정 계획하기", difficulty: 'B', butlerComment: "계획 없는 자가 먼저 무너집니다." },
    { title: "일기 쓰기", difficulty: 'C', butlerComment: "회귀자는 기록을 남겨야 합니다." },
    { title: "운동 30분", difficulty: 'A', butlerComment: "리안 경도 감탄할 체력이 필요합니다." },
    { title: "자정 전에 잠들기", difficulty: 'B', butlerComment: "잠든 자는 죽는다지만, 못 잔 자는 더 빨리 죽습니다." },
];

export const generateSideQuests = (userState: GameState): Quest[] => {
    const existing = new Set(userState.quests.map(q => q.title));
    const pool = RITUALS.filter(r => !existing.has(r.title)).sort(() => Math.random() - 0.5).slice(0, 3);
    const now = Date.now();
    return pool.map((r, i) => ({
        id: now + i,
        title: r.title,
        completed: false,
        reward: TIER_REWARDS[r.difficulty].gold,
        xpReward: TIER_REWARDS[r.difficulty].xp,
        difficulty: r.difficulty,
        butlerComment: r.butlerComment,
        type: 'Normal',
    }));
};

// --- 3. Oracle Hint ---
export const getOracleAdvice = (state: GameState, itemName: (id: string) => string | undefined): string => {
    const next = state.storyChapters.find(c => c.type === 'Main' && !c.isCompleted);
    if (!next) return "모든 운명을 넘어섰습니다. 이제 당신이 이 세계의 주인입니다.";
    const needs: string[] = [];
    if (next.reqItem && !state.inventory.includes(next.reqItem)) needs.push(`'${itemName(next.reqItem) || next.reqItem}'을(를) 손에 넣으십시오`);
    if (next.reqStats) {
        Object.entries(next.reqStats).forEach(([stat, min]) => {
            const current = state.stats[stat as keyof GameState['stats']];
            if (min !== undefined && current < min) needs.push(`${stat}을(를) ${min}까지 올리십시오 (현재 ${current})`);
        });
    }
    if (needs.length === 0) return `[${next.title}] 운명의 문이 열려 있습니다. 망설이지 마십시오.`;
    return `[${next.title}] 다음 운명을 위해 ${needs.join(", ")}.`;
};

// --- 4. Character Lines ---
const LINES: Record<string, { low: string[]; mid: string[]; high: string[] }> = {
    "카엘루스": {
        low: ["용건만 말해.", "내 시간을 낭비하지 마라."],
        mid: ["...오늘은 쫓아내지 않겠다.", "추운데 왜 나와 있지? 들어가."],
        high: ["이번 생에서는 반드시 너를 지킨다.", "네가 웃으면, 아홉 번의 겨울이 녹는 것 같아."],
    },
    "리안": {
        low: ["아가씨, 명령을 내려 주십시오.", "주변은 안전합니다."],
        mid: ["오늘은 표정이 밝으시네요. 다행입니다.", "검보다 아가씨의 웃음을 지키고 싶습니다."],
        high: ["황제가 아니라, 당신에게 충성을 맹세합니다.", "제 검은 이제 당신의 것입니다."],
    },
    "시온": {
        low: ["흥미 없는 변수군.", "실험 중이야. 방해하지 마."],
        mid: ["네 행동 패턴은 예측이 안 돼. 재밌네.", "오늘 로그에 네 이름이 열두 번 찍혔어."],
        high: ["이 세계가 가짜라도, 너는 진짜야.", "서버가 무너져도 너만은 백업해 둘게."],
    },
};

export const getVNDialogue = (leadName: string, affection: number): string => {
    const lines = LINES[leadName];
    if (!lines) return "...";
    return pick(affection >= 60 ? lines.high : affection >= 25 ? lines.mid : lines.low);
};
