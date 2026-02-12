# Anima Avatar Asset Production Plan 🎨

## 1. Design Philosophy
- **Consistency**: All sprites must be derived from `shutiao_base.png` (or the original `shutiao_full.png` fusion) to ensure the character look remains 100% consistent.
- **Variety**: Each emotion should have at least 2-3 distinct variants (hand gestures, eye states).
- **Quality**: 16:9 Aspect Ratio, 2K Resolution, high detail.

## 2. Production Matrix

| ID | Emotion | Variant | Description | Base Image (Input) | Inpainting Prompt (Key Changes) | Status | Filename |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **001** | **Base** | `v1` | Standard/Listening | `shutiao_full.png` + BG | `gentle smile, looking at viewer, hands clasped` | ✅ Done | `shutiao_base.png` |
| **002** | **Happy** | `v1` | Big Smile | `shutiao_base.png` | `big happy smile, eyes closed in joy` | ✅ Done | `shutiao_happy.png` |
| **003** | **Happy** | `v2` | Peace Sign ✌️ | `shutiao_base.png` | `happy smile, winking, making peace sign hand gesture near face` | ⏳ Todo | `shutiao_happy_v2.png` |
| **004** | **Happy** | `v3` | Giggling 🤭 | `shutiao_base.png` | `shy smile, hand covering mouth, giggling` | ⏳ Todo | `shutiao_happy_v3.png` |
| **005** | **Angry** | `v1` | Pouting | `shutiao_base.png` | `angry face, pouting lips, eyebrows furrowed` | ✅ Done | `shutiao_angry.png` |
| **006** | **Angry** | `v2` | Crossed Arms 💢 | `shutiao_base.png` | `angry expression, arms crossed on chest, looking away` | ⏳ Todo | `shutiao_angry_v2.png` |
| **007** | **Angry** | `v3` | Scolding ☝️ | `shutiao_base.png` | `stern face, pointing finger at viewer, scolding` | ⏳ Todo | `shutiao_angry_v3.png` |
| **008** | **Shy** | `v1` | Blushing | `shutiao_base.png` | `shy face, heavy blush, looking down` | ✅ Done | `shutiao_shy.png` |
| **009** | **Shy** | `v2` | Hiding 🙈 | `shutiao_base.png` | `very shy, hands covering face/eyes, peeking through fingers` | ⏳ Todo | `shutiao_shy_v2.png` |
| **010** | **Think** | `v1` | Pensive | `shutiao_base.png` | `thinking face, looking up/sideways, hand on chin` | ✅ Done | `shutiao_think.png` |
| **011** | **Think** | `v2` | Idea 💡 | `shutiao_base.png` | `surprised expression, mouth open, realization, index finger up` | ⏳ Todo | `shutiao_think_v2.png` |

## 3. Execution Log
- [x] Base Generation (Dual Image Fusion)
- [x] Batch 1 (Happy v1, Angry v1, Shy v1, Think v1)
- [ ] Batch 2 (Hand Gestures: Happy v2, Angry v2, Think v2)
- [ ] Batch 3 (Complex Actions: Happy v3, Angry v3, Shy v2)

## 4. Technical Config
- **Model**: Gemini 3 Pro Image (Nano Banana Pro)
- **Resolution**: 2K (or 1K for stability if 500 errors occur)
- **Denoising Strength**: Low (0.3-0.4) for expressions, Medium (0.5-0.6) for hand gestures.
