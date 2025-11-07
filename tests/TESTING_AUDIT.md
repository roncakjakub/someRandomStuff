# AUDIT EXISTUJÚCICH TESTOV

**Dátum:** 7. november 2025

---

## EXISTUJÚCE TEST SÚBORY

### 1. Root Level Tests

#### `test_replicate.py`
- Test pre Replicate API (Flux models)

#### `test_tools.py`
- Základné testy pre tools

#### `test_wan_tool.py`
- Špecifický test pre Wan tool

---

### 2. Test Scripts Directory (`test_scripts/`)

#### `test_luma_video.py`
- Test pre Luma video generation

#### `test_minimax_video.py`
- Test pre Minimax video generation

#### `test_pika_video.py`
- Test pre Pika video generation

#### `test_pikamorph.py`
- Test pre Pika morph functionality

#### `test_runway_video.py`
- Test pre Runway video generation

#### `test_wan_video.py`
- Test pre Wan video generation

---

### 3. Tests Directory (`tests/`)

#### `tests/test_image_tools.py`
- Testy pre image generation tools (náš nový)

#### `tests/test_tools.py`
- Duplicate? Skontrolovať obsah

#### `tests/test_video_tools.py`
- Komplexné testy pre všetky video tools
- Obsahuje:
  - `test_runway()` - Runway Gen-4 Turbo
  - `test_pika()` - Pika v2.2 (single + morph)
  - `test_minimax()` - Minimax Hailuo 2.3
  - `test_luma()` - Luma Ray
  - `test_wan()` - Wan 2.5 i2v
  - `create_test_image()` - Helper na vytvorenie test obrázka

---

## ČO UŽ MÁME

### Video Tools - ✅ HOTOVÉ
- ✅ Runway test
- ✅ Pika test (single + morph)
- ✅ Minimax test
- ✅ Luma test
- ✅ Wan test

### Image Tools - ⚠️ ČIASTOČNE
- ⚠️ Flux Dev (v `test_replicate.py`)
- ❌ InstantCharacter
- ❌ Flux Kontext Pro
- ❌ Midjourney
- ❌ Ideogram
- ❌ Seedream4

---

## ČO CHÝBA

### 1. Image Tools Tests
- [ ] InstantCharacter (s reference image)
- [ ] Flux Kontext Pro (s reference image)
- [ ] Midjourney (APIFRAME)
- [ ] Ideogram (text in images)
- [ ] Seedream4

### 2. Agent Tests
- [ ] Creative Strategist
- [ ] Visual Production Agent
- [ ] Assembly Agent
- [ ] Voiceover Agent
- [ ] Research Agent (ak sa používa)

### 3. Workflow Tests
- [ ] Workflow orchestrator
- [ ] Workflow router
- [ ] End-to-end test (1 scéna)
- [ ] End-to-end test (multi-scéna)

### 4. Integration Tests
- [ ] Image → Video pipeline
- [ ] Video → Assembly pipeline
- [ ] Full workflow (bez hlasu)
- [ ] Full workflow (s hlasom)

---

## ODPORÚČANÝ TESTOVACÍ PLÁN

### Fáza 1: Dokončiť Image Tools Tests (2-3 hodiny)
1. Použiť existujúci `tests/test_video_tools.py` ako vzor
2. Vytvoriť komplexný `tests/test_image_tools_complete.py`
3. Otestovať všetky image tools systematicky

### Fáza 2: Vytvoriť Agent Tests (4-6 hodín)
1. `tests/test_agents.py` - všetky agenty
2. Mock vstupy pre každý agent
3. Overiť výstupy

### Fáza 3: Workflow Tests (6-8 hodín)
1. `tests/test_workflow_simple.py` - 1 scéna, bez hlasu
2. `tests/test_workflow_multi.py` - viac scén, bez hlasu
3. `tests/test_workflow_full.py` - s hlasom

### Fáza 4: Integration Tests (8-10 hodín)
1. End-to-end testy
2. Performance testy
3. Cost tracking

---

## POUŽITIE EXISTUJÚCICH TESTOV

### Spustiť video tools tests:
```bash
cd /home/ubuntu/social_video_agent_fixed

# Test jednotlivých tools
python tests/test_video_tools.py --tool minimax
python tests/test_video_tools.py --tool luma
python tests/test_video_tools.py --tool wan

# Test všetkých
python tests/test_video_tools.py --all
```

### Spustiť špecifické testy:
```bash
python test_scripts/test_minimax_video.py
python test_scripts/test_luma_video.py
python test_scripts/test_wan_video.py
```

---

## ODPORÚČANIE

**Použiť existujúce testy ako základ:**

1. ✅ `tests/test_video_tools.py` je veľmi dobrý - použiť ako vzor
2. ✅ Obsahuje helper funkcie (create_test_image)
3. ✅ Má dobrú štruktúru a error handling

**Vytvoriť podobné pre:**
- Image tools (dokončiť)
- Agents (nové)
- Workflow (nové)

**Neprepisovať existujúce testy, ale rozšíriť ich!**

---

## NAJBLIŽŠIE KROKY

1. **Spustiť existujúce video tools tests** (overíme že fungujú)
   ```bash
   python tests/test_video_tools.py --tool minimax --output-dir tests/outputs
   ```

2. **Dokončiť image tools tests** (použiť rovnakú štruktúru)

3. **Vytvoriť agent tests**

4. **Vytvoriť workflow tests** (1 scéna → multi-scéna → s hlasom)

---

**Záver:** Máme dobrý základ pre video tools, potrebujeme dokončiť image tools a pridať agent/workflow testy.
