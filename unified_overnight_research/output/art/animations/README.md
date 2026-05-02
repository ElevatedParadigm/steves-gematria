# 🎬 Animation Generator Documentation

**Location**: `/unified_overnight_research/scripts/animation_generator.py`  
**Purpose**: Convert pattern trail discoveries into themed pixel art animations  
**Status**: ✅ Ready for execution

---

## 📖 What It Does

Generates animated video sequences showing:

| Scene | Theme | Metaphor | Use Case |
|-------|-------|----------|----------|
| **Fireflies** | Harmony/Integration | Twinkling sparks, golden particles | Discovery moments, cycle completion |
| **Embers** | Transformation | Rising red-orange embers | Completion cycles, domain transitions |
| **Neon Rain** | Cyberpunk Domain | Urban neon atmosphere (cyan/magenta) | Domain 938 visualizations, cluster maps |
| **Sparkles** | Discovery Moments | Magical dust, twinkling effect | Achievement celebrations, pattern finds |

---

## 🛠️ Usage

### Quick Start Commands

```bash
# Generate all animations for all trails (AUTO MODE)
cd /home/avalonas/.hermes/gematria/unified_overnight_research/scripts
python3 animation_generator.py --auto

# Generate specific scene only
python3 animation_generator.py --scene fireflies
python3 animation_generator.py --scene embers
python3 animation_generator.py --scene neon
python3 animation_generator.py --scene sparkles

# Use NES pixel art style
python3 animation_generator.py --preset nes

# Process all trails with all scenes
python3 animation_generator.py --auto --preset arcade
```

### Integration with Overnight Runner

Add to overnight runner script:

```bash
# After exports complete, optionally generate animations
if [ -f /unified_overnight_research/CURRENT_STATUS.md ]; then
    python3 /unified_overnight_research/scripts/animation_generator.py \
        --auto \
        --preset arcade \
        --output-dir /unified_overnight_research/output/art/animations
fi
```

---

## 📂 Output Structure

```
output/art/animations/
├── trail_correlation_fireflies.mp4      # Firefly harmony animation (6s)
├── trail_domain_matrix_embers.mp4       # Ember transformation animation (8s)
├── trail_cluster938_neon.mp4           # Neon rain cyberpunk (7s)
├── trail_discovery_sparkles.mp4        # Sparkle discovery moments (5s)
└── demo_correlation_fireflies.mp4      # Demo animations for testing
```

Each video is loopable and suitable for:
- Discord embeds (small size)
- Terminal display (via ASCII overlay if needed)  
- Obsidian callouts (embedded images, though MP4 needs browser viewing)

---

## 🎨 Scene Details

### 🔥 Fireflies Scene
**Duration**: 6 seconds @ 12fps = 72 frames  
**Palette**: Warm gold/amber/yellow (harmony theme)  
**Effects**: Twinkling particles rising upward like sparks of discovery  

**Best for**: 
- Cycle completion celebrations
- Harmony/Integration domain visualizations
- Achievement moments

### 🔥 Embers Scene  
**Duration**: 8 seconds @ 10fps = 80 frames  
**Palette**: Red-orange-red gradient (transformation theme)  
**Effects**: Rising embers symbolizing transformation and completion  

**Best for**:
- Domain transition sequences
- Completion cycle celebrations
- "Fire holds vessel" metaphor

### 🌧️ Neon Rain Scene
**Duration**: 7 seconds @ 15fps = 105 frames  
**Palette**: Cyan/magenta (cyberpunk theme)  
**Effects**: Urban rain with neon pulse (domain atmosphere)  

**Best for**:
- Domain 938 visualizations
- Cluster maps
- Cyberpunk aesthetic overlays

### ✨ Sparkles Scene
**Duration**: 5 seconds @ 12fps = 60 frames  
**Palette**: Soft pastels or adaptive white/gold (discovery theme)  
**Effects**: Magical dust and twinkling particles  

**Best for**:
- Discovery moment celebrations
- Pattern finding events
- Gentle aesthetic overlays

---

## 📋 Example Output Files

### Fireflies Harmony Animation:
```bash
./output/art/animations/trail_correlation_fireflies.mp4
# Duration: 6s | FPS: 12 | Style: NES pixel art + firefly particles
# Content: Golden sparks rising upward in harmony cycle pattern
```

### Embers Transformation Animation:
```bash
./output/art/animations/trail_domain_matrix_embers.mp4
# Duration: 8s | FPS: 10 | Style: Arcade pixel art + ember flow
# Content: Red-orange particles flowing upward representing change
```

---

## 🎯 Quick Reference

| Command | Purpose | Files Generated |
|---------|---------|-----------------|
| `--auto` | Process all trails with all scenes | 4 videos (one per scene) |
| `--scene fireflies` | Generate harmony animation only | 1 firefly video |
| `--preset nes` | Use NES 8-bit style | Same as above, different style |
| No args | Demo mode | Small test animations |

---

## 🔌 Dependencies

**Required:**
- Python 3.9+
- Pillow (`PIL.Image`)
- ffmpeg (for encoding MP4 - installed by default with Hermes)

**Optional (for full features):**
- pixel-art skill (`/home/avalonas/.hermes/skills/creative/pixel-art/`)

---

## ⚙️ Technical Implementation

### Pipeline:

1. **Discover Input**: Scan vault for `*correlation*.png`, `*domain*.png` files  
2. **Convert to Pixel Art**: Apply preset style (NES/arcade/etc) as base  
3. **Generate Scenes**: Overwrite particle effects per scene theme  
4. **Encode MP4**: Use ffmpeg with libx264, 1080p or lower if needed  

### Output Format:
- Container: MP4 (H.264/AAC)
- Resolution: Scaled to fit source image (max 720px width for Discord)
- Bitrate: Adaptive (target 250kbps for video quality)

---

## 📊 Status Tracking

Animation generation updates CURRENT_STATUS.md:

```markdown
## Animation Generation Status

Last Run: 2026-04-30 15:45:00
Mode: Auto (all trails, all scenes)

### Generated Files
✅ trail_correlation_fireflies.mp4 (6s, 4.2MB)
✅ trail_domain_matrix_embers.mp4 (8s, 5.1MB)  
✅ trail_cluster938_neon.mp4 (7s, 4.8MB)
✅ trail_discovery_sparkles.mp4 (5s, 3.9MB)

Total: 4 files, ~18MB downloaded/processed
```

---

## 🚀 Advanced Usage

### Create Demo Animations for Testing

```bash
# Quick demo with NES style
python3 animation_generator.py --preset nes

# Generate just fireflies for domain 938
python3 animation_generator.py \
    --scene fireflies \
    --preset arcade

# Custom output directory
export ANIMATION_OUTPUT=/tmp/animations
python3 animation_generator.py --auto
```

### Continuous Mode (in overnight loop)

Add to `overnight_runner_local.py`:

```bash
#!/usr/bin/env python3
...
# After manual_export_toolset.py runs
if args.generate_art:
    import subprocess
    result = subprocess.run([
        'python3', 
        '/unified_overnight_research/scripts/animation_generator.py',
        '--auto'
    ])
```

---

## 📖 See Also

- [README_TOOLS_SUITE.md](../scripts/README_TOOLS_SUITE.md) - All runner tools
- [PATTERN_TRAIL_ART_EXAMPLES.md](../output/PATTERN_TRAIL_ART_EXAMPLES.md) - ASCII art demos  
- `pixel-art` skill - Retro image conversion base
- overnight_runner_local.py - Automated research pipeline

---

**Created**: 2026-04-30  
**Mode**: Animation Scene Generator  
**Status**: ✅ Ready for pattern trail input
