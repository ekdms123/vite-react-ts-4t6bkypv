// Reads a picked image file and shrinks it to a JPEG data URL small enough
// to keep in the localStorage save slot (which is capped at a few MB).
export const readImageFile = (file: File, maxSize = 1024): Promise<string> =>
    new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onerror = () => reject(new Error("이미지를 읽을 수 없습니다."));
        reader.onload = () => {
            const img = new Image();
            img.onerror = () => reject(new Error("이미지 파일이 아닙니다."));
            img.onload = () => {
                const scale = Math.min(1, maxSize / Math.max(img.width, img.height));
                const canvas = document.createElement("canvas");
                canvas.width = Math.round(img.width * scale);
                canvas.height = Math.round(img.height * scale);
                canvas.getContext("2d")!.drawImage(img, 0, 0, canvas.width, canvas.height);
                resolve(canvas.toDataURL("image/jpeg", 0.85));
            };
            img.src = reader.result as string;
        };
        reader.readAsDataURL(file);
    });

// Opens the system file picker and resolves with the resized image (or null if cancelled).
export const pickImage = (): Promise<string | null> =>
    new Promise(resolve => {
        const input = document.createElement("input");
        input.type = "file";
        input.accept = "image/*";
        input.onchange = async () => {
            const file = input.files?.[0];
            if (!file) return resolve(null);
            try { resolve(await readImageFile(file)); }
            catch (e) { alert((e as Error).message); resolve(null); }
        };
        input.click();
    });
