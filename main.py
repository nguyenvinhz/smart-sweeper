import os
import sys

# Hide Pygame greeting
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# pyrefly: ignore [missing-import]
import pygame
import time

from config.settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    STATE_SETUP, STATE_RUNNING, STATE_PAUSED, STATE_FINISHED,
    STATE_COMPARING, STATE_COMPARE_RUNNING,
    ALGORITHM_LIST
)
from ui.renderer import Renderer
from core.board import Board
from algorithms import create_algorithm

class App:
    def __init__(self):
        pygame.init()
        # Enable high DPI on Windows for sharper text
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        
        self.running = True
        self.state = STATE_SETUP

        self.settings = {
            'rows': 15,
            'cols': 15,
            'mines': 20,
            'speed': 5,
        }
        
        self.active_input = None
        self.input_text = ""
        self.selected_algo = 0
        self.collapsed_categories = set()
        
        self.board = None
        self.replay_board = None
        
        self.current_algorithm = None
        self.algo_steps = []
        self.step_index = 0
        self.step_timer = 0.0
        self.anim_timer = 0.0
        self.algo_metrics = None
        self.algo_info = None
        
        self.comparison_results = []
        

        self.algo_rects = {}
        self.setting_rects = {}
        self.btn_rects = {}
        self.cat_rects = {}

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                self._handle_typing(event)

    def _handle_click(self, pos):
        if self.state == STATE_COMPARING and getattr(self, 'close_comp_rect', None):
            if self.close_comp_rect.collidepoint(pos):
                self.state = getattr(self, 'pre_compare_state', STATE_SETUP)
                return


        clicked_input = False
        for key, rects in self.setting_rects.items():
            if rects['plus'].collidepoint(pos):
                self._commit_input()
                self._adjust_setting(key, 1)
                return
            if rects['minus'].collidepoint(pos):
                self._commit_input()
                self._adjust_setting(key, -1)
                return
            if rects['val_rect'].collidepoint(pos):
                if self.active_input != key:
                    if self.active_input is not None:
                        self._commit_input()
                    self.active_input = key
                    self.input_text = str(self.settings[key])
                clicked_input = True
                return

        if not clicked_input and self.active_input is not None:
            self._commit_input()


        for cat_idx, rect in self.cat_rects.items():
            if rect.collidepoint(pos):
                if cat_idx in self.collapsed_categories:
                    self.collapsed_categories.remove(cat_idx)
                else:
                    self.collapsed_categories.add(cat_idx)
                return


        for i, rect in self.algo_rects.items():
            if rect.collidepoint(pos):
                self.selected_algo = i
                return


        for btn_key, rect in self.btn_rects.items():
            if rect.collidepoint(pos):
                self._handle_button(btn_key)
                return

    def _handle_button(self, btn_key):
        if btn_key == 'create':
            self._create_board()
        elif btn_key == 'play':
            if self.state == STATE_PAUSED:
                self.state = STATE_RUNNING
            else:
                self._start_algorithm()
        elif btn_key == 'pause':
            self.state = STATE_PAUSED
        elif btn_key == 'step':
            if self.board:
                if not self.algo_steps:
                    self._start_algorithm()
                    self.state = STATE_PAUSED
                if self.step_index < len(self.algo_steps):
                    self._advance_step()
        elif btn_key == 'reset':
            self._reset()
        elif btn_key == 'compare':
            self._run_comparison()

    def _handle_typing(self, event):
        if self.active_input is None:
            return
            
        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            self._commit_input()
        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        else:

            char = ""
            if event.unicode and event.unicode.isdigit():
                char = event.unicode
            elif pygame.K_0 <= event.key <= pygame.K_9:
                char = chr(event.key)
            elif pygame.K_KP0 <= event.key <= pygame.K_KP9:
                char = chr(event.key - pygame.K_KP0 + ord('0'))
                
            if char:
                self.input_text += char
                if len(self.input_text) > 4:
                    self.input_text = self.input_text[:4]

    def _commit_input(self):
        if self.active_input and self.input_text:
            val = int(self.input_text)
            limits = self.setting_rects[self.active_input]
            val = max(limits['min'], min(val, limits['max']))
            self.settings[self.active_input] = val
            
            # Revalidate mines if rows/cols changed
            max_mines = self.settings['rows'] * self.settings['cols'] - 9
            if max_mines < 1: max_mines = 1
            if self.settings['mines'] > max_mines:
                self.settings['mines'] = max_mines
                
        self.active_input = None
        self.input_text = ""

    def _adjust_setting(self, key, delta):
        limits = self.setting_rects[key]
        val = self.settings[key] + delta
        val = max(limits['min'], min(val, limits['max']))
        self.settings[key] = val
        self._commit_input()

    def _create_board(self):
        self.board = Board(
            self.settings['rows'],
            self.settings['cols'],
            self.settings['mines']
        )
        self.board.place_mines(safe_row=self.settings['rows']//2, safe_col=self.settings['cols']//2)
        self._reset()

    def _reset(self):
        self.state = STATE_SETUP
        self.step_index = 0
        self.algo_steps = []
        self.algo_metrics = None
        self.comparison_results = []
        if self.board:
            self.replay_board = self.board.copy()
            self.replay_board.reset()

    def _start_algorithm(self):
        if not self.board: return
        algo_name, cat_idx, algo_key = ALGORITHM_LIST[self.selected_algo]
        algo = create_algorithm(algo_key, self.board)
        if not algo: return
        
        algo.solve()
        self.algo_steps = algo.get_steps()
        self.algo_metrics = algo.get_metrics()
        self.algo_info = {
            'name': algo_name,
            'description': algo.description
        }
        
        self.replay_board = self.board.copy()
        self.replay_board.reset()
        self.step_index = 0
        self.step_timer = 0.0
        self.anim_timer = 0.0
        self.state = STATE_RUNNING

    def _run_comparison(self):
        if not self.board: return

        self.board_copy = self.board.copy()
        self.board_copy.reset()
        
        self.pre_compare_state = self.state
        if self.state == STATE_RUNNING:
            self.pre_compare_state = STATE_PAUSED
            
        self.comparison_results = []
        self.compare_queue = list(ALGORITHM_LIST)
        self.state = STATE_COMPARE_RUNNING

    def _update(self, dt):
        if self.state == STATE_COMPARE_RUNNING:
            if hasattr(self, 'compare_queue') and self.compare_queue:
                algo_name, cat_idx, algo_key = self.compare_queue.pop(0)
                try:
                    algo = create_algorithm(algo_key, self.board_copy.copy())
                    if algo:
                        algo.solve()
                        self.comparison_results.append({
                            'name': algo_name,
                            'metrics': algo.get_metrics()
                        })
                except Exception:
                    pass
            else:
                self.state = STATE_COMPARING

        elif self.state == STATE_RUNNING:
            self.anim_timer += dt * 1000
            
            speed_val = self.settings.get('speed', 5)
            delay = 50
            steps_per_tick = 1
            if speed_val == 1: delay = 500
            elif speed_val == 2: delay = 250
            elif speed_val == 3: delay = 100
            elif speed_val == 4: delay = 50
            elif speed_val == 5: delay = 25
            elif speed_val == 6: delay = 10
            elif speed_val == 7: delay = 5
            elif speed_val == 8: delay = 0; steps_per_tick = 1
            elif speed_val == 9: delay = 0; steps_per_tick = 5
            elif speed_val == 10: delay = 0; steps_per_tick = 20
            
            if delay > 0:
                while self.anim_timer >= delay and self.step_index < len(self.algo_steps):
                    self.anim_timer -= delay
                    self._advance_step()
            else:
                self.anim_timer = 0
                for _ in range(steps_per_tick):
                    self._advance_step()
            
            if self.step_index >= len(self.algo_steps):
                self.state = STATE_FINISHED

    def _advance_step(self):
        if self.step_index >= len(self.algo_steps): return
        step = self.algo_steps[self.step_index]
        if step['action'] == 'reveal':
            self.replay_board.reveal(step['row'], step['col'])
        elif step['action'] == 'flag':

            if hasattr(self.replay_board, 'toggle_flag'):
                if not self.replay_board.is_flagged(step['row'], step['col']):
                    self.replay_board.toggle_flag(step['row'], step['col'])
            else:
                self.replay_board.flag(step['row'], step['col'])
        self.step_index += 1

    def _draw(self):
        self.renderer.draw_background()
        

        sidebar_data = self.renderer.draw_sidebar(
            self.selected_algo, self.settings, self.active_input, self.input_text, self.collapsed_categories
        )
        self.algo_rects = sidebar_data[0]
        self.setting_rects = sidebar_data[1]
        self.cat_rects = sidebar_data[2]
        

        self.btn_rects = self.renderer.draw_toolbar(self.state, self.board is not None)
        

        self.renderer.draw_bottom_panel(
            self.algo_info,
            self.algo_metrics,
            self.state,
            self.step_index,
            len(self.algo_steps) if self.algo_steps else 0,
            self.comparison_results
        )
        

        self.close_comp_rect = None
        if self.state == STATE_COMPARING and self.comparison_results:
            self.close_comp_rect = self.renderer.draw_leaderboard(self.comparison_results)
        elif self.state == STATE_COMPARE_RUNNING:
            done = len(ALGORITHM_LIST) - len(getattr(self, 'compare_queue', []))
            self.renderer.draw_loading_comparison(done, len(ALGORITHM_LIST))
        else:
            draw_board = self.replay_board if self.replay_board else self.board
            if draw_board:
                cs, gx, gy = self.renderer.calculate_grid_layout(draw_board.rows, draw_board.cols)
                self.renderer.draw_board(draw_board, cs, gx, gy)
            else:
                self.renderer.draw_board(None, 0, 0, 0)
            
        pygame.display.flip()

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
