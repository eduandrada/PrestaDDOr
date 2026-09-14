import random
import io
import json
from PIL import Image, ImageDraw, ImageFont

THEMES = {
    'canva_neon': {
        'name': 'Canva Neon Cyber',
        'bg_start': (11, 15, 25), 'bg_end': (30, 27, 75),
        'card_bg': (15, 23, 42, 220), 'card_border': (99, 102, 241),
        'accent_header': (2, 132, 199), 'accent_border': (56, 189, 248),
        'text_title': (255, 255, 255), 'text_sub': (56, 189, 248),
        'prize_header': (245, 158, 11), 'prize_text': (241, 245, 249),
        'num_bg': (15, 23, 42), 'num_border': (51, 65, 85), 'num_text': (226, 232, 240),
        'footer_bg': (2, 132, 199), 'badge_text': (254, 240, 138)
    },
    'pinterest_emerald': {
        'name': 'Pinterest Emerald Gold',
        'bg_start': (4, 47, 46), 'bg_end': (15, 23, 42),
        'card_bg': (6, 78, 59, 220), 'card_border': (52, 211, 153),
        'accent_header': (5, 150, 105), 'accent_border': (110, 231, 183),
        'text_title': (255, 255, 255), 'text_sub': (110, 231, 183),
        'prize_header': (251, 191, 36), 'prize_text': (240, 253, 244),
        'num_bg': (6, 78, 59), 'num_border': (16, 185, 129), 'num_text': (236, 253, 245),
        'footer_bg': (5, 150, 105), 'badge_text': (254, 240, 138)
    },
    'template_net_sunset': {
        'name': 'Template.net AI Sunset',
        'bg_start': (131, 24, 67), 'bg_end': (15, 23, 42),
        'card_bg': (88, 28, 135, 220), 'card_border': (244, 63, 94),
        'accent_header': (225, 29, 72), 'accent_border': (251, 113, 133),
        'text_title': (255, 255, 255), 'text_sub': (253, 164, 175),
        'prize_header': (250, 204, 21), 'prize_text': (255, 241, 242),
        'num_bg': (76, 29, 149), 'num_border': (168, 85, 247), 'num_text': (250, 232, 255),
        'footer_bg': (225, 29, 72), 'badge_text': (254, 240, 138)
    },
    'luxury_gold': {
        'name': 'VIP Luxury Gold',
        'bg_start': (9, 9, 11), 'bg_end': (24, 24, 27),
        'card_bg': (39, 39, 42, 230), 'card_border': (217, 119, 6),
        'accent_header': (180, 83, 9), 'accent_border': (251, 191, 36),
        'text_title': (254, 240, 138), 'text_sub': (251, 191, 36),
        'prize_header': (251, 191, 36), 'prize_text': (250, 250, 250),
        'num_bg': (24, 24, 27), 'num_border': (217, 119, 6), 'num_text': (254, 240, 138),
        'footer_bg': (180, 83, 9), 'badge_text': (254, 240, 138)
    }
}

def get_font(size, bold=False):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "calibrib.ttf" if bold else "calibri.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()

def create_gradient_bg(W, H, c1, c2):
    img = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(img)
    for y in range(H):
        ratio = y / H
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return img

def test_generate_flyer(title="GRAN BINGO & RIFA ANIVERSARIO", motive="Fondo de Construcción & Eventos", price=1500.0, draw_date="Sábado 20:00 hs", theme_key='canva_neon'):
    t = THEMES.get(theme_key, THEMES['canva_neon'])
    W, H = 1080, 1350
    img = create_gradient_bg(W, H, t['bg_start'], t['bg_end'])
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Fonts
    f_header = get_font(26, bold=True)
    f_title = get_font(46, bold=True)
    f_sub = get_font(26, bold=False)
    f_prize_h = get_font(28, bold=True)
    f_body = get_font(22, bold=False)
    f_num = get_font(18, bold=True)
    f_footer = get_font(24, bold=True)
    
    # Top Tag
    draw.rounded_rectangle([60, 35, W - 60, 105], radius=20, fill=t['accent_header'] + (240,), outline=t['accent_border'], width=2)
    draw.text((W // 2, 70), "✨ CANVA / PINTEREST AI TEMPLATE ✨", fill=(255, 255, 255), font=f_header, anchor="mm")
    
    # Title & Motive
    draw.text((W // 2, 160), title.upper(), fill=t['text_title'], font=f_title, anchor="mm")
    draw.text((W // 2, 215), f"📌 {motive}", fill=t['text_sub'], font=f_sub, anchor="mm")
    
    # Prizes Box
    draw.rounded_rectangle([60, 260, W - 60, 410], radius=22, fill=t['card_bg'], outline=t['card_border'], width=3)
    draw.text((85, 285), "🏆 PREMIOS DESTACADOS:", fill=t['prize_header'], font=f_prize_h)
    
    prizes = ["1° PREMIO: $150.000 EN EFECTIVO + ORDEN DE COMPRA", "2° PREMIO: CANASTA FAMILIAR DE MERCADERÍAS + VINO", "3° PREMIO: ELECTRODOMÉSTICO A ELECCIÓN"]
    y_p = 325
    for p in prizes:
        draw.text((95, y_p), f"✨ {p}", fill=t['prize_text'], font=f_body)
        y_p += 32
        
    # Grid Header
    draw.text((W // 2, 440), "ELEGÍ TU NÚMERO DEL 01 AL 100", fill=t['text_sub'], font=f_header, anchor="mm")
    
    # Grid Numbers
    total_nums = 100
    cols = 10
    rows = 10
    grid_top = 475
    grid_left = 60
    cell_w = (W - 120) // cols
    cell_h = 62
    
    for idx in range(total_nums):
        r_i = idx // cols
        c_i = idx % cols
        x1 = grid_left + c_i * cell_w + 3
        y1 = grid_top + r_i * cell_h + 3
        x2 = x1 + cell_w - 6
        y2 = y1 + cell_h - 6
        
        draw.rounded_rectangle([x1, y1, x2, y2], radius=10, fill=t['num_bg'] + (230,), outline=t['num_border'], width=1)
        draw.text(((x1 + x2) // 2, (y1 + y2) // 2), f"{idx+1:02d}", fill=t['num_text'], font=f_num, anchor="mm")
        
    # Footer Banner
    footer_top = H - 180
    draw.rounded_rectangle([60, footer_top, W - 60, H - 45], radius=25, fill=t['footer_bg'] + (240,), outline=t['accent_border'], width=3)
    draw.text((90, footer_top + 45), f"💵 VALOR DEL NÚMERO: ${price:,.2f}", fill=(255, 255, 255), font=f_footer)
    draw.text((90, footer_top + 90), f"📅 FECHA DE SORTEO: {draw_date}", fill=(240, 249, 255), font=f_body)
    draw.text((W - 90, footer_top + 65), "VERIFICADO ✓", fill=t['badge_text'], font=f_footer, anchor="rm")
    
    img.save("scratch_flyer_test.png")
    print("Flyer generated successfully: scratch_flyer_test.png")

test_generate_flyer()
