export type TabId = 'home' | 'love' | 'writing' | 'ledger' | 'diary';

export type Season = 'Spring' | 'Summer' | 'Autumn' | 'Winter';

export type DifficultyTier = 'S' | 'A' | 'B' | 'C' | 'F';

export interface Stats {
  STR: number;
  INT: number;
  DEX: number;
  CHR: number;
  WIS: number;
  LUK: number;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  cost: number;
  unlocked: boolean;
  category: 'Economy' | 'Social' | 'Adventure';
  effectType: 'gold_boost' | 'charm' | 'xp_boost';
  effectValue: number;
}

export interface ShopItem {
  id: string;
  name: string;
  price: number;
  type: 'consumable' | 'secret_tool' | 'key_item' | 'gift' | 'special';
  effectDesc: string;
  maxStock?: number;
}

export interface Secret {
  id: string;
  title: string;
  description: string;
  isDiscovered: boolean;
  reqItem?: string;
}

export interface MaleLead {
  id: string;
  name: string;
  affection: number;
  color: string;
  desc: string;
  appearancePrompt: string;
  hiddenThoughts: string[];
  secrets: Secret[];
  imageUrl?: string;
  isImageLocked?: boolean;
  isVillain?: boolean;
}

export interface Choice {
  text: string;
  effect?: (state: GameState) => Partial<GameState>;
  alertMsg?: string;
}

export interface DialogueScript {
  speaker: string;
  text: string;
  choices?: Choice[];
}

export interface StoryChapter {
  id: string;
  type: 'Main' | 'Route';
  relatedLeadId?: string;
  title: string;
  description: string;
  reqStats?: Partial<Stats>;
  reqItem?: string;
  reqAffection?: { leadId: string; min: number };
  isUnlocked: boolean;
  isCompleted: boolean;
  cgPromptBase: string;
  cgUrl?: string;
  dialogueScripts: DialogueScript[];
}

export interface Quest {
  id: number;
  title: string;
  completed: boolean;
  reward: number;
  xpReward: number;
  isDaily?: boolean;
  difficulty: DifficultyTier;
  butlerComment?: string;
  type: 'Normal' | 'Social';
}

export interface Expense {
  id: number;
  amount: number;
  category: 'Food' | 'Item' | 'Luxury' | 'Travel' | 'Income';
  memo: string;
  date: string;
}

export interface WritingLog {
  date: string;
  wordCount: number;
}

export interface DailyRecord {
  date: string;
  completionRate: number;
  completedQuestIds: number[];
}

export interface GameState {
  name: string;
  title: string;
  userAppearancePrompt: string;
  level: number;
  xp: number;
  maxXp: number;
  hp: number;
  maxHp: number;
  gold: number;
  skillPoints: number;
  reputation: number;
  corruption: number;
  currentDate: string;
  season: Season;
  dayCount: number;
  lastLoginDate: string;
  stats: Stats;
  quests: Quest[];
  kingdom: Expense[];
  maleLeads: MaleLead[];
  longTermGoal: string;
  writingLogs: WritingLog[];
  skills: Skill[];
  inventory: string[];
  calendar: DailyRecord[];
  storyChapters: StoryChapter[];
  userImageUrl?: string;
  backgroundImageUrl?: string;
  isUserImageLocked?: boolean;
  isBgImageLocked?: boolean;
}
