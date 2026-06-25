# pyrefly: ignore [missing-import]
import pygame
from config.settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, SIDEBAR_W, BOTTOM_PANEL_H, TOOLBAR_H,
    C, NUMBER_COLORS, CATEGORIES, ALGORITHM_LIST,
    STATE_SETUP, STATE_RUNNING, STATE_PAUSED, STATE_FINISHED,
    STATE_COMPARING, STATE_COMPARE_RUNNING,
    GRID_PADDING, CELL_MARGIN, MIN_CELL_SIZE, MAX_CELL_SIZE
)
from .helpers import (
    draw_input_box, draw_toolbar_btn, draw_3d_cell, draw_revealed_cell,
    draw_mine, draw_flag, draw_card, draw_progress_bar, wrap_text
)

# Quản lý vẽ tất cả các thành phần giao diện của ứng dụng.
class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self._init_fonts()
        self._load_icons()

    # Tải các icon dạng PNG từ thư mục assets/icons.
    def _load_icons(self):
        self.icons = {}
        import os
        icon_dir = "assets/icons"
        if os.path.exists(icon_dir):
            for file in os.listdir(icon_dir):
                if file.endswith('.png'):
                    name = file[:-4]
                    try:
                        img = pygame.image.load(os.path.join(icon_dir, file)).convert_alpha()

                        self.icons[name] = pygame.transform.smoothscale(img, (16, 16))
                    except:
                        pass

    # Khởi tạo các font chữ cho tiêu đề, văn bản và ô số.
    def _init_fonts(self):
        try:
            self.f_logo = pygame.font.SysFont("segoeui", 22, bold=True)
            self.f_title = pygame.font.SysFont("segoeui", 16, bold=True)
            self.f_head = pygame.font.SysFont("segoeui", 14, bold=True)
            self.f_body = pygame.font.SysFont("segoeui", 13)
            self.f_small = pygame.font.SysFont("segoeui", 12)
            self.f_tiny = pygame.font.SysFont("segoeui", 10)
            self.f_cell = pygame.font.SysFont("segoeui", 16, bold=True)
        except:
            self.f_logo = pygame.font.Font(None, 26)
            self.f_title = pygame.font.Font(None, 20)
            self.f_head = pygame.font.Font(None, 16)
            self.f_body = pygame.font.Font(None, 15)
            self.f_small = pygame.font.Font(None, 14)
            self.f_tiny = pygame.font.Font(None, 12)
            self.f_cell = pygame.font.Font(None, 20)

    def draw_background(self):
        self.screen.fill(C.BG_BOARD)


    # Vẽ bảng điều khiển bên trái chứa các thông số cấu hình và danh sách thuật toán.
    def draw_sidebar(self, selected_algo, settings, active_input, input_text, collapsed_categories):
        sw = SIDEBAR_W
        sh = WINDOW_HEIGHT
        
        sidebar_r = pygame.Rect(0, 0, sw, sh)
        pygame.draw.rect(self.screen, C.BG_SIDEBAR, sidebar_r)
        
        y = 20
        pygame.draw.circle(self.screen, (239, 68, 68), (30, y+10), 3)
        
        logo_ts = self.f_logo.render("SMART SWEEPER", True, C.TEXT_WHITE)
        self.screen.blit(logo_ts, (50, y))
        y += 40
        

        y += 20
        iw = (sw - 50) // 2
        

        ls_rows = self.f_small.render("Số hàng", True, C.TEXT_MUTED)
        ls_cols = self.f_small.render("Số cột", True, C.TEXT_MUTED)
        self.screen.blit(ls_rows, (20, y))
        self.screen.blit(ls_cols, (20 + iw + 10, y))
        y += 25
        
        r_rows = pygame.Rect(20, y, iw, 32)
        r_cols = pygame.Rect(20 + iw + 10, y, iw, 32)
        
        p_rows, m_rows = draw_input_box(self.screen, r_rows, self.f_body, 
            input_text if active_input == 'rows' else str(settings['rows']), active_input == 'rows')
        p_cols, m_cols = draw_input_box(self.screen, r_cols, self.f_body, 
            input_text if active_input == 'cols' else str(settings['cols']), active_input == 'cols')
            
        y += 45
        

        ls_mines = self.f_small.render("Số bom", True, C.TEXT_MUTED)
        ls_speed = self.f_small.render("Tốc độ", True, C.TEXT_MUTED)
        self.screen.blit(ls_mines, (20, y))
        self.screen.blit(ls_speed, (20 + iw + 10, y))
        y += 25
        
        r_mines = pygame.Rect(20, y, iw, 32)
        r_speed = pygame.Rect(20 + iw + 10, y, iw, 32)
        
        p_mines, m_mines = draw_input_box(self.screen, r_mines, self.f_body, 
            input_text if active_input == 'mines' else str(settings['mines']), active_input == 'mines')
        p_speed, m_speed = draw_input_box(self.screen, r_speed, self.f_body, 
            input_text if active_input == 'speed' else str(settings.get('speed', 5)), active_input == 'speed')
            
        max_mines = settings['rows'] * settings['cols'] - 9
        if max_mines < 1: max_mines = 1
        
        setting_rects = {
            'rows': {'val_rect': r_rows, 'plus': p_rows, 'minus': m_rows, 'value': settings['rows'], 'min': 5, 'max': 40},
            'cols': {'val_rect': r_cols, 'plus': p_cols, 'minus': m_cols, 'value': settings['cols'], 'min': 5, 'max': 40},
            'mines': {'val_rect': r_mines, 'plus': p_mines, 'minus': m_mines, 'value': settings['mines'], 'min': 1, 'max': max_mines},
            'speed': {'val_rect': r_speed, 'plus': p_speed, 'minus': m_speed, 'value': settings.get('speed', 5), 'min': 1, 'max': 10},
        }
        
        y += 40
        pygame.draw.line(self.screen, (55, 65, 81), (20, y), (sw-20, y))
        y += 15
        

        algo_rects = {}
        cat_rects = {}
        current_cat = -1
        
        for i, (name, cat_idx, key) in enumerate(ALGORITHM_LIST):
            if cat_idx != current_cat:
                current_cat = cat_idx
                cat = CATEGORIES[cat_idx]
                
                cat_rect = pygame.Rect(0, y, sw, 28)
                cat_rects[cat_idx] = cat_rect
                
                hdr = self.f_body.render(cat['name'], True, C.TEXT_WHITE)
                self.screen.blit(hdr, (20, y))

                is_collapsed = cat_idx in collapsed_categories
                icon_key = 'chevron_down' if is_collapsed else 'chevron_up'
                icon = self.icons.get(icon_key)
                if icon:
                    self.screen.blit(icon, (sw - 30, y + 6))
                else:
                    chev_char = "v" if is_collapsed else "^"
                    chev = self.f_small.render(chev_char, True, C.TEXT_WHITE)
                    self.screen.blit(chev, (sw - 30, y+4))
                y += 28
                
            if cat_idx in collapsed_categories:
                continue
                
            br = pygame.Rect(0, y, sw, 28)
            algo_rects[i] = br
            is_sel = (i == selected_algo)
            
            if is_sel:
                pygame.draw.rect(self.screen, (55, 65, 81), br)
                pygame.draw.rect(self.screen, C.BTN_BLUE, (0, y, 4, 28))
                ts = self.f_body.render(name, True, C.TEXT_WHITE)
            else:
                ts = self.f_body.render(name, True, C.TEXT_MUTED)
                
            self.screen.blit(ts, (35, y + (br.h - ts.get_height()) // 2))
            y += 28
            
        return algo_rects, setting_rects, cat_rects


    # Vẽ thanh công cụ phía trên chứa các nút điều khiển game.
    def draw_toolbar(self, app_state, has_board):
        btn_rects = {}
        btn_h = 32
        btn_y = 15
        bx = SIDEBAR_W + 20
        

        r = pygame.Rect(bx, btn_y, 100, btn_h)
        draw_toolbar_btn(self.screen, r, "Tạo bảng", self.f_body, C.BTN_BLUE, True, self.icons.get('plus'))
        btn_rects['create'] = r
        bx += 110
        

        bx = WINDOW_WIDTH - 20
        
        bx -= 180
        r = pygame.Rect(bx, btn_y, 180, btn_h)
        draw_toolbar_btn(self.screen, r, "So sánh tất cả", self.f_body, C.BTN_GRAY, has_board, self.icons.get('compare'))
        btn_rects['compare'] = r
        bx -= 10
        
        bx -= 90
        r = pygame.Rect(bx, btn_y, 90, btn_h)
        draw_toolbar_btn(self.screen, r, "Đặt lại", self.f_body, C.BTN_GRAY, has_board, self.icons.get('reset'))
        btn_rects['reset'] = r
        bx -= 10
        
        bx -= 80
        r = pygame.Rect(bx, btn_y, 80, btn_h)
        draw_toolbar_btn(self.screen, r, "Bước", self.f_body, C.BTN_GRAY, has_board and app_state != STATE_RUNNING, self.icons.get('step'))
        btn_rects['step'] = r
        bx -= 10
        
        bx -= 80
        r = pygame.Rect(bx, btn_y, 80, btn_h)
        if app_state == STATE_RUNNING:
            draw_toolbar_btn(self.screen, r, "Dừng", self.f_body, C.BTN_BLUE, True, self.icons.get('pause'))
            btn_rects['pause'] = r
        else:
            label = "Chạy" if app_state != STATE_PAUSED else "Tiếp"
            draw_toolbar_btn(self.screen, r, label, self.f_body, C.BTN_BLUE, has_board, self.icons.get('play'))
            btn_rects['play'] = r
            
        return btn_rects


    # Vẽ bảng thông tin bên dưới hiển thị hiệu suất và kết quả chạy của thuật toán.
    def draw_bottom_panel(self, algo_info, metrics, app_state, step_index, total_steps, comp_results=None):
        px = SIDEBAR_W
        py = WINDOW_HEIGHT - BOTTOM_PANEL_H
        pw = WINDOW_WIDTH - px
        ph = BOTTOM_PANEL_H
        
        gap = 15
        card_w = (pw - 40 - gap * 3) // 4
        card_h = ph - 20
        cy = py + 5
        cx = px + 20
        

        c1 = pygame.Rect(cx, cy, card_w, card_h)
        title_c1 = algo_info['name'] if algo_info else "Thông tin thuật toán"
        draw_card(self.screen, c1, title_c1, self.f_head, C.CARD_BORDER_ORANGE)
        if algo_info and algo_info.get('description'):
            lines = wrap_text(algo_info['description'], card_w - 30, self.f_small)
            ly = c1.y + 45
            for line in lines[:4]:
                ls = self.f_small.render(line, True, C.TEXT_MUTED)
                self.screen.blit(ls, (c1.x + 15, ly))
                ly += 18
        cx += card_w + gap
        

        c2 = pygame.Rect(cx, cy, card_w, card_h)
        draw_card(self.screen, c2, "Hiệu suất", self.f_head, C.CARD_BORDER_BLUE)
        
        ty = c2.y + 45
        if metrics:
            stats_2 = [
                ("Thời gian (ms)", f"{metrics.get('time_ms', 0):.2f}"),
                ("Số bước", str(metrics.get('total_steps', 0))),
                ("Số node đã duyệt", str(metrics.get('nodes_explored', 0))),
            ]
            for label, val in stats_2:
                ls = self.f_body.render(label, True, C.TEXT_MUTED)
                vs = self.f_body.render(val, True, C.TEXT_WHITE)
                self.screen.blit(ls, (c2.x + 15, ty))
                self.screen.blit(vs, (c2.right - 15 - vs.get_width(), ty))
                ty += 28
        else:
            ls = self.f_body.render("Chưa có dữ liệu", True, C.TEXT_MUTED)
            self.screen.blit(ls, (c2.x + 15, ty))
            
        cx += card_w + gap
        
        c3 = pygame.Rect(cx, cy, card_w, card_h)
        draw_card(self.screen, c3, "Kết quả", self.f_head, C.CARD_BORDER_GREEN)
        
        ty3 = c3.y + 45
        if metrics:
            status = "Hoàn thành xuất sắc" if metrics.get('success') else ("Hoàn thành (Chạm mìn)" if metrics.get('completed') else "Đang chạy...")
            stats_3 = [
                ("Trạng thái", status),
                ("Ô an toàn đã mở", str(metrics.get('cells_revealed', 0))),
                ("Mìn đã chạm", str(metrics.get('mines_hit', 0))),
            ]
            for label, val in stats_3:
                ls = self.f_body.render(label, True, C.TEXT_MUTED)
                

                if label == "Trạng thái":
                    color = C.CARD_BORDER_GREEN if "xuất sắc" in val else (C.CARD_BORDER_ORANGE if "mìn" in val else C.TEXT_WHITE)
                elif label == "Mìn đã chạm" and metrics.get('mines_hit', 0) > 0:
                    color = C.MINE_BG
                else:
                    color = C.TEXT_WHITE
                    
                vs = self.f_body.render(val, True, color)
                self.screen.blit(ls, (c3.x + 15, ty3))
                self.screen.blit(vs, (c3.right - 15 - vs.get_width(), ty3))
                ty3 += 28
        else:
            ls = self.f_body.render("Chưa có dữ liệu", True, C.TEXT_MUTED)
            self.screen.blit(ls, (c3.x + 15, ty3))
            
        cx += card_w + gap
        
        c4 = pygame.Rect(cx, cy, card_w, card_h)
        draw_card(self.screen, c4, "Hoàn thành", self.f_head, C.CARD_BORDER_BLUE)
        
        if total_steps > 0:
            progress = step_index / max(1, total_steps)
        else:
            progress = 0
            
        bar_w = card_w - 30
        pct_str = f"{progress*100:.0f}%"
        ps = self.f_small.render(pct_str, True, C.TEXT_WHITE)
        self.screen.blit(ps, (c4.x + card_w - 15 - ps.get_width(), c4.y + 40))
        
        draw_progress_bar(self.screen, pygame.Rect(c4.x + 15, c4.y + 60, bar_w, 8), progress)


    # Vẽ bảng xếp hạng so sánh hiệu suất giữa các thuật toán.
    def draw_leaderboard(self, comp_results):
        ax = SIDEBAR_W + GRID_PADDING
        ay = TOOLBAR_H + GRID_PADDING
        aw = WINDOW_WIDTH - SIDEBAR_W - GRID_PADDING * 2
        ah = WINDOW_HEIGHT - TOOLBAR_H - BOTTOM_PANEL_H - GRID_PADDING * 2
        

        pygame.draw.rect(self.screen, (45, 55, 72), (ax, ay, aw, ah), border_radius=12)
        pygame.draw.rect(self.screen, (75, 85, 99), (ax, ay, aw, ah), width=2, border_radius=12)
        

        ts = self.f_head.render("BẢNG XẾP HẠNG THUẬT TOÁN (LEADERBOARD)", True, C.TEXT_WHITE)
        self.screen.blit(ts, (ax + 30, ay + 20))
        
        close_rect = pygame.Rect(ax + aw - 40, ay + 15, 24, 24)
        pygame.draw.rect(self.screen, C.MINE_BG, close_rect, border_radius=4)
        x_ts = self.f_head.render("X", True, C.TEXT_WHITE)
        self.screen.blit(x_ts, (close_rect.x + (close_rect.w - x_ts.get_width()) // 2, close_rect.y + (close_rect.h - x_ts.get_height()) // 2 + 1))
        

        hy = ay + 70
        pygame.draw.rect(self.screen, (55, 65, 81), (ax + 20, hy, aw - 40, 36), border_top_left_radius=6, border_top_right_radius=6)
        
        headers = ["Hạng", "Tên Thuật Toán", "Kết Quả", "Ô An Toàn", "Mìn Chạm", "TG (ms)", "Số Bước", "Nodes"]
        col_w = [(aw - 40) * 0.08, (aw - 40) * 0.22, (aw - 40) * 0.15, (aw - 40) * 0.12, (aw - 40) * 0.1, (aw - 40) * 0.11, (aw - 40) * 0.11, (aw - 40) * 0.11]
        
        cx = ax + 20
        for i, h in enumerate(headers):

            hs = self.f_body.render(h, True, (209, 213, 219))
            self.screen.blit(hs, (cx + 10, hy + 8))
            cx += col_w[i]
            

        sorted_res = sorted(comp_results, key=lambda x: (
            -int(x['metrics'].get('success', False)),
            -x['metrics'].get('cells_revealed', 0),
            x['metrics'].get('mines_hit', 9999),
            x['metrics'].get('time_ms', 999999)
        ))
        
        ry = hy + 36
        for idx, res in enumerate(sorted_res):

            row_bg = (60, 70, 88) if idx % 2 == 1 else (45, 55, 72)
            

            if idx == len(sorted_res) - 1:
                pygame.draw.rect(self.screen, row_bg, (ax + 20, ry, aw - 40, 30), border_bottom_left_radius=6, border_bottom_right_radius=6)
            else:
                pygame.draw.rect(self.screen, row_bg, (ax + 20, ry, aw - 40, 30))
            
            m = res['metrics']
            success_str = "Thành công" if m.get('success') else ("Có chạm mìn" if m.get('completed') else "Thất bại")
            color_success = (52, 211, 153) if m.get('success') else ((251, 146, 60) if m.get('completed') else C.TEXT_WHITE)
            
            data = [
                f"#{idx+1}",
                res['name'],
                success_str,
                str(m.get('cells_revealed', 0)),
                str(m.get('mines_hit', 0)),
                f"{m.get('time_ms', 0):.1f}",
                str(m.get('total_steps', 0)),
                str(m.get('nodes_explored', 0))
            ]
            
            cx = ax + 20
            for j, d in enumerate(data):
                color = C.TEXT_WHITE
                if j == 0: color = (156, 163, 175)
                elif j == 1: color = (96, 165, 250)
                elif j == 2: color = color_success
                elif j == 4 and m.get('mines_hit', 0) > 0: color = (248, 113, 113)
                
                ds = self.f_body.render(d, True, color)
                self.screen.blit(ds, (cx + 10, ry + 5))
                cx += col_w[j]
                
            ry += 30
        return close_rect

    # Tính toán kích thước ô và khoảng cách căn lề để vẽ lưới game cân đối ở giữa màn hình.
    def calculate_grid_layout(self, rows, cols):
        ax = SIDEBAR_W + GRID_PADDING
        ay = TOOLBAR_H + GRID_PADDING
        aw = WINDOW_WIDTH - SIDEBAR_W - GRID_PADDING * 2
        ah = WINDOW_HEIGHT - TOOLBAR_H - BOTTOM_PANEL_H - GRID_PADDING * 2

        cw = (aw - (cols + 1) * CELL_MARGIN) // max(cols, 1)
        ch = (ah - (rows + 1) * CELL_MARGIN) // max(rows, 1)
        cs = max(MIN_CELL_SIZE, min(cw, ch, MAX_CELL_SIZE))

        gw = cols * (cs + CELL_MARGIN)
        gh = rows * (cs + CELL_MARGIN)
        
        ox = ax + (aw - gw) // 2
        oy = ay + (ah - gh) // 2
        
        return cs, ox, oy

    def draw_loading_comparison(self, done, total):
        ax = SIDEBAR_W + GRID_PADDING
        ay = TOOLBAR_H + GRID_PADDING
        aw = WINDOW_WIDTH - SIDEBAR_W - GRID_PADDING * 2
        ah = WINDOW_HEIGHT - TOOLBAR_H - BOTTOM_PANEL_H - GRID_PADDING * 2
        

        pygame.draw.rect(self.screen, (45, 55, 72), (ax, ay, aw, ah), border_radius=12)
        pygame.draw.rect(self.screen, (75, 85, 99), (ax, ay, aw, ah), width=2, border_radius=12)
        
        ts = self.f_head.render("ĐANG TIẾN HÀNH SO SÁNH...", True, C.TEXT_WHITE)
        cx = ax + (aw - ts.get_width()) // 2
        cy = ay + ah // 2 - 20
        self.screen.blit(ts, (cx, cy))
        
        pct = done / max(total, 1)
        sub_ts = self.f_body.render(f"Đã hoàn thành {done}/{total} thuật toán ({int(pct*100)}%)", True, C.TEXT_MUTED)
        self.screen.blit(sub_ts, (ax + (aw - sub_ts.get_width()) // 2, cy + 30))
        
        bar_w = aw // 2
        r = pygame.Rect(ax + (aw - bar_w) // 2, cy + 60, bar_w, 10)
        draw_progress_bar(self.screen, r, pct)

    # Vẽ lưới các ô của bảng game Minesweeper.
    def draw_board(self, board, cell_size, gx, gy):
        if board is None:
            t = self.f_title.render("NHẤN '+ TẠO BẢNG' ĐỂ BẮT ĐẦU", True, C.TEXT_MUTED)
            cx = SIDEBAR_W + (WINDOW_WIDTH - SIDEBAR_W)//2 - t.get_width()//2
            cy = TOOLBAR_H + (WINDOW_HEIGHT - TOOLBAR_H - BOTTOM_PANEL_H)//2 - t.get_height()//2
            self.screen.blit(t, (cx, cy))
            return

        for r in range(board.rows):
            for c in range(board.cols):
                cx = gx + c * (cell_size + CELL_MARGIN)
                cy = gy + r * (cell_size + CELL_MARGIN)
                cr = pygame.Rect(cx, cy, cell_size, cell_size)

                if board.is_revealed(r, c):
                    if board.is_mine(r, c):
                        draw_mine(self.screen, cr)
                    else:
                        num = board.numbers.get((r, c), 0)
                        draw_revealed_cell(self.screen, cr)
                        if num > 0:
                            fc = NUMBER_COLORS.get(num, C.TEXT_WHITE)
                            ns = self.f_cell.render(str(num), True, fc)
                            self.screen.blit(ns, (cr.x + (cr.w - ns.get_width()) // 2,
                                                  cr.y + (cr.h - ns.get_height()) // 2))
                elif board.is_flagged(r, c):
                    draw_flag(self.screen, cr)
                else:
                    draw_3d_cell(self.screen, cr)
