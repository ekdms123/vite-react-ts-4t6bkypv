
import React, { useState, useEffect, useRef } from 'react';
import { Settings, X, Loader2, UserCog, Download, Upload, Image as ImageIcon, Copy, Check, Lock, Unlock, Wand2, Film, Send, Sparkles, Palette, Book, ShoppingBag, ScrollText, MapPin, RefreshCcw, Scroll, Ghost, Sword, Feather, BarChart2, Link, LogIn, Save, FileJson, Crown, Trophy } from 'lucide-react';
import { Navbar } from './components/Navbar';
import { GameHeader } from './components/GameHeader'; 
import { QuestBoard } from './components/QuestBoard'; 
import { KingdomManager } from './components/KingdomManager';
import { Grimoire } from './components/Grimoire';
import { Romance } from './components/Romance';
import { Shop } from './components/Shop';
import { CalendarView } from './components/CalendarView'; 
import { StatusCard } from './components/StatusCard'; 
import { getOracleAdvice, generateCharacterPortrait, generateBackground, evaluateQuestDifficulty, editMagicalImage, generateVideoFromImage, generateSideQuests } from './services/geminiService';
import { GameState, TabId, Skill, ShopItem, MaleLead, Quest, StoryChapter, Choice, Expense, Secret } from './types';
import { ResponsiveContainer, BarChart, Bar, XAxis, Tooltip } from 'recharts';

// --- [OMNI-ARCHITECT] DATA CORE: THE COUNTESS CHRONICLES (HARD MODE 365) ---

// 1. SKILLS
const INITIAL_SKILLS: Skill[] = [
  { id: 'eco_1', name: '장부 조작', description: '골드 획득량 15% 증가. (Corruption +1/day)', cost: 0, unlocked: false, category: 'Economy', effectType: 'gold_boost', effectValue: 0.15 },
  { id: 'soc_1', name: '가면 무도회', description: '화술(Charm) +20%. 거짓말이 능숙해집니다.', cost: 500, unlocked: false, category: 'Social', effectType: 'charm', effectValue: 1.2 },
  { id: 'int_1', name: '독약 감별사', description: '암살 이벤트 생존 확률 증가.', cost: 1000, unlocked: false, category: 'Adventure', effectType: 'xp_boost', effectValue: 0.1 },
];

// 2. SHOP (Story Keys)
const SHOP_ITEMS: ShopItem[] = [
  // Consumables
  { id: 'potion_stamina', name: '각성제 (Black Coffee)', price: 200, type: 'consumable', effectDesc: 'HP 30 회복. 잠들면 죽는다.', maxStock: 99 },
  { id: 'scroll_escape', name: '비상 탈출 스크롤', price: 500, type: 'consumable', effectDesc: '배드 엔딩 직전에 1회 회피 가능.', maxStock: 3 },
  // Secrets
  { id: 'tool_monocle', name: '진실의 단안경', price: 5000, type: 'secret_tool', effectDesc: '[카엘루스]의 속마음을 엿볼 수 있습니다.', maxStock: 1 },
  { id: 'tool_old_letter', name: '피 묻은 편지', price: 5000, type: 'secret_tool', effectDesc: '[리안]의 과거 기억을 해금합니다.', maxStock: 1 },
  { id: 'tool_glitch_shard', name: '오류난 마석 조각', price: 8000, type: 'secret_tool', effectDesc: '[시온]의 시스템 로그를 해독합니다.', maxStock: 1 },
  // Spring Keys
  { id: 'key_dress', name: '미드나잇 벨벳 드레스', price: 3000, type: 'key_item', effectDesc: '[봄] 사교계 데뷔 필수품.', maxStock: 1 },
  { id: 'key_invitation', name: '황실 무도회 초대장', price: 5000, type: 'key_item', effectDesc: '[봄] 황태자를 만날 수 있는 유일한 기회.', maxStock: 1 },
  { id: 'key_seal_fake', name: '위조된 가주 인장', price: 4500, type: 'key_item', effectDesc: '[봄] 임시로 가문의 권한을 행사합니다.', maxStock: 1 },
  // Summer Keys
  { id: 'key_antidote_ring', name: '해독의 루비 반지', price: 8000, type: 'key_item', effectDesc: '[여름] 새어머니의 독살 시도를 막습니다.', maxStock: 1 },
  { id: 'key_herbs', name: '엘릭서 원료 (약초)', price: 6000, type: 'key_item', effectDesc: '[여름] 영지에 퍼진 전염병을 치료합니다.', maxStock: 1 },
  { id: 'key_trade_permit', name: '동방 무역 허가증', price: 10000, type: 'key_item', effectDesc: '[여름] 막대한 자금을 확보할 수 있습니다.', maxStock: 1 },
  // Autumn Keys
  { id: 'key_ledger_real', name: '백작가의 진짜 장부', price: 15000, type: 'key_item', effectDesc: '[가을] 횡령 증거 확보.', maxStock: 1 },
  { id: 'key_permit', name: '사병 양성 허가증', price: 20000, type: 'key_item', effectDesc: '[가을] 전쟁을 대비해 병력을 모을 권리.', maxStock: 1 },
  { id: 'key_magic_stone', name: '고대 방어 마석', price: 25000, type: 'key_item', effectDesc: '[가을] 저택의 결계를 강화합니다.', maxStock: 1 },
  // Winter Keys
  { id: 'key_assassin_contract', name: '그림자 길드 계약서', price: 30000, type: 'key_item', effectDesc: '[겨울] 최후의 수단.', maxStock: 1 },
  { id: 'key_crown', name: '가주의 인장 (진품)', price: 50000, type: 'key_item', effectDesc: '[엔딩] 진정한 백작가의 주인이 됩니다.', maxStock: 1 },
  // Gifts
  { id: 'gift_chess', name: '흑요석 체스말', price: 3000, type: 'gift', effectDesc: '[카엘루스] 선호.', maxStock: 5 },
  { id: 'gift_sword_oil', name: '최고급 검 오일', price: 2500, type: 'gift', effectDesc: '[리안] 선호.', maxStock: 5 },
  { id: 'gift_scroll', name: '고대 마법 스크롤', price: 4000, type: 'gift', effectDesc: '[시온] 선호.', maxStock: 5 },
];

// 3. CHARACTERS
const INITIAL_MALE_LEADS: MaleLead[] = [
  { 
    id: "kael", name: "카엘루스", affection: 0, color: "#1e3a8a", 
    desc: "북부 대공. 나의 처형을 묵인했던 냉혈한.", 
    appearancePrompt: "Cold handsome anime duke, sharp blue eyes, black hair slicked back, wearing heavy fur coat and military uniform, snowy landscape background, looking down with arrogance, masterpiece, 8k resolution",
    hiddenThoughts: ["제발... 내게서 멀어져라.", "네가 미워해야만, 네가 산다."],
    secrets: [{ id: 'sec_kael_1', title: '회귀자 (The Regressor)', description: '그는 당신이 죽는 것을 9번이나 지켜보았습니다.', isDiscovered: false, reqItem: 'tool_monocle' }]
  },
  { 
    id: "rian", name: "리안", affection: 15, color: "#b91c1c", 
    desc: "나의 호위기사. 유일하게 믿을 수 있는 사람.", 
    appearancePrompt: "Warm loyal anime knight, messy red hair, golden eyes, shining silver armor with royal crest, holding a sword protectively, sunny garden background, gentle smile, masterpiece, 8k resolution",
    hiddenThoughts: ["황제 폐하의 명령은 절대적이다.", "아가씨를 베어야 하는 날이 온다면..."],
    secrets: [{ id: 'sec_rian_1', title: '황제의 사냥개 (The Assassin)', description: '그는 당신을 감시하고 암살하라는 밀명을 받았습니다.', isDiscovered: false, reqItem: 'tool_old_letter' }]
  },
  { 
    id: "sion", name: "시온", affection: 5, color: "#5b21b6", 
    desc: "미치광이 마탑주. 세상의 멸망을 바라는 자.", 
    appearancePrompt: "Mysterious anime mage, long silver hair, purple glowing eyes, dark robes with floating runes, magical laboratory background, insane smirk, magical particles, masterpiece, 8k resolution",
    hiddenThoughts: ["System Error: Affection overflow.", "이 세계는 가짜야."],
    secrets: [{ id: 'sec_sion_1', title: '관리자 (The Admin)', description: '그는 이 세계가 반복되는 게임이라는 것을 알고 있습니다.', isDiscovered: false, reqItem: 'tool_glitch_shard' }]
  },
];

// 4. THE EPIC SAGA (45 Chapters)
const STORY_CHAPTERS: StoryChapter[] = [
    // --- SPRING (Main 1-8) ---
    { id: 'main_1', type: 'Main', title: 'Spring 1. 장례식장의 아침', description: '[D-365] 회귀 첫날. 새어머니의 가짜 눈물.', isUnlocked: true, isCompleted: false, cgPromptBase: "Anime noble lady in black funeral dress, raining cemetery, holding umbrella, cold expression", dialogueScripts: [{ speaker: "나", text: "눈물 거두시죠, 어머니. 역겨우니까.", choices: [{ text: "냉정하게 대처 (INT+1)", effect: s=>({stats:{...s.stats, INT: s.stats.INT+1}}) }, { text: "연기하며 기절 (CHR+1)", effect: s=>({reputation: s.reputation+5}) }] }] },
    { id: 'main_2', type: 'Main', title: 'Spring 2. 텅 빈 금고', description: '자금이 없다. 살아남으려면 돈이 필요하다.', reqStats: { INT: 5 }, isUnlocked: false, isCompleted: false, cgPromptBase: "Empty safe vault, spiderwebs, shocked noble lady holding lamp", dialogueScripts: [{ speaker: "나", text: "벌써 다 빼돌렸군. 당장 돈을 벌어야 해." }] },
    { id: 'main_3', type: 'Main', title: 'Spring 3. 다락방의 유령', description: '하녀들의 기강을 잡아야 한다.', reqStats: { CHR: 10 }, isUnlocked: false, isCompleted: false, cgPromptBase: "Noble lady looking down at kneeling maids, authoritative", dialogueScripts: [{ speaker: "나", text: "내 물건에 손댄 자, 손목을 내놓아라." }] },
    { id: 'main_4', type: 'Main', title: 'Spring 4. 가짜 인장', description: '가문의 권한을 행사하려면 인장이 필요하다.', reqItem: 'key_seal_fake', isUnlocked: false, isCompleted: false, cgPromptBase: "Hand stamping document with golden seal, candlelight", dialogueScripts: [{ speaker: "나", text: "이걸로 예산을 동결시킨다." }] },
    { id: 'main_5', type: 'Main', title: 'Spring 5. 사교계 데뷔', description: '나의 건재함을 알려야 한다.', reqItem: 'key_dress', isUnlocked: false, isCompleted: false, cgPromptBase: "Grand ballroom, lady in midnight blue dress entering, spotlight", dialogueScripts: [{ speaker: "귀족들", text: "저 드레스... 백작 영애가 저렇게 아름다웠나?" }] },
    { id: 'main_6', type: 'Main', title: 'Spring 6. 황태자의 시선', description: '황태자가 흥미를 보인다.', reqItem: 'key_invitation', isUnlocked: false, isCompleted: false, cgPromptBase: "Prince with golden hair reaching out hand, ballroom balcony", dialogueScripts: [{ speaker: "황태자", text: "그대, 소문보다 흥미롭군." }] },
    { id: 'main_7', type: 'Main', title: 'Spring 7. 빗속의 조우', description: '카엘루스와 마주쳤다.', isUnlocked: false, isCompleted: false, cgPromptBase: "Raining garden, cold duke walking past, sad atmosphere", dialogueScripts: [{ speaker: "카엘루스", text: "내 눈앞에 띄지 마." }] },
    { id: 'main_8', type: 'Main', title: 'Spring 8. 봄의 끝', description: '첫 계절이 지났다.', isUnlocked: false, isCompleted: false, cgPromptBase: "Lady looking out window at cherry blossoms", dialogueScripts: [{ speaker: "나", text: "이제 진짜 지옥 시작이야." }] },

    // --- SUMMER (Main 9-15) ---
    { id: 'main_9', type: 'Main', title: 'Summer 1. 독차', description: '새어머니가 독을 탔다.', reqItem: 'key_antidote_ring', isUnlocked: false, isCompleted: false, cgPromptBase: "Tea party, ruby ring glowing red near tea cup", dialogueScripts: [{ speaker: "나", text: "차 색깔이 핏빛이네요.", choices: [{text: "협박하여 돈 뜯기 (Gold+)", effect: s=>({gold: s.gold+2000})}, {text: "폭로하기 (Reputation+)", effect: s=>({reputation: s.reputation+20})}] }] },
    { id: 'main_10', type: 'Main', title: 'Summer 2. 가뭄', description: '영지민들이 굶주린다.', reqStats: { WIS: 10 }, isUnlocked: false, isCompleted: false, cgPromptBase: "Dried wheat field, burning sun", dialogueScripts: [{ speaker: "나", text: "창고를 개방해라." }] },
    { id: 'main_11', type: 'Main', title: 'Summer 3. 역병', description: '치료제가 필요하다.', reqItem: 'key_herbs', isUnlocked: false, isCompleted: false, cgPromptBase: "Slums, lady in mask distributing medicine", dialogueScripts: [{ speaker: "나", text: "한 명도 포기하지 마!" }] },
    { id: 'main_12', type: 'Main', title: 'Summer 4. 무역로', description: '자금 확보를 위한 무역.', reqItem: 'key_trade_permit', isUnlocked: false, isCompleted: false, cgPromptBase: "Busy port, merchant ships, gold coins", dialogueScripts: [{ speaker: "나", text: "독점 계약입니다." }] },
    { id: 'main_13', type: 'Main', title: 'Summer 5. 마탑주', description: '시온의 방문.', isUnlocked: false, isCompleted: false, cgPromptBase: "Mage examining patient, purple magic", dialogueScripts: [{ speaker: "시온", text: "이건 자연적인 병이 아니야. 코드야." }] },
    { id: 'main_14', type: 'Main', title: 'Summer 6. 첩자', description: '내부에 적이 있다.', reqStats: { INT: 15 }, isUnlocked: false, isCompleted: false, cgPromptBase: "Shadowy figure running in hallway", dialogueScripts: [{ speaker: "나", text: "쥐새끼가 있었구나." }] },
    { id: 'main_15', type: 'Main', title: 'Summer 7. 폭풍우', description: '거대한 폭풍.', isUnlocked: false, isCompleted: false, cgPromptBase: "Thunderstorm hitting mansion", dialogueScripts: [{ speaker: "나", text: "폭풍이 지나면 세상이 바뀔 거야." }] },

    // --- AUTUMN (Main 16-23) ---
    { id: 'main_16', type: 'Main', title: 'Autumn 1. 장부 쟁탈전', description: '진짜 장부를 찾아라.', reqItem: 'key_ledger_real', isUnlocked: false, isCompleted: false, cgPromptBase: "Opening secret safe behind painting", dialogueScripts: [{ speaker: "나", text: "찾았다. 횡령 증거." }] },
    { id: 'main_17', type: 'Main', title: 'Autumn 2. 사병 양성', description: '무력이 필요하다.', reqItem: 'key_permit', isUnlocked: false, isCompleted: false, cgPromptBase: "Knights training at sunset", dialogueScripts: [{ speaker: "나", text: "나를 위해 죽을 자만 남으라." }] },
    { id: 'main_18', type: 'Main', title: 'Autumn 3. 정보 길드', description: '약점을 샀다.', reqStats: { LUK: 15 }, isUnlocked: false, isCompleted: false, cgPromptBase: "Shady tavern, exchanging scroll for gold", dialogueScripts: [{ speaker: "정보상", text: "황제도 모르는 비밀입니다." }] },
    { id: 'main_19', type: 'Main', title: 'Autumn 4. 결계', description: '방어 마석 설치.', reqItem: 'key_magic_stone', isUnlocked: false, isCompleted: false, cgPromptBase: "Mansion surrounded by blue magic dome", dialogueScripts: [{ speaker: "시온", text: "드래곤도 못 뚫어." }] },
    { id: 'main_20', type: 'Main', title: 'Autumn 5. 가면 무도회', description: '은밀한 거래.', isUnlocked: false, isCompleted: false, cgPromptBase: "People in venetian masks, mysterious", dialogueScripts: [{ speaker: "나", text: "가면 뒤에 숨으니 본성이 나오네." }] },
    { id: 'main_21', type: 'Main', title: 'Autumn 6. 리안의 고백', description: '기사의 흔들림.', isUnlocked: false, isCompleted: false, cgPromptBase: "Knight kneeling in rain, crying", dialogueScripts: [{ speaker: "리안", text: "저는 당신을 벨 수 없습니다." }] },
    { id: 'main_22', type: 'Main', title: 'Autumn 7. 숙청', description: '배신자 처단.', isUnlocked: false, isCompleted: false, cgPromptBase: "Dungeon cell, cold expression", dialogueScripts: [{ speaker: "나", text: "자비는 없다." }] },
    { id: 'main_23', type: 'Main', title: 'Autumn 8. 전운', description: '전쟁 준비.', isUnlocked: false, isCompleted: false, cgPromptBase: "Red autumn leaves, marching army", dialogueScripts: [{ speaker: "나", text: "겨울이 오면 끝낼 거야." }] },

    // --- WINTER (Main 24-30) ---
    { id: 'main_24', type: 'Main', title: 'Winter 1. 고립', description: '폭설과 고립.', reqStats: { STR: 10 }, isUnlocked: false, isCompleted: false, cgPromptBase: "Castle in snowstorm, soldiers on wall", dialogueScripts: [{ speaker: "나", text: "성문을 잠궈라." }] },
    { id: 'main_25', type: 'Main', title: 'Winter 2. 암살', description: '그림자 길드의 습격.', reqItem: 'key_assassin_contract', isUnlocked: false, isCompleted: false, cgPromptBase: "Assassin jumping through window, dagger clash", dialogueScripts: [{ speaker: "나", text: "내 목숨 값은 비싸." }] },
    { id: 'main_26', type: 'Main', title: 'Winter 3. 지원군', description: '카엘루스의 참전.', isUnlocked: false, isCompleted: false, cgPromptBase: "Blue knights charging in snow", dialogueScripts: [{ speaker: "카엘루스", text: "늦어서 미안하군." }] },
    { id: 'main_27', type: 'Main', title: 'Winter 4. 마법 전쟁', description: '시온의 폭주.', isUnlocked: false, isCompleted: false, cgPromptBase: "Purple meteors falling, destruction", dialogueScripts: [{ speaker: "시온", text: "리미트 해제." }] },
    { id: 'main_28', type: 'Main', title: 'Winter 5. 결전', description: '최후의 전투.', isUnlocked: false, isCompleted: false, cgPromptBase: "Burning courtyard, lady leading charge", dialogueScripts: [{ speaker: "나", text: "이 땅의 주인은 나다!" }] },
    { id: 'main_29', type: 'Main', title: 'Winter 6. 심판', description: '승리와 복수.', isUnlocked: false, isCompleted: false, cgPromptBase: "Throne room, enemy kneeling", dialogueScripts: [{ speaker: "나", text: "전부 뺏어주지." }] },
    { id: 'main_30', type: 'Main', title: 'Final. 대관식', description: '새로운 가주.', reqItem: 'key_crown', isUnlocked: false, isCompleted: false, cgPromptBase: "Coronation, wearing crown, victory", dialogueScripts: [{ speaker: "시스템", text: "생존 성공.", choices: [{text:"철혈의 여제 (Corruption)", effect: s=>({title:"철혈의 여제"})}, {text:"성군 (Reputation)", effect: s=>({title:"빛의 인도자"})}] }] },

    // --- KAEL ROUTE (5 Episodes) ---
    { id: 'kael_1', type: 'Route', relatedLeadId: 'kael', title: 'Ep 1. 거절', description: '그가 나를 밀어낸다.', reqAffection: {leadId: 'kael', min: 20}, isUnlocked: false, isCompleted: false, cgPromptBase: "Snowy forest, duke turning back", dialogueScripts: [{speaker:"카엘루스", text:"다가오지 마."}] },
    { id: 'kael_2', type: 'Route', relatedLeadId: 'kael', title: 'Ep 2. 악몽', description: '그의 악몽.', reqAffection: {leadId: 'kael', min: 40}, isUnlocked: false, isCompleted: false, cgPromptBase: "Duke sleeping, sweating, lady wiping forehead", dialogueScripts: [{speaker:"나", text:"괜찮아요."}] },
    { id: 'kael_3', type: 'Route', relatedLeadId: 'kael', title: 'Ep 3. 기억', description: '9번의 회귀.', reqItem: 'tool_monocle', reqAffection: {leadId: 'kael', min: 60}, isUnlocked: false, isCompleted: false, cgPromptBase: "Flashback, duke crying at grave", dialogueScripts: [{speaker:"나", text:"나를 위해 죽었던 건가요?"}] },
    { id: 'kael_4', type: 'Route', relatedLeadId: 'kael', title: 'Ep 4. 해동', description: '저주 해제.', reqAffection: {leadId: 'kael', min: 80}, isUnlocked: false, isCompleted: false, cgPromptBase: "Kissing ritual, ice shattering", dialogueScripts: [{speaker:"카엘루스", text:"따뜻해..."}] },
    { id: 'kael_5', type: 'Route', relatedLeadId: 'kael', title: 'Ep 5. 맹세', description: '영원한 사랑.', reqAffection: {leadId: 'kael', min: 95}, isUnlocked: false, isCompleted: false, cgPromptBase: "Wedding in snow, happy ending", dialogueScripts: [{speaker:"카엘루스", text:"너만 사랑하겠어."}] },

    // --- RIAN ROUTE (5 Episodes) ---
    { id: 'rian_1', type: 'Route', relatedLeadId: 'rian', title: 'Ep 1. 비밀', description: '피 냄새.', reqAffection: {leadId: 'rian', min: 20}, isUnlocked: false, isCompleted: false, cgPromptBase: "Knight hiding sword", dialogueScripts: [{speaker:"리안", text:"아무것도 아닙니다."}] },
    { id: 'rian_2', type: 'Route', relatedLeadId: 'rian', title: 'Ep 2. 밀명', description: '황제의 명령.', reqItem: 'tool_old_letter', reqAffection: {leadId: 'rian', min: 40}, isUnlocked: false, isCompleted: false, cgPromptBase: "Reading burnt letter, shocked", dialogueScripts: [{speaker:"나", text:"나를 감시했어?"}] },
    { id: 'rian_3', type: 'Route', relatedLeadId: 'rian', title: 'Ep 3. 각성', description: '명령 거부.', reqAffection: {leadId: 'rian', min: 60}, isUnlocked: false, isCompleted: false, cgPromptBase: "Knight blocking attack for lady", dialogueScripts: [{speaker:"리안", text:"더 이상 개가 아닙니다."}] },
    { id: 'rian_4', type: 'Route', relatedLeadId: 'rian', title: 'Ep 4. 혈맹', description: '피의 맹세.', reqAffection: {leadId: 'rian', min: 80}, isUnlocked: false, isCompleted: false, cgPromptBase: "Cutting palms, holding hands", dialogueScripts: [{speaker:"나", text:"우린 운명 공동체야."}] },
    { id: 'rian_5', type: 'Route', relatedLeadId: 'rian', title: 'Ep 5. 연인', description: '기사에서 연인으로.', reqAffection: {leadId: 'rian', min: 95}, isUnlocked: false, isCompleted: false, cgPromptBase: "Knight taking off armor, embracing lady", dialogueScripts: [{speaker:"리안", text:"당신만을 안겠습니다."}] },

    // --- SION ROUTE (5 Episodes) ---
    { id: 'sion_1', type: 'Route', relatedLeadId: 'sion', title: 'Ep 1. 오류', description: '가짜 세상.', reqAffection: {leadId: 'sion', min: 20}, isUnlocked: false, isCompleted: false, cgPromptBase: "Mage looking at glitching sky", dialogueScripts: [{speaker:"시온", text:"해상도가 떨어지네."}] },
    { id: 'sion_2', type: 'Route', relatedLeadId: 'sion', title: 'Ep 2. 관찰', description: '감정 발생.', reqAffection: {leadId: 'sion', min: 40}, isUnlocked: false, isCompleted: false, cgPromptBase: "Mage analyzing lady's face", dialogueScripts: [{speaker:"시온", text:"왜 심박수가 오르지?"}] },
    { id: 'sion_3', type: 'Route', relatedLeadId: 'sion', title: 'Ep 3. 로그', description: '게임의 비밀.', reqItem: 'tool_glitch_shard', reqAffection: {leadId: 'sion', min: 60}, isUnlocked: false, isCompleted: false, cgPromptBase: "Holographic screens, code", dialogueScripts: [{speaker:"나", text:"우리가 게임 캐릭터라고?"}] },
    { id: 'sion_4', type: 'Route', relatedLeadId: 'sion', title: 'Ep 4. 붕괴', description: '세계를 부수다.', reqAffection: {leadId: 'sion', min: 80}, isUnlocked: false, isCompleted: false, cgPromptBase: "World crumbling, shield protecting lady", dialogueScripts: [{speaker:"시온", text:"서버를 터트려서라도 지킬게."}] },
    { id: 'sion_5', type: 'Route', relatedLeadId: 'sion', title: 'Ep 5. 현실', description: '새로운 시작.', reqAffection: {leadId: 'sion', min: 95}, isUnlocked: false, isCompleted: false, cgPromptBase: "Floating in stars, holding hands", dialogueScripts: [{speaker:"시온", text:"여기가 우리의 현실이야."}] }
];

const INITIAL_STATE: GameState = {
  name: "이름을 입력하세요",
  title: "백작가의 생존자",
  userAppearancePrompt: "Beautiful noble lady with determined eyes, silver hair, red jeweled necklace, luxurious rofan dress, anime style masterpiece",
  level: 1, xp: 0, maxXp: 100, hp: 100, maxHp: 100, gold: 500, skillPoints: 0, reputation: 0,
  corruption: 0, // Karma System
  currentDate: new Date().toISOString().split('T')[0], season: 'Spring', dayCount: 1, lastLoginDate: new Date().toISOString().split('T')[0],
  stats: { STR: 5, INT: 5, DEX: 5, CHR: 5, WIS: 5, LUK: 10 }, 
  quests: [], kingdom: [], maleLeads: INITIAL_MALE_LEADS, longTermGoal: "가주가 되어 나를 위협한 자들을 심판한다.", writingLogs: [],
  skills: INITIAL_SKILLS, inventory: [], calendar: [], storyChapters: STORY_CHAPTERS
};

// --- [OMNI-ARCHITECT] DEEP MERGE SYSTEM ---
const sanitizeState = (savedState: any): GameState => {
    if (!savedState) return INITIAL_STATE;
    const merged = { ...INITIAL_STATE, ...savedState };
    // Merge Leads (Preserve static data)
    merged.maleLeads = INITIAL_STATE.maleLeads.map(initLead => {
        const savedLead = savedState.maleLeads?.find((l: MaleLead) => l.id === initLead.id);
        if (savedLead) {
            return {
                ...initLead,
                affection: savedLead.affection,
                isVillain: savedLead.isVillain,
                imageUrl: savedLead.imageUrl || initLead.imageUrl,
                isImageLocked: savedLead.isImageLocked,
                secrets: initLead.secrets.map(initSecret => {
                    const savedSecret = savedLead.secrets?.find((s: Secret) => s.id === initSecret.id);
                    return savedSecret ? { ...initSecret, isDiscovered: savedSecret.isDiscovered } : initSecret;
                })
            };
        }
        return initLead;
    });
    // Merge Chapters (Preserve progress, update content)
    merged.storyChapters = INITIAL_STATE.storyChapters.map(initCh => {
        const savedCh = savedState.storyChapters?.find((c: StoryChapter) => c.id === initCh.id);
        if (savedCh) {
            return {
                ...initCh,
                isUnlocked: savedCh.isUnlocked,
                isCompleted: savedCh.isCompleted,
                cgUrl: savedCh.cgUrl || initCh.cgUrl
            };
        }
        return initCh;
    });
    // Safety
    merged.inventory = savedState.inventory || [];
    merged.quests = savedState.quests || [];
    merged.kingdom = savedState.kingdom || [];
    merged.writingLogs = savedState.writingLogs || [];
    merged.calendar = savedState.calendar || [];
    merged.skills = savedState.skills || INITIAL_STATE.skills;
    return merged;
};

export const App: React.FC = () => {
  const [state, setState] = useState<GameState>(() => {
    try {
      const saved = localStorage.getItem("grimoire_save_v20_countess");
      return saved ? sanitizeState(JSON.parse(saved)) : INITIAL_STATE;
    } catch { return INITIAL_STATE; }
  });

  const [activeTab, setActiveTab] = useState<TabId>('home');
  const [showSettings, setShowSettings] = useState(false);
  const [apiKeyLinked, setApiKeyLinked] = useState(false);
  const [lastSavedTime, setLastSavedTime] = useState<string>("");
  const [showEnding, setShowEnding] = useState(false);

  // Modals & Overlays
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showPortraitModal, setShowPortraitModal] = useState(false); 
  const [showMainStoryModal, setShowMainStoryModal] = useState(false);
  const [showShopModal, setShowShopModal] = useState(false);

  // Generation States
  const [genLoading, setGenLoading] = useState<string | null>(null);
  const [imageSize, setImageSize] = useState<'1K' | '2K' | '4K'>('2K');
  const [editPrompt, setEditPrompt] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [videoLoading, setVideoLoading] = useState(false);
  const [questGenLoading, setQuestGenLoading] = useState(false);
  
  // VN Logic
  const [activeChapter, setActiveChapter] = useState<StoryChapter | null>(null);
  const [currentScriptIndex, setCurrentScriptIndex] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { 
      localStorage.setItem("grimoire_save_v20_countess", JSON.stringify(state)); 
      setLastSavedTime(new Date().toLocaleTimeString());
      const finalCh = state.storyChapters.find(c => c.id === 'main_30');
      if (finalCh?.isCompleted && !localStorage.getItem("ending_seen")) {
          setShowEnding(true);
          localStorage.setItem("ending_seen", "true");
      }
  }, [state]);

  useEffect(() => {
      // @ts-ignore
      if (window.aistudio && window.aistudio.hasSelectedApiKey) {
          // @ts-ignore
          window.aistudio.hasSelectedApiKey().then(hasKey => setApiKeyLinked(hasKey));
      }
  }, []);

  useEffect(() => {
      let hasUpdates = false;
      const updatedLeads = state.maleLeads.map(lead => {
          const updatedSecrets = lead.secrets.map(secret => {
              if (!secret.isDiscovered && secret.reqItem && state.inventory.includes(secret.reqItem)) {
                  hasUpdates = true;
                  alert(`[진실 해금] ${lead.name}의 치명적인 비밀을 알아냈습니다!`);
                  return { ...secret, isDiscovered: true };
              }
              return secret;
          });
          return { ...lead, secrets: updatedSecrets };
      });
      if (hasUpdates) setState(prev => ({ ...prev, maleLeads: updatedLeads }));
  }, [state.inventory]);

  const handleLinkGoogle = async () => {
      try {
          // @ts-ignore
          if (window.aistudio && window.aistudio.openSelectKey) {
              // @ts-ignore
              await window.aistudio.openSelectKey();
              setApiKeyLinked(true);
              alert("Google 계정이 성공적으로 연동되었습니다! 이제 고화질 이미지 생성이 가능합니다.");
          } else { alert("이 환경에서는 자동 연동을 지원하지 않습니다."); }
      } catch (e) { alert("연동 중 오류가 발생했습니다."); }
  };

  const handleExport = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `grimoire_backup_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const fileReader = new FileReader();
    if (event.target.files && event.target.files[0]) {
      fileReader.readAsText(event.target.files[0], "UTF-8");
      fileReader.onload = (e) => {
        if(e.target?.result) {
            try {
                const parsed = JSON.parse(e.target.result as string);
                const sanitized = sanitizeState(parsed);
                setState(sanitized);
                alert("데이터가 성공적으로 복구되었습니다.");
                setShowSettings(false);
            } catch (err) { alert("파일 형식이 올바르지 않습니다."); }
        }
      };
    }
  };

  const handleGenImage = async (target: string) => {
      if ((target==='user' && state.isUserImageLocked) || (target==='bg' && state.isBgImageLocked)) return alert("이미지가 고정(Lock)되어 있습니다.");
      setGenLoading(target);
      let prompt = target === 'user' ? state.userAppearancePrompt : "Dark fantasy mansion hallway, candlelight, shadows, gothic architecture, webtoon style background";
      const url = target === 'bg' ? await generateBackground(prompt, imageSize) : await generateCharacterPortrait(prompt, imageSize); 
      if(url) {
          if (target === 'user') setState(p => ({...p, userImageUrl: url}));
          else if (target === 'bg') setState(p => ({...p, backgroundImageUrl: url}));
      }
      setGenLoading(null);
  }

  const handleEditImage = async (target: string) => {
      if (!editPrompt.trim()) return;
      let img = target === 'user' ? state.userImageUrl : state.backgroundImageUrl;
      if (!img) return;
      setGenLoading(target);
      const url = await editMagicalImage(img, editPrompt);
      if(url) {
          if (target === 'user') setState(p => ({...p, userImageUrl: url}));
          else if (target === 'bg') setState(p => ({...p, backgroundImageUrl: url}));
          setEditPrompt("");
      }
      setGenLoading(null);
  }

  const handleAnimate = async (target: string) => {
      let img = target === 'user' ? state.userImageUrl : state.backgroundImageUrl;
      if (!img) return;
      setVideoLoading(true);
      const url = await generateVideoFromImage(img);
      if(url) setVideoUrl(url);
      setVideoLoading(false);
  }

  const addQuest = async (text: string, isDaily: boolean = false) => {
    const analysis = await evaluateQuestDifficulty(text);
    const newQuest: Quest = { id: Date.now(), title: text, completed: false, reward: analysis.gold, xpReward: analysis.xp, isDaily, difficulty: analysis.tier, butlerComment: analysis.comment, type: isDaily ? 'Normal' : 'Social' };
    // @ts-ignore
    setState(prev => ({ ...prev, quests: [...prev.quests, newQuest] }));
  };

  const handleAutoSuggestQuests = async () => {
      setQuestGenLoading(true);
      const suggestions = await generateSideQuests(state);
      const dailySuggestions = suggestions.map(q => ({...q, isDaily: true, type: 'Normal' as const}));
      setState(prev => ({ ...prev, quests: [...prev.quests, ...dailySuggestions] }));
      setQuestGenLoading(false);
      alert("집사가 귀하를 위한 새로운 생존 루틴을 제안했습니다.");
  };

  const toggleQuest = (id: number) => {
      setState(prev => ({
          ...prev, 
          quests: prev.quests.map(q => q.id === id ? { ...q, completed: true } : q),
          gold: prev.quests.find(q=>q.id===id)?.isDaily ? prev.gold : prev.gold + (prev.quests.find(q=>q.id===id)?.reward || 0),
          xp: prev.xp + (prev.quests.find(q=>q.id===id)?.xpReward || 0)
      }));
  };

  const handlePlayChapter = async (id: string) => {
      const ch = state.storyChapters.find(c => c.id === id);
      if(ch) { 
          if (ch.reqItem && !state.inventory.includes(ch.reqItem)) {
              alert(`[진행 불가] 필요한 아이템이 없습니다: ${SHOP_ITEMS.find(i=>i.id===ch.reqItem)?.name}`);
              return;
          }
          if (ch.reqAffection) {
              const lead = state.maleLeads.find(l => l.id === ch.reqAffection!.leadId);
              if (!lead || lead.affection < ch.reqAffection.min) {
                  alert(`[진행 불가] ${lead?.name}의 호감도가 부족합니다.`);
                  return;
              }
          }
          if (!ch.cgUrl) {
              setGenLoading('chapter');
              const url = await generateBackground(ch.cgPromptBase, '2K'); 
              if (url) {
                  setState(prev => ({...prev, storyChapters: prev.storyChapters.map(c => c.id === id ? { ...c, cgUrl: url } : c)}));
                  setActiveChapter({...ch, cgUrl: url});
              } else { setActiveChapter(ch); }
              setGenLoading(null);
          } else { setActiveChapter(ch); }
          setCurrentScriptIndex(0); 
      }
  };
  
  const handleNextScript = () => {
    if (!activeChapter) return;
    if (currentScriptIndex < activeChapter.dialogueScripts.length - 1) {
        setCurrentScriptIndex(prev => prev + 1);
    } else {
        setState(prev => ({
            ...prev,
            storyChapters: prev.storyChapters.map(c => c.id === activeChapter.id ? { ...c, isCompleted: true } : c),
            xp: prev.xp + 1000, 
            gold: prev.gold + 500
        }));
        setActiveChapter(null);
    }
  };

  const handleChoice = (choice: Choice) => {
      if(choice.effect) setState(prev => ({...prev, ...choice.effect!(prev)}));
      if(choice.alertMsg) alert(choice.alertMsg);
      handleNextScript();
  }

  const handleSetName = (name: string) => {
    setState(prev => ({ ...prev, name }));
  };

  const renderPortraitControl = (type: 'user' | 'bg', imageUrl?: string, locked?: boolean, onLock?: () => void, onGen?: () => void) => (
    <div className="bg-white border border-[#c5a059]/30 rounded-lg p-4 shadow-sm relative overflow-hidden group">
        <div className="flex items-center gap-3 mb-3">
            <div className="w-14 h-14 rounded bg-gray-100 overflow-hidden border border-[#c5a059] relative shrink-0">
                {imageUrl ? <img src={imageUrl} className="w-full h-full object-cover"/> : <ImageIcon size={32} className="m-3 text-gray-400"/>}
                {locked && <div className="absolute inset-0 bg-black/30 flex items-center justify-center"><Lock size={12} className="text-white"/></div>}
            </div>
            <div className="flex-1 min-w-0">
                <div className="font-bold text-sm text-[#2c1e12] truncate">{type === 'user' ? '주인공 (Me)' : '배경 (Lobby)'}</div>
                <div className="flex gap-1 mt-1">
                     <button onClick={onLock} className={`p-1.5 rounded border ${locked ? 'bg-[#c5a059] text-white' : 'text-gray-400'}`}>{locked ? <Lock size={12}/> : <Unlock size={12}/>}</button>
                     <button onClick={onGen} disabled={genLoading===type || locked} className="bg-[#2c1e12] text-[#c5a059] px-2 py-1.5 rounded text-xs font-bold disabled:opacity-50 flex items-center gap-1">
                         {genLoading===type ? <Loader2 size={12} className="animate-spin"/> : <Sparkles size={12}/>} 생성
                     </button>
                </div>
            </div>
        </div>
        {imageUrl && (
           <div className="border-t border-dashed border-gray-200 pt-2 mt-2 space-y-2">
               <div className="flex gap-1">
                   <input type="text" placeholder="예: 흑발로 변경" value={editPrompt} onChange={e => setEditPrompt(e.target.value)} className="flex-1 text-[10px] p-1 border rounded bg-gray-50 focus:outline-[#c5a059]" disabled={locked}/>
                   <button onClick={() => handleEditImage(type)} disabled={locked || genLoading===type} className="bg-purple-100 text-purple-700 p-1 rounded hover:bg-purple-200 disabled:opacity-50"><Wand2 size={12}/></button>
               </div>
               <button onClick={() => handleAnimate(type)} className="w-full py-1 bg-gradient-to-r from-blue-500 to-indigo-600 text-white text-[10px] font-bold rounded flex items-center justify-center gap-1 hover:brightness-110"><Film size={12}/> 생동감 부여 (Veo)</button>
           </div>
        )}
    </div>
  );

  return (
    <div className="h-screen w-full flex flex-col overflow-hidden relative sm:border-x-2 sm:border-[#e2e8f0] max-w-md mx-auto shadow-2xl font-sans bg-[#fdfbf7]">
      <div onClick={() => setShowStatusModal(true)} className="cursor-pointer transition-transform active:scale-95 z-40 relative">
          <GameHeader state={state} setShowSettings={(e) => { e.stopPropagation(); setShowSettings(true); }} />
      </div>

      <main className="flex-1 relative overflow-hidden pt-[70px]">
          {activeTab === 'home' && (
              <div className="h-full flex flex-col relative pb-24 overflow-hidden">
                  <div className="absolute inset-0 z-0">
                       <img src={state.backgroundImageUrl || "https://images.unsplash.com/photo-1550503986-f8a47d2d3851?q=80&w=2072&auto=format&fit=crop"} className="w-full h-full object-cover" />
                       <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/60"></div>
                  </div>
                  <div className="absolute inset-0 z-0 flex items-end justify-center pointer-events-none">
                       {state.userImageUrl ? <img src={state.userImageUrl} className="h-[85%] object-contain drop-shadow-2xl" /> : null}
                  </div>
                  <div className="absolute top-1/2 -translate-y-1/2 right-4 z-20 flex flex-col gap-4 animate-fade-in">
                       <button onClick={() => setShowMainStoryModal(true)} className="w-14 h-14 bg-[#2c1e12]/90 border border-[#c5a059] rounded-xl shadow-xl flex flex-col items-center justify-center gap-1 hover:scale-105 transition-transform group backdrop-blur">
                           <Scroll className="text-[#c5a059] group-hover:text-white" size={20}/>
                           <span className="text-[8px] text-[#c5a059] font-cinzel text-center leading-tight">STORY</span>
                       </button>
                       <button onClick={() => setShowShopModal(true)} className="w-14 h-14 bg-[#1a1a1a]/90 border border-white/20 rounded-xl shadow-xl flex flex-col items-center justify-center gap-1 hover:scale-105 transition-transform group backdrop-blur">
                           <ShoppingBag className="text-white group-hover:text-[#c5a059]" size={20}/>
                           <span className="text-[8px] text-white font-cinzel">SHOP</span>
                       </button>
                       <button onClick={() => setShowPortraitModal(true)} className="w-14 h-14 bg-purple-900/80 border border-purple-400 rounded-xl text-purple-200 shadow-lg hover:bg-purple-800 flex flex-col items-center justify-center gap-1 hover:scale-105 transition-transform backdrop-blur">
                           <Palette size={20}/>
                           <span className="text-[8px] font-cinzel">ATELIER</span>
                       </button>
                  </div>
              </div>
          )}
          
          {activeTab === 'love' && (
             <Romance leads={state.maleLeads} inventory={state.inventory} shopItems={SHOP_ITEMS} chapters={state.storyChapters} onGift={(lid, iid) => { setState(prev => ({...prev, inventory: prev.inventory.filter(i=>i!==iid), maleLeads: prev.maleLeads.map(l=>l.id===lid ? {...l, affection: l.affection+20} : l)})); alert("선물 전달 완료 (호감도 상승)"); }} onGeneratePortrait={async(lid, size) => { const l = state.maleLeads.find(x=>x.id===lid); if(l) { if(l.isImageLocked) return alert("이미지가 잠겨있습니다."); const url = await generateCharacterPortrait(l.appearancePrompt, size); if(url) setState(prev => ({...prev, maleLeads: prev.maleLeads.map(x=>x.id===lid ? {...x, imageUrl: url} : x)})); } }} season={state.season} onLockPortrait={(id) => setState(prev => ({...prev, maleLeads: prev.maleLeads.map(l=>l.id===id ? {...l, isImageLocked: !l.isImageLocked} : l)}))} onPlayChapter={handlePlayChapter} onChoiceMade={handleChoice} />
          )}

          {activeTab === 'writing' && (
             <div className="h-full p-4 pb-24 overflow-y-auto custom-scroll">
                <Grimoire writingLogs={state.writingLogs} onAddLog={(count) => setState(p => ({...p, writingLogs: [...p.writingLogs, {date: new Date().toISOString().split('T')[0], wordCount: count}]}))} skills={state.skills} skillPoints={state.skillPoints} onUnlockSkill={() => {}} />
             </div>
          )}

          {activeTab === 'ledger' && (
              <div className="h-full overflow-y-auto custom-scroll">
                  <KingdomManager expenses={state.kingdom} addExpense={(a,c,m) => setState(prev => ({...prev, gold: prev.gold - (c==='Income'? -parseInt(a) : parseInt(a)), kingdom: [{id:Date.now(), amount:parseInt(a), category:c as any, memo:m, date:new Date().toISOString()}, ...prev.kingdom]}))} gold={state.gold} onClaimWeeklyReward={() => {}} />
              </div>
          )}

          {activeTab === 'diary' && (
              <div className="h-full p-4 pb-24 overflow-y-auto custom-scroll flex flex-col gap-6">
                  <div className="bg-[#1a1a1a] p-4 rounded-xl border-l-4 border-[#c5a059] shadow-lg">
                      <h4 className="text-[#c5a059] text-xs font-bold mb-1 font-cinzel flex items-center gap-2"><ScrollText size={14}/> 1-YEAR OATH (생존 목표)</h4>
                      {state.longTermGoal ? <p className="text-white font-serif text-lg">"{state.longTermGoal}"</p> : <input type="text" placeholder="1년 뒤 살아남기 위해 무엇을 하시겠습니까?" className="w-full bg-transparent text-white font-serif border-b border-gray-600 focus:border-[#c5a059] outline-none placeholder-gray-500" onBlur={(e) => setState({...state, longTermGoal: e.target.value})} />}
                  </div>
                  <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200">
                      <h4 className="text-[#2c1e12] font-bold text-xs mb-3 flex items-center gap-2"><BarChart2 size={14}/> WEEKLY PERFORMANCE</h4>
                      <div className="h-32">
                         <ResponsiveContainer width="100%" height="100%">
                             <BarChart data={state.writingLogs.slice(-7).map(l => ({date: l.date.slice(5), count: l.wordCount}))}>
                                 <XAxis dataKey="date" stroke="#9ca3af" fontSize={10} tickLine={false} axisLine={false} />
                                 <Tooltip />
                                 <Bar dataKey="count" fill="#c5a059" radius={[4, 4, 0, 0]} />
                             </BarChart>
                         </ResponsiveContainer>
                      </div>
                  </div>
                  <CalendarView calendar={state.calendar} quests={state.quests}/>
                  <div className="flex-1">
                      <h4 className="font-bold text-[#c5a059] mb-2 font-cinzel text-lg flex items-center gap-2">DAILY RITUALS <button onClick={handleAutoSuggestQuests} disabled={questGenLoading} className="text-[10px] bg-[#2c1e12] text-[#f4e4bc] px-2 py-1 rounded-full border border-[#c5a059] flex items-center gap-1 hover:bg-[#c5a059] hover:text-[#2c1e12] transition-colors">{questGenLoading ? <Loader2 size={10} className="animate-spin"/> : <Sparkles size={10}/>} 집사의 제안</button></h4>
                      <QuestBoard quests={state.quests.filter(q => q.isDaily)} addQuest={async (t) => addQuest(t, true)} toggleQuest={toggleQuest} deleteQuest={(id) => setState(prev => ({...prev, quests: prev.quests.filter(q=>q.id!==id)}))} />
                  </div>
              </div>
          )}
      </main>

      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      {showEnding && (
          <div className="absolute inset-0 z-[100] bg-black flex flex-col items-center justify-center p-6 animate-fade-in text-center">
              <div className="max-w-md w-full border-4 border-[#c5a059] p-8 bg-[#1a1212] relative shadow-[0_0_50px_rgba(197,160,89,0.5)]">
                  <Trophy size={64} className="text-[#ffd700] mx-auto mb-4 animate-bounce" />
                  <h1 className="text-3xl font-cinzel font-bold text-[#c5a059] mb-2 tracking-widest">VICTORY</h1>
                  <p className="text-white font-serif text-lg mb-6 leading-relaxed">"축하합니다, 가주님.<br/>당신의 지혜와 용기로 가문을 구해냈습니다."</p>
                  <div className="bg-black/50 p-4 rounded mb-6 border border-[#c5a059]/30">
                      <div className="text-[#c5a059] text-xs font-bold mb-2">FINAL STATISTICS</div>
                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-300"><div>LV: {state.level}</div><div>GOLD: {state.gold}</div><div>KARMA: {state.corruption}</div><div>LOVERS: {state.maleLeads.filter(l => l.affection > 80).length}명</div></div>
                  </div>
                  <button onClick={() => { setShowEnding(false); localStorage.removeItem("grimoire_save_v20_countess"); window.location.reload(); }} className="w-full py-4 bg-[#c5a059] text-[#1a1212] font-bold font-cinzel text-lg rounded hover:bg-white transition-colors">NEW GAME+ (Return)</button>
              </div>
          </div>
      )}
      {showMainStoryModal && (
          <div className="absolute inset-0 z-50 bg-black/90 flex p-6 animate-fade-in">
              <div className="w-full h-full border border-[#c5a059] rounded-lg p-4 flex flex-col relative bg-[#1a1a1a]">
                  <button onClick={() => setShowMainStoryModal(false)} className="absolute top-4 right-4 text-white"><X/></button>
                  <h2 className="text-2xl font-cinzel font-bold text-[#c5a059] mb-4 text-center">GRIMOIRE OF FATE</h2>
                  <div className="flex-1 overflow-y-auto custom-scroll space-y-4">
                      {state.storyChapters.filter(c => c.type === 'Main').map((ch, idx) => (
                          <div key={ch.id} className={`p-4 rounded border relative overflow-hidden ${ch.isUnlocked ? 'bg-[#2c1e12] border-[#c5a059]/30' : 'bg-black/50 border-gray-800 opacity-60'}`}>
                              <div className="text-[#c5a059] text-xs font-bold mb-1">CHAPTER {idx+1}</div>
                              <h3 className="text-white font-bold">{ch.title}</h3>
                              <p className="text-gray-400 text-sm mt-1 mb-3">{ch.description}</p>
                              {ch.reqItem && !ch.isCompleted && <div className="text-[10px] bg-red-900/30 text-red-400 p-1 mb-2 inline-block rounded border border-red-900">필요: {SHOP_ITEMS.find(i=>i.id===ch.reqItem)?.name || "Unknown Item"}</div>}
                              {ch.isUnlocked && !ch.isCompleted && <button onClick={() => handlePlayChapter(ch.id)} className="w-full py-2 bg-[#c5a059] text-black font-bold rounded text-xs flex items-center justify-center gap-2">{genLoading === 'chapter' ? <Loader2 size={12} className="animate-spin"/> : <Sparkles size={12}/>} 운명 시작하기</button>}
                              {ch.isCompleted && <div className="text-green-500 font-bold text-xs text-center border-t border-white/10 pt-2 mt-2">COMPLETED</div>}
                              {!ch.isUnlocked && <div className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-[1px]"><Lock className="text-gray-500"/></div>}
                          </div>
                      ))}
                  </div>
              </div>
          </div>
      )}
      {showShopModal && (
          <div className="absolute inset-0 z-50 bg-black/80 flex items-center justify-center p-4">
              <div className="w-full max-w-sm h-[80%] bg-[#fdfbf7] rounded-xl overflow-hidden relative shadow-2xl border-4 border-[#c5a059]">
                  <button onClick={() => setShowShopModal(false)} className="absolute top-2 right-2 text-[#2c1e12] z-10 hover:text-red-500"><X/></button>
                  <Shop gold={state.gold} items={SHOP_ITEMS} inventory={state.inventory} buyItem={(i) => { if(state.gold>=i.price){ setState({...state, gold: state.gold-i.price, inventory:[...state.inventory, i.id]}); } else alert("골드가 부족합니다."); }} />
              </div>
          </div>
      )}
      {showPortraitModal && (
          <div className="absolute inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fade-in">
              <div className="panel-game w-full max-w-sm p-4 relative bg-[#fdfbf7] max-h-[90%] overflow-y-auto custom-scroll">
                  <button onClick={() => setShowPortraitModal(false)} className="absolute top-4 right-4 text-gray-400 hover:text-red-500"><X/></button>
                  <h3 className="text-xl font-cinzel font-bold text-[#c5a059] mb-1 flex items-center gap-2"><Palette size={20}/> Atelier</h3>
                  <div className="flex gap-2 mb-4 bg-gray-100 p-1 rounded-lg">{(['1K', '2K', '4K'] as const).map(s => (<button key={s} onClick={() => setImageSize(s)} className={`flex-1 py-1 text-xs font-bold rounded ${imageSize === s ? 'bg-white text-[#c5a059] shadow-sm' : 'text-gray-400'}`}>{s}</button>))}</div>
                  <div className="space-y-4">
                      {renderPortraitControl('user', state.userImageUrl, state.isUserImageLocked, () => setState(p => ({...p, isUserImageLocked: !p.isUserImageLocked})), () => handleGenImage('user'))}
                      {renderPortraitControl('bg', state.backgroundImageUrl, state.isBgImageLocked, () => setState(p => ({...p, isBgImageLocked: !p.isBgImageLocked})), () => handleGenImage('bg'))}
                  </div>
              </div>
          </div>
      )}
      {showStatusModal && (
        <div className="absolute inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in">
            <div className="w-full max-w-sm relative">
                <button onClick={() => setShowStatusModal(false)} className="absolute -top-10 right-0 text-white"><X/></button>
                <StatusCard state={state} onAskOracle={async () => { const advice = await getOracleAdvice(state); alert(`[AKASHIC RECORD]\n\n"${advice}"`); }} isOracleLoading={false} onSetName={handleSetName} />
            </div>
        </div>
      )}
      {showSettings && (
          <div className="absolute inset-0 bg-black/80 z-[60] flex items-center justify-center p-6 backdrop-blur animate-fade-in">
              <div className="panel-game p-6 w-full max-w-sm bg-white border-[#c5a059] flex flex-col gap-4">
                  <div className="flex justify-between items-center mb-2"><h2 className="text-xl font-bold font-cinzel text-[#c5a059] flex items-center gap-2"><Settings size={20}/> SETTINGS</h2><button onClick={()=>setShowSettings(false)} className="text-gray-400 hover:text-[#c5a059]"><X/></button></div>
                  <button onClick={handleLinkGoogle} className={`w-full py-3 border-2 font-bold rounded-lg flex items-center justify-center gap-2 shadow-sm transition-all ${apiKeyLinked ? 'bg-green-50 border-green-500 text-green-700' : 'bg-blue-50 border-blue-200 text-blue-600 hover:bg-blue-100'}`}>{apiKeyLinked ? <Check size={18}/> : <LogIn size={18}/>}{apiKeyLinked ? "Google 연동됨" : "Gemini API 연동"}</button>
                  <div className="h-px bg-gray-200 my-1"></div>
                  <div className="flex items-center justify-between text-xs bg-gray-100 p-3 rounded text-gray-500"><span className="flex items-center gap-1"><Save size={12}/> Auto-Save Active</span><span className="font-bold text-[#c5a059]">{lastSavedTime} 저장됨</span></div>
                  <h3 className="text-xs font-bold text-gray-500 mt-2 flex items-center gap-1"><FileJson size={12}/> DATA BACKUP</h3>
                  <div className="flex gap-2"><button onClick={handleExport} className="flex-1 py-3 bg-[#2c1e12] text-[#f4e4bc] border border-[#c5a059] rounded-lg font-bold text-xs flex flex-col items-center justify-center gap-1 hover:brightness-110"><Download size={16}/> 내보내기</button><label className="flex-1 py-3 bg-white text-[#2c1e12] border border-gray-300 rounded-lg font-bold text-xs flex flex-col items-center justify-center gap-1 hover:bg-gray-50 cursor-pointer"><Upload size={16}/> 가져오기<input type="file" accept=".json" onChange={handleImport} ref={fileInputRef} className="hidden"/></label></div>
                  <div className="h-px bg-gray-200 my-2"></div>
                  <button onClick={() => { localStorage.removeItem("grimoire_save_v20_countess"); window.location.reload(); }} className="w-full py-3 bg-red-50 text-red-500 border border-red-200 font-bold rounded-lg flex items-center justify-center gap-2 hover:bg-red-100 shadow-sm text-xs"><RefreshCcw size={14}/> 초기화 (RESET ALL DATA)</button>
              </div>
          </div>
      )}
      {activeChapter && (
        <div className="absolute inset-0 bg-black z-50 flex flex-col animate-fade-in">
            <div className="flex-1 bg-gray-900 relative">
                {activeChapter.cgUrl ? <img src={activeChapter.cgUrl} className="w-full h-full object-cover animate-fade-in" /> : <div className="w-full h-full flex flex-col items-center justify-center text-gray-500 gap-4"><Loader2 className="animate-spin" size={40}/><p className="text-xs font-serif">운명의 장면을 그리는 중...</p></div>}
                <div className="absolute bottom-0 left-0 right-0 h-1/2 bg-gradient-to-t from-black via-black/50 to-transparent"></div>
            </div>
            <div className="h-[35%] bg-[#fdfbf7] border-t-4 border-[#c5a059] p-6 flex flex-col justify-center shadow-[0_-10px_40px_rgba(0,0,0,0.5)] relative">
                <div className="absolute -top-5 left-6 bg-[#2c1e12] text-[#c5a059] border border-[#c5a059] px-6 py-2 font-bold font-cinzel text-sm shadow-lg tracking-widest">{activeChapter.dialogueScripts[currentScriptIndex].speaker}</div>
                <div className="text-[#2d3748] text-lg font-serif leading-relaxed animate-slide-up">"{activeChapter.dialogueScripts[currentScriptIndex].text}"</div>
                <div className="mt-6 space-y-2">
                    {activeChapter.dialogueScripts[currentScriptIndex].choices ? (
                        activeChapter.dialogueScripts[currentScriptIndex].choices!.map((c, i) => (
                            <button key={i} onClick={() => handleChoice(c)} className="w-full py-3 border-2 border-[#c5a059] text-[#2c1e12] font-bold rounded-lg hover:bg-[#c5a059] hover:text-white transition-all shadow-sm active:scale-95 text-left px-4">{c.text}</button>
                        ))
                    ) : (
                        <button onClick={handleNextScript} className="w-full py-3 bg-[#e2e8f0] text-gray-600 font-bold rounded-lg hover:bg-[#cbd5e0] flex items-center justify-center gap-2"><span className="animate-pulse">▼</span> 다음 (Next)</button>
                    )}
                </div>
            </div>
        </div>
      )}
    </div>
  );
};
