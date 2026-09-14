import random
import io
import json
from PIL import Image, ImageDraw, ImageFont

CANVA_FLYER_THEMES = {
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
    },
    'cyber_indigo': {
        'name': 'Cyber Indigo Pink',
        'bg_start': (30, 16, 53), 'bg_end': (15, 23, 42),
        'card_bg': (49, 23, 80, 220), 'card_border': (236, 72, 153),
        'accent_header': (192, 38, 211), 'accent_border': (240, 171, 252),
        'text_title': (255, 255, 255), 'text_sub': (240, 171, 252),
        'prize_header': (234, 179, 8), 'prize_text': (253, 244, 255),
        'num_bg': (49, 23, 80), 'num_border': (217, 70, 239), 'num_text': (253, 242, 248),
        'footer_bg': (192, 38, 211), 'badge_text': (254, 240, 138)
    },
    'minimal_cream': {
        'name': 'Pinterest Chic Cream',
        'bg_start': (250, 250, 249), 'bg_end': (231, 229, 228),
        'card_bg': (255, 255, 255, 240), 'card_border': (194, 65, 12),
        'accent_header': (194, 65, 12), 'accent_border': (251, 146, 60),
        'text_title': (28, 25, 23), 'text_sub': (194, 65, 12),
        'prize_header': (194, 65, 12), 'prize_text': (44, 40, 37),
        'num_bg': (28, 25, 23), 'num_border': (68, 64, 60), 'num_text': (255, 255, 255),
        'footer_bg': (194, 65, 12), 'badge_text': (254, 240, 138)
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

def generate_90_ball_card():
    for _ in range(500):
        cols_with_two = set(random.sample(range(9), 6))
        col_counts = [2 if i in cols_with_two else 1 for i in range(9)]
        ranges = [(1, 9), (10, 19), (20, 29), (30, 39), (40, 49), (50, 59), (60, 69), (70, 79), (80, 90)]
        col_numbers = [sorted(random.sample(range(r[0], r[1] + 1), col_counts[i])) for i, r in enumerate(ranges)]
        grid = [[None]*9 for _ in range(3)]
        row_counts = [0, 0, 0]
        possible = True
        col_order = sorted(range(9), key=lambda c: col_counts[c], reverse=True)
        for c in col_order:
            cnt = col_counts[c]
            avail = [r for r in range(3) if row_counts[r] < 5 and grid[r][c] is None]
            if len(avail) < cnt:
                possible = False
                break
            selected_rows = sorted(random.sample(avail, cnt))
            for i_r, r_idx in enumerate(selected_rows):
                grid[r_idx][c] = col_numbers[c][i_r]
                row_counts[r_idx] += 1
        if possible and row_counts == [5, 5, 5]:
            return grid
    return None

def generate_75_ball_card():
    col_ranges = [('B', 1, 15), ('I', 16, 30), ('N', 31, 45), ('G', 46, 60), ('O', 61, 75)]
    card_cols = []
    for letter, start, end in col_ranges:
        count = 4 if letter == 'N' else 5
        nums = sorted(random.sample(range(start, end + 1), count))
        if letter == 'N':
            nums.insert(2, 'FREE')
        card_cols.append(nums)
    grid = []
    for row_i in range(5):
        grid.append([card_cols[col_i][row_i] for col_i in range(5)])
    return grid

print("Full flyer & bingo generator helper ready.")
