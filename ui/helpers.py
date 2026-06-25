# pyrefly: ignore [missing-import]
import pygame
from config.settings import C

# Vẽ hộp nhập liệu số với nút tăng giảm.
def draw_input_box(screen, rect, font, text, is_active=False):
    pygame.draw.rect(screen, C.INPUT_BG, rect, border_radius=4)
    if is_active:
        pygame.draw.rect(screen, C.BTN_BLUE, rect, 1, border_radius=4)
        
    ts = font.render(text, True, C.INPUT_TEXT)
    screen.blit(ts, (rect.x + 8, rect.y + (rect.h - ts.get_height()) // 2))
    
    cx = rect.right - 10
    cy = rect.y + rect.h // 2
    pygame.draw.polygon(screen, C.BTN_GRAY, [(cx-4, cy-2), (cx+4, cy-2), (cx, cy-6)])
    pygame.draw.polygon(screen, C.BTN_GRAY, [(cx-4, cy+2), (cx+4, cy+2), (cx, cy+6)])
    
    r_up = pygame.Rect(rect.right - 20, rect.y, 20, rect.h // 2)
    r_down = pygame.Rect(rect.right - 20, rect.y + rect.h // 2, 20, rect.h // 2)
    return r_up, r_down

# Vẽ nút bấm trên thanh công cụ hỗ trợ trạng thái vô hiệu hóa/nhấp chuột.
def draw_toolbar_btn(screen, rect, text, font, color_bg, is_enabled=True, icon=None):
    alpha = 255 if is_enabled else 100
    bg_color = (*color_bg[:3], alpha)
    
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s, bg_color, (0, 0, rect.w, rect.h), border_radius=4)
    screen.blit(s, (rect.x, rect.y))
    
    ts = font.render(text, True, C.TEXT_WHITE)
    if not is_enabled:
        ts.set_alpha(100)
        
    if icon:
        if not is_enabled:
            icon = icon.copy()
            icon.set_alpha(100)
        total_w = icon.get_width() + 5 + ts.get_width()
        start_x = rect.x + (rect.w - total_w) // 2
        screen.blit(icon, (start_x, rect.y + (rect.h - icon.get_height()) // 2))
        screen.blit(ts, (start_x + icon.get_width() + 5, rect.y + (rect.h - ts.get_height()) // 2))
    else:
        screen.blit(ts, (rect.x + (rect.w - ts.get_width())//2, rect.y + (rect.h - ts.get_height())//2))

# Vẽ hiệu ứng 3D nổi cho các ô chưa mở.
def draw_3d_cell(screen, rect, pressed=False):
    if not pressed:
        pygame.draw.rect(screen, C.CELL_HIDDEN_CENTER, rect)
        pygame.draw.polygon(screen, C.CELL_HIDDEN_TOP, [
            (rect.left, rect.bottom), (rect.left, rect.top), (rect.right, rect.top),
            (rect.right-3, rect.top+3), (rect.left+3, rect.top+3), (rect.left+3, rect.bottom-3)
        ])
        pygame.draw.polygon(screen, C.CELL_HIDDEN_BOT, [
            (rect.left, rect.bottom), (rect.right, rect.bottom), (rect.right, rect.top),
            (rect.right-3, rect.top+3), (rect.right-3, rect.bottom-3), (rect.left+3, rect.bottom-3)
        ])
    else:
        pygame.draw.rect(screen, C.CELL_REVEALED, rect)
        pygame.draw.rect(screen, C.CELL_REVEALED_BORDER, rect, 1)

def draw_revealed_cell(screen, rect):
    pygame.draw.rect(screen, C.CELL_REVEALED, rect)
    pygame.draw.rect(screen, C.CELL_REVEALED_BORDER, rect, 1)

# Vẽ hình quả mìn màu đỏ và ngòi nổ.
def draw_mine(screen, rect):
    draw_revealed_cell(screen, rect)
    pygame.draw.rect(screen, C.MINE_BG, rect)
    pygame.draw.rect(screen, C.CELL_REVEALED_BORDER, rect, 1)
    
    cx, cy = rect.center
    r = min(rect.w, rect.h) // 4
    pygame.draw.circle(screen, (0, 0, 0), (cx, cy+1), r)
    pygame.draw.rect(screen, (0, 0, 0), (cx-r+2, cy-r-2, r*2-4, 4))
    pygame.draw.line(screen, (255, 200, 0), (cx, cy-r-2), (cx+r, cy-r-6), 2)

# Vẽ hình lá cờ màu đỏ trên ô chưa mở.
def draw_flag(screen, rect):
    draw_3d_cell(screen, rect)
    cx, cy = rect.center
    w = rect.w
    h = rect.h
    pygame.draw.line(screen, (0, 0, 0), (cx-w//8, cy-h//4), (cx-w//8, cy+h//4), 2)
    pygame.draw.polygon(screen, C.FLAG_COLOR, [
        (cx-w//8, cy-h//4), (cx+w//4, cy-h//8), (cx-w//8, cy)
    ])

# Vẽ khung dạng thẻ (card) với viền tiêu đề có màu tùy chỉnh.
def draw_card(screen, rect, title, font_title, top_color):
    pygame.draw.rect(screen, C.CARD_BG, rect, border_radius=6)
    pygame.draw.lines(screen, top_color, False, [
        (rect.left+6, rect.top), (rect.right-6, rect.top)
    ], width=4)
    pygame.draw.circle(screen, top_color, (rect.left+6, rect.top+2), 2)
    pygame.draw.circle(screen, top_color, (rect.right-6, rect.top+2), 2)
    
    ts = font_title.render(title, True, C.TEXT_WHITE)
    screen.blit(ts, (rect.x + 15, rect.y + 15))

# Vẽ thanh tiến trình tiến độ chạy thuật toán.
def draw_progress_bar(screen, rect, progress):
    pygame.draw.rect(screen, C.PROGRESS_TRACK, rect, border_radius=4)
    if progress > 0:
        w = max(4, int(rect.w * progress))
        pygame.draw.rect(screen, C.PROGRESS_FILL, (rect.x, rect.y, w, rect.h), border_radius=4)

# Tách văn bản dài thành các dòng ngắn hơn dựa trên chiều rộng giới hạn.
def wrap_text(text, max_width, font):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        fw, fh = font.size(' '.join(current_line))
        if fw > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines
