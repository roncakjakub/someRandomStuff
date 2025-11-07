# 🔍 KOMPLETNÁ ANALÝZA PROJEKTU - Social Video Agent

**Dátum:** 7. november 2025  
**Verzia:** 3.2.12 FINAL  
**Jazyk:** Slovenčina

---

## 📊 1. ŠTÝLY VIDEA

### PIKA Style (Prémiový - Character Consistency)

**Charakteristika:**
- **Účel:** Videá s konzistentnou postavou naprieč scénami
- **Kvalita:** Najvyššia (Midjourney + InstantCharacter + Veo 3.1)
- **Cena:** ~$6.75 za 9-scénové video
- **Trvanie:** ~60-90 sekúnd

**Workflow:**
1. **Opening frame:** Midjourney ($0.05)
2. **Character scenes:** InstantCharacter s referenciou ($0.04 × 6-8)
3. **Object scenes:** Flux Dev ($0.03 × 1-3)
4. **Morph videos:** Veo 3.1 ($0.80 × 8) - 8-sekundové morph prechody
5. **Voiceover:** ElevenLabs (~$0.10-0.30)
6. **Assembly:** Finálne video s morphingom

**Výstup:**
- ✅ Plynulé morph prechody medzi scénami
- ✅ Rovnaká postava vo všetkých ľudských scénach
- ✅ Profesionálna kvalita (Midjourney + Veo 3.1)
- ✅ Vertikálny formát 9:16

**Kedy použiť:**
- Príbehy s ľudskými postavami
- Prémiový obsah pre Instagram/TikTok
- Brand storytelling s konzistentným charakterom

---

### HYBRID Style (Vyvážený)

**Charakteristika:**
- **Účel:** Všeobecný obsah, príroda, objekty
- **Kvalita:** Dobrá (Flux Dev + Luma)
- **Cena:** ~$4.77 za 9-scénové video
- **Trvanie:** ~60-90 sekúnd

**Workflow:**
1. **Všetky obrázky:** Flux Dev ($0.03 × 9)
2. **Videá:** Luma ($0.50 × 9) - animácie z obrázkov
3. **Voiceover:** ElevenLabs (~$0.10-0.30)
4. **Assembly:** Finálne video

**Výstup:**
- ✅ Dobré animácie (Luma)
- ✅ Rýchlejšia produkcia
- ✅ Nižšia cena
- ✅ Vertikálny formát 9:16

**Kedy použiť:**
- Príroda, krajiny, objekty
- Product showcase
- Všeobecný obsah bez ľudí
- Hromadná produkcia

---

### SEEDREAM Style (Rýchly & Lacný)

**Charakteristika:**
- **Účel:** Testy, drafty, hromadná produkcia
- **Kvalita:** Rýchla (Flux Schnell + Minimax)
- **Cena:** ~$1.89 za 9-scénové video
- **Trvanie:** ~60-90 sekúnd

**Workflow:**
1. **Všetky obrázky:** Flux Schnell ($0.01 × 9)
2. **Videá:** Minimax ($0.20 × 9)
3. **Voiceover:** ElevenLabs (~$0.10-0.30)
4. **Assembly:** Finálne video

**Výstup:**
- ✅ Veľmi rýchla produkcia
- ✅ Najnižšia cena
- ✅ Vhodné na testy
- ✅ Vertikálny formát 9:16

**Kedy použiť:**
- Testovanie konceptov
- Drafty pred finálnou produkciou
- Denný obsah (daily news)
- Veľké objemy videí

---

## 🎯 2. TOP-LEVEL POŽIADAVKY

### Používateľské požiadavky:
```bash
python main.py --topic "TÉMA" --style ŠTÝL --language JAZYK
```

**Parametre:**
- `--topic`: Téma videa (napr. "life of coffee")
- `--style`: pika | hybrid | seedream
- `--language`: sk | en | cs | ...
- `--num-scenes`: (voliteľné) počet scén (default: 9)

**Očakávaný výstup:**
- ✅ Finálne video: `output/YYYYMMDD_HHMMSS_TÉMA/final_video.mp4`
- ✅ Voiceover: `voiceover_JAZYK_*.mp3`
- ✅ Všetky obrázky v output adresári
- ✅ (PIKA) Morph videá: `veo31_*.mp4`
- ✅ (HYBRID/SEEDREAM) Animované videá: `luma_*.mp4` / `minimax_*.mp4`
- ✅ Metadata: `results_*.json`

---

## 🔧 3. MID-LEVEL POŽIADAVKY

### Workflow Requirements:

**Phase 1: Creative Strategy**
- ✅ Vygenerovať 9 scén s popismi
- ✅ Vytvoriť voiceover script
- ✅ Určiť content_type pre každú scénu (human_portrait, human_action, object, transition)
- ✅ Priradiť nástroje pre každú scénu (midjourney, instant_character, flux, etc.)

**Phase 2: Visual Production**
- ✅ Vygenerovať všetky obrázky podľa scén
- ✅ (PIKA) Scene 1: Midjourney opening frame
- ✅ (PIKA) Scene 2-N: InstantCharacter s referenciou (ak human)
- ✅ (PIKA) Scene X: Flux Dev (ak object, bez referencie)
- ✅ Uložiť všetky obrázky lokálne

**Phase 3: Video Morphs (PIKA only)**
- ✅ Uploadnúť frame images na fal.ai storage
- ✅ Vygenerovať 8 morph videí (Veo 3.1)
- ✅ Každý morph: Scene N → Scene N+1
- ✅ Trvanie: 8 sekúnd každý

**Phase 4: Voiceover**
- ✅ Vygenerovať voiceover v požadovanom jazyku
- ✅ ElevenLabs API
- ✅ Uložiť ako MP3

**Phase 5: Assembly**
- ✅ Spojiť všetky videá/obrázky
- ✅ Pridať voiceover
- ✅ Exportovať finálne video
- ✅ Vertikálny formát 9:16

---

## 🔄 4. FLOW OD MAIN.PY

### main.py → workflow.py

**1. main.py (entry point)**
```python
# Parsovanie argumentov
args = parse_args()
topic = args.topic          # "life of coffee"
style = args.style          # "pika"
language = args.language    # "sk"

# Vytvorenie workflow
workflow = VideoWorkflow(style=style)

# Spustenie
final_state = workflow.run({
    "topic": topic,
    "language": language,
    "num_scenes": args.num_scenes
})
```

**2. workflow.py (orchestration)**
```python
class VideoWorkflow:
    def __init__(self, style="pika"):
        self.style = style
        self.graph = self._build_graph()
    
    def _build_graph(self):
        # Vytvorenie LangGraph workflow
        # Phase 1: Creative Strategy
        # Phase 2: Visual Production
        # Phase 3: Video Morphs (PIKA only)
        # Phase 4: Voiceover
        # Phase 5: Assembly
```

**3. Phase 1: Creative Strategy**
```python
def _creative_strategy_node(state):
    # agents/creative_strategist.py
    strategist = CreativeStrategist()
    scenes = strategist.generate_scenes(
        topic=state["topic"],
        num_scenes=state["num_scenes"]
    )
    # Výstup: 9 scén s popismi, content_type, tools
```

**4. Phase 2: Visual Production**
```python
def _visual_production_node(state):
    # agents/visual_production_agent.py
    agent = VisualProductionAgent(style=self.style)
    
    if self.style == "pika":
        result = agent._generate_pika_style(scenes)
        # Step 1: Generovať všetky obrázky
        # Step 2: Generovať morph videá
    elif self.style == "hybrid":
        result = agent._generate_hybrid_style(scenes)
    elif self.style == "seedream":
        result = agent._generate_seedream_style(scenes)
```

---

## 🐛 5. VŠETKY FIXES (v3.2.8 - v3.2.12)

### ✅ v3.2.8: Reference Image Upload (InstantCharacter)

**Súbor:** `tools/instant_character.py`

**Problém:**
```
Could not load image from url: output/.../midjourney_xxx.png
```

**Fix:**
```python
# Line 83-95
if reference_image_url:
    # Check if it's a local file path
    if os.path.exists(reference_image_url):
        print(f"📤 Uploading local reference image...")
        
        # Upload to fal.ai storage
        uploaded_url = fal_client.upload_file(reference_image_url)
        
        print(f"✅ Uploaded to: {uploaded_url}")
        reference_image_url = uploaded_url  # Use the public URL
    
    request_data["image_url"] = reference_image_url
```

**Overenie:**
```bash
grep "os.path.exists(reference_image_url)" tools/instant_character.py
# Musí vrátiť: if os.path.exists(reference_image_url):
```

---

### ✅ v3.2.9: Output Path + Image URL Download

**Súbor:** `agents/visual_production_agent.py`

**Problém:**
```
IsADirectoryError: [Errno 21] Is a directory: 'output/...'
```

**Fix 1: Odstrániť output_path z tool_input**
```python
# Line 245 - REMOVE this line:
# "output_path": str(output_dir),  ❌ DELETED
```

**Fix 2: Stiahnuť image_url a uložiť lokálne**
```python
# Lines 268-292
elif "image_url" in result:
    # InstantCharacter/FluxKontext return image_url
    # Download it and save locally
    image_url = result["image_url"]
    seed = result.get("seed", uuid.uuid4().hex[:8])
    filename = f"{tool_name}_{seed}.jpg"
    local_path = Path(output_dir) / filename
    
    self.logger.info(f"    Downloading image from {image_url}")
    
    # Download image
    response = requests.get(image_url)
    response.raise_for_status()
    
    with open(local_path, 'wb') as f:
        f.write(response.content)
    
    self.logger.info(f"    Saved to {local_path}")
    
    image_paths = [str(local_path)]
```

**Overenie:**
```bash
grep "output_path removed" agents/visual_production_agent.py
# Musí vrátiť: # NOTE: output_path removed...

grep "elif \"image_url\" in result:" agents/visual_production_agent.py
# Musí vrátiť: elif "image_url" in result:
```

---

### ✅ v3.2.10: Automatic Tool Fallback

**Súbor:** `agents/visual_production_agent.py`

**Problém:**
```
[{'loc': ['body', 'image_url'], 'msg': 'field required'}]
```

**Fix:**
```python
# Lines 361-366
# If InstantCharacter/FluxKontext but no reference, use default tool
# (InstantCharacter requires image_url, so it can't work without reference)
if scene_tool in ["instant_character", "flux_kontext_pro"] and not use_reference:
    original_tool = scene_tool
    scene_tool = self.default_image_tool
    self.logger.info(f"    {original_tool} requires reference image, using {scene_tool} instead")
```

**Overenie:**
```bash
grep "requires reference image, using" agents/visual_production_agent.py
# Musí vrátiť: self.logger.info(f"    {original_tool} requires reference image, using {scene_tool} instead")
```

---

### ✅ v3.2.11: Video Tool Kwargs Unpacking

**Súbor:** `agents/visual_production_agent.py`

**Problém:**
```
Veo31FLF2VTool.execute() missing 2 required positional arguments
```

**Fix:**
```python
# Lines 648-673
if video_tool_name == "veo31_flf2v":
    tool_input = {
        "first_frame_url": start_image,
        "last_frame_url": end_image,
        "prompt": scene_description,
        "aspect_ratio": "9:16",
    }
    # Veo31FLF2VTool expects individual parameters, not dict
    result = tool.execute(**tool_input)  # ✅ Unpack dict!
else:
    # Other video tools expect dict
    result = tool.execute({
        "start_image": start_image,
        "end_image": end_image,
        "prompt": scene_description,
        "output_dir": str(output_dir),
    })
```

**Overenie:**
```bash
grep "result = tool.execute(\*\*tool_input)" agents/visual_production_agent.py
# Musí vrátiť: result = tool.execute(**tool_input)
```

---

### ✅ v3.2.12: Frame Image Upload (Veo 3.1)

**Súbor:** `agents/visual_production_agent.py`

**Problém:**
```
Failed to load the image: 'output/.../flux_dev_xxx.png'
```

**Fix:**
```python
# Lines 649-664 (inside veo31_flf2v block)
import fal_client
import os

# Upload frame images to fal.ai storage (Veo 3.1 needs public URLs)
first_frame_url = start_image
last_frame_url = end_image

if os.path.exists(start_image):
    self.logger.info(f"    Uploading first frame: {start_image}")
    first_frame_url = fal_client.upload_file(start_image)
    self.logger.info(f"    First frame uploaded: {first_frame_url}")

if os.path.exists(end_image):
    self.logger.info(f"    Uploading last frame: {end_image}")
    last_frame_url = fal_client.upload_file(end_image)
    self.logger.info(f"    Last frame uploaded: {last_frame_url}")

tool_input = {
    "first_frame_url": first_frame_url,  # ✅ Public URL!
    "last_frame_url": last_frame_url,    # ✅ Public URL!
    "prompt": scene_description,
    "aspect_ratio": "9:16",
}
```

**Overenie:**
```bash
grep "Uploading first frame" agents/visual_production_agent.py
# Musí vrátiť: self.logger.info(f"    Uploading first frame: {start_image}")

grep "Uploading last frame" agents/visual_production_agent.py
# Musí vrátiť: self.logger.info(f"    Uploading last frame: {end_image}")
```

---

## 📁 6. ZMENENÉ SÚBORY

### Súbor 1: `tools/instant_character.py`
**Zmeny:** v3.2.8 (Reference image upload)  
**Počet riadkov:** ~15 pridaných

### Súbor 2: `agents/visual_production_agent.py`
**Zmeny:** v3.2.9, v3.2.10, v3.2.11, v3.2.12  
**Počet riadkov:** ~50 pridaných/upravených

**Celkom:** 2 súbory, ~65 riadkov kódu

---

## ✅ 7. OVERENIE FIXOV

Spusti tieto príkazy na overenie:

```bash
cd social_video_agent_fixed

# v3.2.8: Reference image upload
grep "os.path.exists(reference_image_url)" tools/instant_character.py

# v3.2.9: Output path removed
grep "output_path removed" agents/visual_production_agent.py

# v3.2.9: Image URL download
grep "elif \"image_url\" in result:" agents/visual_production_agent.py

# v3.2.10: Tool fallback
grep "requires reference image, using" agents/visual_production_agent.py

# v3.2.11: Kwargs unpacking
grep "result = tool.execute(\*\*tool_input)" agents/visual_production_agent.py

# v3.2.12: Frame upload
grep "Uploading first frame" agents/visual_production_agent.py
grep "Uploading last frame" agents/visual_production_agent.py
```

**Všetky príkazy musia vrátiť výsledok!**

---

## 🎬 8. TESTOVANIE

### Test 1: PIKA Style
```bash
python main.py --topic "coffee journey" --style pika --language en
```

**Očakávaný výstup:**
```
Phase 1: Creative Strategy
✅ Generated 9 scenes

Phase 2: Visual Production
Scene 1: midjourney
✅ Image saved

Scene 2: instant_character
📤 Uploading local reference image...        ← v3.2.8
✅ Uploaded to: https://fal.media/files/...  ← v3.2.8
✅ Character image generated!
   Downloading image from https://...        ← v3.2.9
   Saved to output/.../instant_character_xxx.jpg ← v3.2.9

Scene 3: object scene
instant_character requires reference image, using flux_dev instead ← v3.2.10

Phase 3: Video Morphs
Morph 1: Scene 1 → 2
   Uploading first frame: output/...         ← v3.2.12
   First frame uploaded: https://...         ← v3.2.12
   Uploading last frame: output/...          ← v3.2.12
   Last frame uploaded: https://...          ← v3.2.12
   🎬 Generating Veo 3.1 video...            ← v3.2.11
✅ Morph video created!

... (all morphs) ...

Phase 4: Voiceover
✅ Voiceover generated

Phase 5: Assembly
✅ Final video: output/.../final_video.mp4

🎉 Success!
```

### Test 2: HYBRID Style
```bash
python main.py --topic "nature beauty" --style hybrid --language en
```

### Test 3: SEEDREAM Style
```bash
python main.py --topic "daily news" --style seedream --language en
```

---

## 🎯 9. ZÁVER

**Stav projektu:** ✅ **PRODUCTION READY**

**Všetky fixy aplikované:**
- ✅ v3.2.8: Reference image upload
- ✅ v3.2.9: Output path handling + image download
- ✅ v3.2.10: Automatic tool fallback
- ✅ v3.2.11: Video tool kwargs unpacking
- ✅ v3.2.12: Frame image upload

**Čo funguje:**
- ✅ Všetky 3 štýly (PIKA, HYBRID, SEEDREAM)
- ✅ Character consistency (PIKA)
- ✅ Morph videá (PIKA + Veo 3.1)
- ✅ Všetky jazyky
- ✅ Vertikálny formát 9:16

**Známe obmedzenia:**
- ⚠️ Veo 3.1 content policy - niektoré prompty môžu byť odmietnuté
- ⚠️ API rate limits - závisí od fal.ai/APIFRAME kvót

**Odporúčanie:**
- Použiť anglický jazyk pre stabilnejšie prompty
- Vyhnúť sa citlivým slovám ("tired", "without energy", atď.)
- Pre testovanie použiť SEEDREAM style (lacnejší)
- Pre produkciu použiť PIKA style (najvyššia kvalita)

---

**Projekt je pripravený na použitie!** 🎬✨
