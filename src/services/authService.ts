// --- Local email accounts ---
// Accounts live only in this browser's localStorage: no server, no sync between devices.
// Passwords are never stored; only a salted PBKDF2 hash is kept.

const USERS_KEY = "grimoire_users";
const SESSION_KEY = "grimoire_session";
const LEGACY_SAVE_KEY = "grimoire_save_v20_countess";

interface StoredUser { salt: string; hash: string; }

const readUsers = (): Record<string, StoredUser> => {
    try { return JSON.parse(localStorage.getItem(USERS_KEY) || "{}"); } catch { return {}; }
};

const writeUsers = (users: Record<string, StoredUser>) => {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
};

const toHex = (buf: ArrayBuffer | Uint8Array) =>
    Array.from(buf instanceof Uint8Array ? buf : new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");

const fromHex = (hex: string) => new Uint8Array((hex.match(/../g) || []).map(h => parseInt(h, 16)));

const hashPassword = async (password: string, salt: Uint8Array): Promise<string> => {
    if (!window.crypto?.subtle) throw new Error("이 브라우저 환경에서는 로그인을 사용할 수 없습니다. (https 필요)");
    const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]);
    const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", salt, iterations: 100000, hash: "SHA-256" }, key, 256);
    return toHex(bits);
};

export const normalizeEmail = (email: string) => email.trim().toLowerCase();

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const MIN_PASSWORD_LENGTH = 6;

export const signUp = async (rawEmail: string, password: string): Promise<string> => {
    const email = normalizeEmail(rawEmail);
    if (!EMAIL_PATTERN.test(email)) throw new Error("올바른 이메일 주소를 입력하세요.");
    if (password.length < MIN_PASSWORD_LENGTH) throw new Error(`비밀번호는 ${MIN_PASSWORD_LENGTH}자 이상이어야 합니다.`);
    const users = readUsers();
    if (users[email]) throw new Error("이미 가입된 이메일입니다. 로그인해 주세요.");
    const salt = crypto.getRandomValues(new Uint8Array(16));
    users[email] = { salt: toHex(salt), hash: await hashPassword(password, salt) };
    writeUsers(users);
    claimLegacySave(email);
    localStorage.setItem(SESSION_KEY, email);
    return email;
};

export const logIn = async (rawEmail: string, password: string): Promise<string> => {
    const email = normalizeEmail(rawEmail);
    const user = readUsers()[email];
    if (!user || (await hashPassword(password, fromHex(user.salt))) !== user.hash) {
        throw new Error("이메일 또는 비밀번호가 올바르지 않습니다.");
    }
    localStorage.setItem(SESSION_KEY, email);
    return email;
};

export const logOut = () => localStorage.removeItem(SESSION_KEY);

export const getSessionEmail = (): string | null => {
    try {
        const email = localStorage.getItem(SESSION_KEY);
        return email && readUsers()[email] ? email : null;
    } catch { return null; }
};

// Each account keeps its own save slot.
export const getSaveKey = (email: string) => `${LEGACY_SAVE_KEY}:${email}`;
export const getEndingKey = (email: string) => `ending_seen:${email}`;

// The first account created hands over any progress saved before login existed.
const claimLegacySave = (email: string) => {
    const legacy = localStorage.getItem(LEGACY_SAVE_KEY);
    if (legacy && !localStorage.getItem(getSaveKey(email))) {
        localStorage.setItem(getSaveKey(email), legacy);
        localStorage.removeItem(LEGACY_SAVE_KEY);
        if (localStorage.getItem("ending_seen")) {
            localStorage.setItem(getEndingKey(email), "true");
            localStorage.removeItem("ending_seen");
        }
    }
};
