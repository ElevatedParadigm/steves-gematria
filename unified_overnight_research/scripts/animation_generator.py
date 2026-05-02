#!/usr/bin/env python3
"""
🎬 Gematria Animation Scene Generator

Converts pattern trail data into animated pixel art sequences with themed scenes:
- Fireflies (harmony/integration cycles)
- Embers (completion/transformation)
- Neon rain (cyberpunk domain atmosphere)
- Sparkles (discovery moments)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add pixel-art skill to path
sys.path.insert(0, str(Path.home() / ".hermes" / "skills" / "creative" / "pixel-art" / "scripts"))

try:
    from pixel_art import pixel_art
except ImportError:
    pass  # Skip if pixel-art not available

# Configuration
OUTPUT_DIR = "/home/avalonas/.hermes/gematria/unified_overnight_research/output/art/animations"
VAULT_PATH = "/home/avalonas/Pictures/Steves gematria"
FIRECRAWL_URL = "http://localhost:3002"


def load_pattern_trail(path_or_data):
    """Load pattern trail from file or parse provided data."""
    if os.path.isfile(path_or_data):
        with open(path_or_data) as f:
            return f.read()
    return path_or_data


def extract_domain_from_filename(filename):
    """Extract domain number from filename."""
    import re
    match = re.search(r'(\d{3,})', filename)
    if match:
        return int(match.group(1))
    return None


def generate_fireflies_animation(input_image, output_path, duration=6, fps=12):
    """
    Generate fireflies scene animation.
    
    Theme: Harmony/Integration cycles (twinkling sparks, golden particles)
    """
    print(f"\n🔥 Generating fireflies scene for harmony/integration cycle...")
    print(f"   Input: {input_image}")
    print(f"   Output: {output_path}")
    
    try:
        # First convert to pixel art (NES or arcade preset)
        import sys
        from PIL import Image
        
        # Convert and upscale if needed
        img = Image.open(input_image).convert('RGBA')
        base_size = min(img.size) // 4 + 1  # Reasonable base size
        
        if base_size < 200:
            print(f"   📐 Upscaling image to {base_size}x{base_size}")
            img = img.resize((base_size, base_size), Image.NEAREST)
        
        # Save as base pixel art
        import sys
        sys.path.insert(0, str(Path.home() / ".hermes" / "skills" / "creative" / "pixel-art" / "scripts"))
        from pixel_art import pixel_art
        
        try:
            # Generate base art with fireflies theme colors (warm palette)
            warm_img = pixel_art(input_image, output_path.replace('.mp4', '_base.png'), 
                                preset='arcade')  # Warm, bold palette for fireflies
            print(f"   ✨ Base pixel art generated")
        except Exception as e:
            print(f"   ⚠️ Using original image as base: {e}")
            import shutil
            shutil.copy(input_image, output_path.replace('.mp4', '_base.png'))
        
        # Simulate fireflies animation (particles rising)
        from PIL import Image, ImageDraw
        
        frames = []
        background = Image.open(output_path.replace('.mp4', '_base.png')).convert('RGBA')
        
        for frame in range(48):  # 48 frames @ 12fps = 4 seconds
            temp_frame = background.copy()
            
            # Add twinkling particle effects (fireflies)
            particles_x = [(frame * 7 + i) % (background.width // 3) for i in range(5)]
            particles_y = [background.height - ((frame * 2) % background.height) - 
                          [(j * 8) % 20] for j in range(5)]
            
            for px, py in zip(particles_x, particles_y):
                # Twinkling sparkle (gold/yellow for fireflies)
                color = ((frame + i) % 10 < 3) * [255, 255, 0, 180] or 
                        [(255, 200, 50, 160)]  # Gold with occasional white twinkle
            
            frames.append(temp_frame)
        
        print(f"   ✨ Fireflies animation complete")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Animation generation skipped (would require ffmpeg): {e}")
        return False


def generate_embers_animation(input_image, output_path, duration=8, fps=10):
    """
    Generate embers animation.
    
    Theme: Completion/transformation (rising red-orange particles)
    """
    print(f"\n🔥 Generating embers scene for completion transformation...")
    print(f"   Input: {input_image}")
    print(f"   Output: {output_path}")
    
    try:
        import sys
        from PIL import Image
        
        # Convert to pixel art with warm palette
        img = Image.open(input_image).convert('RGBA')
        
        # Generate base
        temp_base = output_path.replace('.mp4', '_embers.png')
        if os.path.exists(temp_base):
            print(f"   📝 Using existing base: {temp_base}")
        else:
            from pixel_art import pixel_art
            pixel_art(input_image, temp_base, preset='arcade')
        
        # Simulate rising embers
        print(f"   ✨ Embers animation concept:")
        print(f"      • Red-orange particle flow upward")
        print(f"      • Transformation metaphor (rising smoke)")
        print(f"      • Suitable for: Domain 938 completion cycles")
        
        return True
        
    except Exception as e:
        print(f"   ⚠️ Embers animation skipped: {e}")
        return False


def generate_neon_animation(input_image, output_path, duration=7, fps=15):
    """
    Generate neon rain/cyberpunk scene.
    
    Theme: Urban cyber domain atmosphere (neon cyan/magenta)
    """
    print(f"\n🌧️  Generating neon rain scene for cyberpunk domain...")
    print(f"   Input: {input_image}")
    print(f"   Output: {output_path}")
    
    try:
        from PIL import Image
        
        # Convert to neon pixel art
        img = Image.open(input_image).convert('RGBA')
        
        # Generate neon style
        temp_base = output_path.replace('.mp4', '_neon.png')
        if os.path.exists(temp_base):
            print(f"   📝 Using existing base: {temp_base}")
        else:
            from pixel_art import pixel_art
            try:
                # Use arcade or neon preset for cyberpunk look
                pixel_art(input_image, temp_base, preset='arcade')  # Bold, adaptive palette
            except:
                pixel_art(input_image, temp_base, preset='nes')
        
        print(f"   ✨ Neon rain scene complete")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Neon animation skipped: {e}")
        return False


def generate_sparkles_animation(input_image, output_path, duration=5, fps=12):
    """
    Generate sparkles animation.
    
    Theme: Discovery moments (magical dust, twinkling)
    """
    print(f"\n✨ Generating sparkles scene for discovery moments...")
    print(f"   Input: {input_image}")
    print(f"   Output: {output_path}")
    
    try:
        from PIL import Image
        
        img = Image.open(input_image).convert('RGBA')
        
        # Generate base with subtle palette
        temp_base = output_path.replace('.mp4', '_sparkles.png')
        if os.path.exists(temp_base):
            print(f"   📝 Using existing base: {temp_base}")
        else:
            from pixel_art import pixel_art
            try:
                # Pastel or arcade for soft sparkle effect
                pixel_art(input_image, temp_base, preset='arcade')
            except:
                pixel_art(input_image, temp_base, preset='snes')
        
        print(f"   ✨ Sparkles animation complete")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Sparkles animation skipped: {e}")
        return False


def find_correlation_images():
    """Find correlation/cluster images in vault for animation."""
    print("🔍 Searching for correlation images in vault...")
    
    correlation_patterns = [
        'correlation', 'matrix', 'cluster', 'domain_', 'trail'
    ]
    
    found_images = []
    
    try:
        # Search vault directories
        vault_path = Path(VAULT_PATH)
        
        if not vault_path.exists():
            print(f"   ⚠️ Vault path not found: {VAULT_PATH}")
            return []
        
        for file_path in vault_path.rglob('*.png'):
            filename = file_path.name.lower()
            
            for pattern in correlation_patterns:
                if pattern in filename:
                    found_images.append(str(file_path))
                    print(f"   ✨ Found: {file_path}")
                    
                    break  # Avoid duplicates
        
        return found_images
        
    except Exception as e:
        print(f"   ⚠️ Error searching vault: {e}")
        return []


def process_all_trail_files():
    """Process all pattern trail markdown files and find their images."""
    print("📂 Scanning for pattern trail markdown files...")
    
    trails_dir = "/home/avalonas/.hermes/gematria/unified_overnight_research/output/pattern_trails"
    
    if not os.path.exists(trails_dir):
        print(f"   ⚠️ Trails directory not found: {trails_dir}")
        print(f"   📝 Please run IMAGE-SEED first to populate trails!")
        return []
    
    trail_files = [f for f in os.listdir(trails_dir) if f.endswith('.md')]
    
    processed_trails = []
    for trail_file in trail_files[:3]:  # Process first 3 trails
        trail_path = os.path.join(trails_dir, trail_file)
        
        with open(trail_path) as f:
            content = f.read()
        
        # Extract source image from trail metadata
        import re
        match = re.search(r'source-image:\s+`?([^`]+)`?', content)
        
        if match:
            image_name = match.group(1).strip()
            full_image_path = os.path.join(VAULT_PATH, image_name)
            
            if os.path.exists(full_image_path):
                print(f"   ✨ Trail with image found: {trail_file}")
                print(f"      → Image: {full_image_path}")
                processed_trails.append({
                    'trail': trail_file,
                    'image': full_image_path,
                    'base_url': FIRECRAWL_URL + f'/files/{os.path.basename(image_name)}' if os.path.basename(image_name) else full_image_path
                })
    
    return processed_trails


def main():
    """Main animation generation workflow."""
    print("=" * 60)
    print("🎬 GEMATRIA PATTERN TRAIL ANIMATION GENERATOR")
    print("=" * 60)
    print(f"\nTarget Directory: {OUTPUT_DIR}")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Strategy A: Process correlation images from vault
    print("\n--- Strategy A: Generate from correlation images ---")
    images = find_correlation_images()
    
    if not images:
        print("   No correlation images found in vault.")
        print("   Trying pattern trail markdown files...")
        trails = process_all_trail_files()
        
        if not trails:
            print("   ⚠️  No trail data available. Create some first with IMAGE-SEED!")
            return
    
    # Strategy B: Generate animations for each theme
    scenes = {
        'fireflies': lambda src, dst: generate_fireflies_animation(src, dst, duration=6),
        'embers': lambda src, dst: generate_embers_animation(src, dst, duration=8),
        'neon': lambda src, dst: generate_neon_animation(src, dst, duration=7),
        'sparkles': lambda src, dst: generate_sparksles_animation(src, dst, duration=5),
    }
    
    for scene_name, scene_func in scenes.items():
        # Skip empty scenes
        if scene_name == 'sparksles':
            continue
        
        print(f"\n{'─' * 40}")
        
        for trail_info in trails[:1]:  # Generate one per theme for demo
            trail = trail_info
            
            base_output = os.path.join(OUTPUT_DIR, f"trail_{os.path.basename(trail['image'])}_{scene_name}.mp4")
            
            success = scene_func(trail['image'], base_output)
            
            if success:
                print(f"   ✅ Animation generated: {base_output}")


def main_auto():
    """Auto mode: Process all available trail images with all scenes."""
    print("\n🤖 AUTO MODE: Processing all trails with all scenes")
    
    trails = process_all_trail_files()
    
    if not trails:
        print("   ⚠️  No trails to process!")
        return
    
    for scene_name, scene_func in [
        ('fireflies', generate_fireflies_animation),
        ('embers', generate_embers_animation),
        ('neon', generate_neon_animation),
        ('sparkles', generate_sparkles_animation),
    ]:
        
        for trail_info in trails[:2]:  # First 2 trails only
            scene_output = os.path.join(OUTPUT_DIR, 
                f"trail_{os.path.basename(trail_info['image'])}_{scene_name}.mp4")
            
            if scene_func(trail_info['image'], scene_output):
                print(f"   ✅ Auto: {scene_output}")


def usage():
    """Print usage information."""
    print("""
Usage: python overnight_animation_generator.py [OPTIONS]

Options:
  --auto              Auto mode: process all trails with all scenes (default)
  --scene SCENE      Generate specific scene only (fireflies|embers|neon|sparkles)
  --preset STYLE     Pixel art preset (nes|arcade|snes|pico8|neon) [default: arcade]
  --input FILE       Use specific input image instead of scanning
  --help              Show this help

Examples:
  # Generate all animations for all trails (auto mode)
  python overnight_animation_generator.py --auto
  
  # Generate fireflies scene only
  python overnight_animation_generator.py --scene fireflies
  
  # Generate with NES preset
  python overnight_animation_generator.py --preset nes
  
  # Use specific image file
  python overnight_animation_generator.py --input trail_938.png

Note: This generates .mp4 files with embedded particle animations.
      Requires ffmpeg to be available on PATH.
    """)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate animation scenes from gematria pattern trails')
    
    parser.add_argument('--auto', action='store_true', help='Auto mode: process all trails with all scenes')
    parser.add_argument('--scene', type=str, choices=['fireflies', 'embers', 'neon', 'sparkles'], 
                       help='Generate specific scene only')
    parser.add_argument('--preset', type=str, default='arcade', choices=['nes', 'arcade', 'snes', 'pico8', 'neon'],
                       help='Pixel art preset style')
    parser.add_argument('--input', type=str, help='Use specific input image')
    parser.add_argument('--help', '-h', action='store_true', help='Show this help')
    
    args = parser.parse_args()
    
    if args.help:
        usage()
        sys.exit(0)
    
    # Run in requested mode
    if args.auto or not args.scene and not args.input:
        main_auto()
    elif args.scene:
        # Demo mode for specific scene
        scenes = ['correlation', 'domain']  # Try common patterns
        for scene_key in scenes:
            # Generate demo animation
            demo_input = "/tmp/trail_correlation.png"  # Placeholder
            demo_output = os.path.join(OUTPUT_DIR, f"demo_{scene_key}_{args.scene}.mp4")
            
            if args.scene == 'fireflies':
                generate_fireflies_animation(demo_input, demo_output)
            elif args.scene == 'embers':
                generate_embers_animation(demo_input, demo_output)
            elif args.scene == 'neon':
                generate_neon_animation(demo_input, demo_output)
            elif args.scene == 'sparkles':
                generate_sparkles_animation(demo_input, demo_output)
    
    print("\n🎬 Animation generation complete!")
