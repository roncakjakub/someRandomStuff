# SYSTEMATICKÝ TESTOVACÍ PLÁN

**Dátum:** 7. november 2025  
**Cieľ:** Otestovať všetky komponenty projektu od základov

---

## PREHĽAD KOMPONENTOV

### 1. TOOLS (21 súborov)

#### Image Generation (8 tools):
- [ ] `apiframe_midjourney.py` - Midjourney via APIFRAME
- [ ] `instant_character.py` - Character consistency (fal.ai)
- [ ] `flux_kontext_pro.py` - Environment consistency (fal.ai)
- [ ] `replicate_image.py` - Flux Dev, Schnell, Pro (Replicate)
- [ ] `seedream4.py` - Character alternative (fal.ai)
- [ ] `ideogram_text.py` - Text in images (Ideogram)
- [ ] `gemini_nanobanana.py` - Gemini (experimental)

#### Video Generation (7 tools):
- [ ] `veo31_flf2v.py` - Veo 3.1 morphs (fal.ai)
- [ ] `wan_flf2v.py` - Wan morphs (fal.ai)
- [ ] `wan_video.py` - Wan animations (fal.ai)
- [ ] `pika_video.py` - Pika effects (fal.ai)
- [ ] `luma_video.py` - Luma animations (Luma AI)
- [ ] `minimax_video.py` - Minimax animations (Minimax)
- [ ] `runway_video.py` - Runway Gen-3 (Runway)

#### Voice & Utility (3 tools):
- [ ] `elevenlabs_voice.py` - Voiceover (ElevenLabs)
- [ ] `tavily_search.py` - Web search (Tavily)
- [ ] `video_assembly.py` - FFmpeg assembly

---

### 2. AGENTS (6 súborov)

- [ ] `creative_strategist.py` - Generuje scenár a scény
- [ ] `visual_production_agent.py` - Generuje obrázky a videá
- [ ] `assembly_agent.py` - Skladá finálne video
- [ ] `voiceover_agent.py` - Generuje voiceover
- [ ] `research_agent.py` - Research (ak sa používa)
- [ ] `concept_director.py` - Concept direction (ak sa používa)

---

### 3. WORKFLOW (3 súbory)

- [ ] `workflow.py` - Hlavný orchestrator
- [ ] `workflow_router.py` - AI Router (GPT-powered)
- [ ] `workflow_router_v2.py` - AI Router v2 (per-scene)

---

### 4. CONFIG & UTILS (5 súborov)

- [ ] `config/settings.py` - Nastavenia
- [ ] `config/brand_loader.py` - Brand loading
- [ ] `config/style_loader.py` - Style loading
- [ ] `utils/scene_detection.py` - Scene detection
- [ ] `main.py` - Entry point

---

## TESTOVACIA STRATÉGIA

### Fáza 1: TOOLS (individuálne testy)

**Prístup:**
1. Každý tool otestovať samostatne
2. Pripraviť test vstupy (prompty, obrázky)
3. Spustiť tool s test vstupom
4. Zaznamenať výstup (success/fail, čas, náklady)
5. Uložiť výsledky

**Test formát:**
```python
def test_tool_name():
    tool = ToolName()
    result = tool.execute(test_input)
    assert result is not None
    assert "expected_key" in result
    print(f"✅ {tool_name} passed")
```

---

### Fáza 2: AGENTS (integračné testy)

**Prístup:**
1. Otestovať každý agent s mock vstupmi
2. Overiť že agent vracia správny formát
3. Overiť že agent volá správne tools

**Test formát:**
```python
def test_agent_name():
    agent = AgentName()
    state = {"test_input": "value"}
    result = agent.run(state)
    assert result is not None
    print(f"✅ {agent_name} passed")
```

---

### Fáza 3: WORKFLOW (end-to-end testy)

**Prístup:**
1. Začať s 1 scénou (bez hlasu)
2. Postupne pridávať scény
3. Nakoniec pridať hlas

**Test scenáre:**
- [ ] 1 scéna, 2 snímky, 1 animácia (bez hlasu)
- [ ] 1 scéna, 3 snímky, 2 animácie (bez hlasu)
- [ ] 2 scény, 4 snímky, 3 animácie (bez hlasu)
- [ ] 3 scény, 6 snímok, 5 animácií (bez hlasu)
- [ ] 3 scény s hlasom (per-scene voiceover)

---

## TESTOVÉ VSTUPY

### Image prompts (`tests/inputs/test_prompts.txt`):
```
A cup of coffee on a wooden table, morning light, cinematic
A person holding a cup of coffee, smiling, warm lighting, portrait
Modern coffee shop interior, minimalist design, natural lighting
Close-up of coffee beans, macro photography, detailed texture
```

### Video prompts:
```
Camera slowly zooms into the coffee cup
Person lifts the cup and takes a sip
Camera pans across the coffee shop
Coffee beans falling in slow motion
```

### Test témy:
```
Simple: "coffee"
Medium: "morning coffee routine"
Complex: "the journey of a coffee bean"
```

---

## VÝSTUPNÁ ŠTRUKTÚRA

```
tests/
├── inputs/
│   ├── test_prompts.txt
│   ├── test_image.png (pre video tools)
│   └── test_audio.mp3 (pre assembly)
├── outputs/
│   ├── tool_name/
│   │   ├── result_1.png
│   │   └── result_2.mp4
│   └── workflow/
│       └── final_video.mp4
└── results/
    ├── tool_results.json
    ├── agent_results.json
    └── workflow_results.json
```

---

## VÝSLEDKOVÝ FORMÁT

```json
{
  "tool_name": "flux_dev",
  "status": "success",
  "time": 30.5,
  "cost": 0.03,
  "output": "tests/outputs/flux_dev/result_1.png",
  "error": null
}
```

---

## PRIORITA TESTOVANIA

### Priority 1: Image tools (najdôležitejšie)
1. Flux Dev (používa sa v HYBRID)
2. InstantCharacter (používa sa v PIKA)
3. Midjourney (používa sa v PIKA)

### Priority 2: Video tools
1. Veo 3.1 (používa sa v PIKA)
2. Wan (používa sa v HYBRID)
3. Minimax (lacný, pre testy)

### Priority 3: Agents
1. Creative Strategist
2. Visual Production Agent
3. Assembly Agent

### Priority 4: Workflow
1. 1 scéna test
2. Multi-scéna test
3. Full workflow s hlasom

---

## POZNÁMKY

- **Hlas:** Zatiaľ zakomentovať, pridať neskôr s per-scene timing
- **Štýly:** Nechať AI rozhodnúť (workflow router)
- **Kredit:** Začať s najlacnejšími tools (Flux Schnell, Minimax)
- **Errors:** Zaznamenať všetky chyby pre debugging

---

## NAJBLIŽŠIE KROKY

1. Vytvoriť test skripty pre všetky tools
2. Pripraviť test vstupy
3. Spustiť testy postupne
4. Zaznamenať výsledky
5. Opraviť nájdené chyby
6. Prejsť na agents
7. Prejsť na workflow
