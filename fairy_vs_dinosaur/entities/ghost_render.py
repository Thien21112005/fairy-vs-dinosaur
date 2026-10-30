import pygame

from fairy_vs_dinosaur.entities.path_drawing import blit_wrapped, draw_arrow_head, LINE_WIDTH


class GhostRenderMixin:
    """Chọn hình theo trạng thái và vẽ đường đi của ghost."""

    def _base_animations(self):
        """Bộ hình khi đi bình thường. Blinky thay bằng bộ Elroy khi còn ít pellet."""
        return self.normal_animations

    def _current_image(self):
        if self.hatching:
            index = int((self.hatch_animation_time / self.hatch_animation_duration) * len(self.hatchegg_frames))
            return self.hatchegg_frames[min(index, len(self.hatchegg_frames) - 1)]
        if self.returning_home:
            return self.turnegg_frames[int(self.time / self.animation_speed) % len(self.turnegg_frames)]
        if self.eaten:
            frames = self.hurt_animations[self.direction]
            index = int((self.eaten_animation_time / self.eaten_animation_duration) * len(frames))
            return frames[min(index, len(frames) - 1)]
        if self.eating and self.game.dying:
            frames = self.eat_animations[self.direction]
            return frames[int((self.eat_animation_time / self.eat_animation_duration) * len(frames) * 3) % len(frames)]
        if self.game.show_ready or self.release_timer > 0:
            return self.relax_frames[int(self.time / self.animation_speed) % len(self.relax_frames)]

        if self._frightened_active():
            about_to_end = self.game.mode_manager.frightened_timer * 1000 < self.flash_start_time
            if about_to_end and int(self.time / self.flash_interval) % 2 != 0:
                return self.flash_animations[self.direction][0]
            frames = self.frightened_animations[self.direction]
        else:
            frames = self._base_animations()[self.direction]
        return frames[int(self.time / self.animation_speed) % len(frames)]

    def draw(self):
        blit_wrapped(self.game.screen, self._current_image(),
                     self.x - self.ghost_w / 2.0, self.y + self.game.y_offset - self.ghost_h / 2.0)

    def _cell_center(self, r, c):
        return (c * self.game.num2_c + self.game.num2_c / 2.0,
                r * self.game.num1_r + self.game.num1_r / 2.0 + self.game.y_offset)

    def _in_special_state(self):
        return self.game.dying or self.game.just_reset or self.eaten or self.returning_home or self.hatching

    def draw_path(self):
        if not self.path or self.game.mode_manager.frightened_active or self._in_special_state():
            return

        screen = self.game.screen
        prev_x, prev_y = self.x, self.y + self.game.y_offset
        prev_r, prev_c = self.row, self.col
        for r, c in self.path[1:]:
            x, y = self._cell_center(r, c)
            dc = c - prev_c
            if abs(dc) > 1 and r == prev_r:  # Xuyên đường hầm
                edge_from, edge_to = (0, self.game.width) if dc > 0 else (self.game.width, 0)
                pygame.draw.line(screen, self.color, (prev_x, prev_y), (edge_from, prev_y), LINE_WIDTH)
                pygame.draw.line(screen, self.color, (edge_to, y), (x, y), LINE_WIDTH)
            else:
                pygame.draw.line(screen, self.color, (prev_x, prev_y), (x, y), LINE_WIDTH)
            prev_x, prev_y = x, y
            prev_r, prev_c = r, c

        if len(self.path) >= 2:
            step = self.game.bfs_finder.step_between(*self.path[-2], *self.path[-1])
            if step:
                size = min(self.game.num1_r, self.game.num2_c) / 2
                draw_arrow_head(screen, self.color, self._cell_center(*self.path[-1]), step[0], step[1], size)
