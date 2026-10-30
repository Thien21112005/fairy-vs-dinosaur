import pygame


class GameStatesMixin:
    """Xử lý một khung hình theo trạng thái hiện tại: mỗi trạng thái tự cập nhật và tự vẽ."""

    def _run_frame(self, dt, delta_time):
        if self.pause_menu.visible:
            self._frame_paused()
        elif self.countdown_active:
            self._frame_countdown(delta_time)
        elif self.ui.game_over.visible:
            self._frame_game_over()
        elif self.level_anim.active:
            self._frame_level_anim(dt)
        elif self.show_level_complete:
            self._frame_level_complete()
        else:
            self._update_just_reset(dt)
            if self.dying:
                self._frame_dying(dt)
            else:
                self._frame_playing(dt, delta_time)

    def _frame_paused(self):
        self.handle_events()
        mouse_pos = pygame.mouse.get_pos()
        self.pause_menu.update_hover(mouse_pos)
        self.ui.update_hover(mouse_pos)
        self.draw_game_screen()

    def _frame_countdown(self, delta_time):
        self.countdown_timer -= delta_time
        count = int(self.countdown_timer + 1)  # Hiển thị 3, 2, 1

        if count != self.last_count and count > 0:
            self.sound_manager.play_count_down()
            self.last_count = count

        self._draw_countdown_frame(count)

        if self.countdown_timer <= 0:
            self.countdown_active = False
            self.last_count = 0
            if self.game_started and not self.dying:
                self.sound_manager.play_ghost_move()
                if self.mode_manager.frightened_active:
                    self.sound_manager.play_power(loops=-1)
            if self.sound_manager.intro_channel.get_busy():
                self.sound_manager.unpause_intro()
            self.sound_manager.unpause_turn_egg()
        self.handle_events()

    def _frame_game_over(self):
        self.ui.game_over.update(pygame.mouse.get_pos())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                self.ui.game_over.handle_event(event)

        self._draw_compact_scene()
        self.ui.game_over.draw()
        pygame.display.flip()

    def _frame_level_anim(self, dt):
        self.level_anim.update(dt)
        self.handle_events()
        self._draw_level_anim_frame()

    def _frame_level_complete(self):
        self.level_menu.update_hover(pygame.mouse.get_pos())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            self.level_menu.handle_events(event)

        self._draw_compact_scene()
        self.level_menu.draw(self.screen)
        pygame.display.flip()

    def _update_just_reset(self, dt):
        if self.just_reset:
            self.reset_timer += dt
            if self.reset_timer >= self.reset_delay:
                self.just_reset = False
                if not self.hint_restored and self.saved_hint_state:
                    self.show_hint = True
                    self.hint_restored = True

    def _frame_dying(self, dt):
        self.death_animation_time += dt
        self.fade_alpha = min(255, int(255 * (self.death_animation_time / self.death_animation_duration)))

        for ghost in self.ghosts:
            if ghost.eating:
                ghost.eat_animation_time += dt

        if self.death_animation_time >= self.death_animation_duration:
            self.dying = False
            self.fade_alpha = 0
            self.lives -= 1

            if self.lives <= 0:
                self.game_over = True
                self.ui.game_over.show()
                self.sound_manager.play_game_over()
                self.solve_locked = False
                self.record_game_history(success=False)
            else:
                self.reset_after_death()

        self.handle_events()
        self._draw_dying_frame()

    def _frame_playing(self, dt, delta_time):
        self._update_ready(dt)

        if self.game_started:
            self.play_time += dt
        self.mode_manager.update(delta_time)

        self.handle_events()
        mouse_pos = pygame.mouse.get_pos()
        self.ui.update_hover(mouse_pos)
        self.pause_menu.update_hover(mouse_pos)

        # Chỉ cập nhật khi đã chọn AI hoặc đã bấm phím chơi thủ công
        if not self.dying and self.game_started and (self.ai_mode or self.manual_mode):
            self.player.update(dt)
            for ghost in self.visible_ghosts():
                ghost.update(dt)
            self.check_ghost_collisions()
            if self.level.remaining_pellets <= 0 and not self.dying and not self.game_over:
                self.record_game_history(success=True)  # Trước khi animation tăng số màn
                self.level_anim.start()
                return

        if self.score > self.high_score:
            self.high_score = self.score

        self._draw_playing_frame(dt)

    def _update_ready(self, dt):
        if self.show_ready:
            if not self.intro_played:
                self.sound_manager.play_intro()
                self.intro_played = True
            self.ready_timer -= dt
            if self.ready_timer <= 0:
                self.show_ready = False
                self.game_started = True
                self.sound_manager.play_ghost_move()
