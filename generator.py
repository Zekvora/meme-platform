"""
MemeMakerBot - Meme Generator (Pillow)
8-position text placement
"""
import uuid
from pathlib import Path
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont

from config import GENERATED_DIR, FONT_PATHS


@dataclass
class TextBlock:
    """Text block with position and size."""
    text: str
    position: str  # top_left, top_center, top_right, middle_left, middle_right, bottom_left, bottom_center, bottom_right
    font_size: str  # small, medium, large, auto


# Position to coordinates mapping (relative to image)
# Format: (x_ratio, y_ratio, horizontal_align, vertical_align)
POSITIONS = {
    # Top center
    "top":      (0.50, 0.05, "center", "top"),
    # Left side (4 positions from top to bottom)
    "left_1":   (0.05, 0.20, "left", "top"),
    "left_2":   (0.05, 0.40, "left", "top"),
    "left_3":   (0.05, 0.60, "left", "top"),
    "left_4":   (0.05, 0.80, "left", "top"),
    # Right side (4 positions from top to bottom)
    "right_1":  (0.95, 0.20, "right", "top"),
    "right_2":  (0.95, 0.40, "right", "top"),
    "right_3":  (0.95, 0.60, "right", "top"),
    "right_4":  (0.95, 0.80, "right", "top"),
    # Bottom center
    "bottom":   (0.50, 0.95, "center", "bottom"),
}


def find_font() -> str | None:
    """Find available font with Cyrillic support."""
    for path in FONT_PATHS:
        if Path(path).exists():
            return path
    return None


def generate_meme(template_path: Path, text_blocks: list[TextBlock]) -> Path:
    """
    Generate meme with multiple text blocks at 8 positions.
    
    Args:
        template_path: Path to template image
        text_blocks: List of TextBlock with text, position, font_size
    """
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    
    with Image.open(template_path) as img:
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        font_path = find_font()
        
        for block in text_blocks:
            if not block.text.strip():
                continue
            
            _draw_text_at_position(
                draw, block.text.upper(), font_path,
                w, h, block.position, block.font_size
            )
        
        out_path = GENERATED_DIR / f"meme_{uuid.uuid4().hex[:12]}.jpg"
        img.save(out_path, format="JPEG", quality=92, optimize=True)
        return out_path


def _draw_text_at_position(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: str | None,
    img_width: int,
    img_height: int,
    position: str,
    font_size_setting: str
):
    """Draw text at one of 8 positions."""
    if not text.strip():
        return
    
    # Get position config (fallback to top)
    pos_config = POSITIONS.get(position, POSITIONS["top"])
    x_ratio, y_ratio, h_align, v_align = pos_config
    
    # Calculate font size
    if font_size_setting == "small":
        base_size = int(img_height * 0.05)
    elif font_size_setting == "medium":
        base_size = int(img_height * 0.08)
    elif font_size_setting == "large":
        base_size = int(img_height * 0.11)
    else:  # auto
        base_size = int(img_height * 0.08)
    
    base_size = max(16, min(base_size, 120))
    
    margin = int(img_width * 0.05)
    max_width = int(img_width * 0.45)  # Max 45% of image width per text
    
    # Find fitting font size
    font_size = base_size
    min_size = 14
    
    while font_size >= min_size:
        font = _load_font(font_path, font_size)
        lines = _wrap_text(draw, text, font, max_width)
        
        # Calculate total height
        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            total_height += bbox[3] - bbox[1] + int(font_size * 0.15)
        
        if total_height <= img_height * 0.35:
            break
        font_size -= 2
    
    font = _load_font(font_path, max(font_size, min_size))
    stroke_width = max(2, int(font_size * 0.08))
    
    lines = _wrap_text(draw, text, font, max_width)
    
    # Calculate line heights
    line_heights = []
    total_height = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        total_height += h
    
    line_spacing = int(font_size * 0.12)
    total_height += line_spacing * (len(lines) - 1)
    
    # Calculate Y start position
    base_y = int(img_height * y_ratio)
    if v_align == "top":
        y = base_y
    elif v_align == "middle":
        y = base_y - total_height // 2
    else:  # bottom
        y = base_y - total_height
    
    y = max(5, min(y, img_height - total_height - 5))
    
    # Draw each line
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        
        # Calculate X based on alignment
        base_x = int(img_width * x_ratio)
        if h_align == "left":
            x = base_x
        elif h_align == "center":
            x = base_x - line_width // 2
        else:  # right
            x = base_x - line_width
        
        x = max(margin, min(x, img_width - line_width - margin))
        
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(255, 255, 255),
            stroke_width=stroke_width,
            stroke_fill=(0, 0, 0),
        )
        
        y += line_heights[i] + line_spacing


def _load_font(font_path: str | None, size: int) -> ImageFont.FreeTypeFont:
    """Load font with fallback."""
    if font_path:
        try:
            return ImageFont.truetype(font_path, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines or [""]

