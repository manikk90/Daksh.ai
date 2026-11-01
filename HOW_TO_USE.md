# Use karne ka tareeka

## Files samajhne ke liye
1. `AGENT_SKILL_MAP.md` se agent ownership aur mappings dekho.
2. `agents/` mein readable operational documentation padho. Har file ke end mein mapped-skills addon hai.
3. `SKILL_CATALOG.md` se exact reference, role, script ya template tak jao.
4. `overlays/LATEST_USER_OVERRIDES_2026-11-01.md` ko relevant agent ke saath load karo; copied originals ko silently overwrite mat karo.

## Source files reuse karne ke liye
`skills/<name>/` mein actual original directory structure hai. Entrypoint `SKILL.md` hai; referenced files same directory tree mein rakho. Ek task ke liye relevant files hi load karo, poora archive context mein paste karna zaroori nahi.

`skill_packages/<name>/skill.zip` mein usi ek skill ka source bundle hai. Outer ZIP multiple skills aur documentation ka export hai, single-skill installer nahi. Target host ki import process aur permissions alag se apply hongi. Export banne se koi installation, account connection ya automation activate nahi hoti.

## Original backup aur verification
`original_dossier/` purane ZIP ke har file ko unchanged preserve karta hai. `mapping/source_files.json` mein original source hashes hain. `verification/FILE_HASHES.json` export files ke hashes deta hai, aur `verification/verify_export.py` unhe recheck karta hai.

```bash
python verification/verify_export.py .
```

`verification/QA_REPORT.md` mein executed checks aur limitations dono diye hain. External provider entrypoint snapshots ko fully self-contained plugin installers mat samajhna. AI Writer ki original source gap `missing/AI_WRITER_SOURCE_STATUS.md` mein marked hai.
