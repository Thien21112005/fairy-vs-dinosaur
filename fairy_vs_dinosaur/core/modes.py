class ModeManager:
    def __init__(self, game):
        self.game = game
        self.mode_phases = [('scatter', 7), ('chase', 20), ('scatter', 7), ('chase', 20),
                            ('scatter', 5), ('chase', 20), ('scatter', 5), ('chase', float('inf'))]
        self.current_phase = 0
        self.phase_timer = 0.0
        self.frightened_active = False
        self.frightened_timer = 0.0
        self.frightened_duration = 6.0

    def update(self, delta_time):
        if self.game.game_started and not self.frightened_active:
            self.phase_timer += delta_time
            phase_duration = self.mode_phases[self.current_phase][1]
            if self.phase_timer >= phase_duration:
                self.phase_timer = 0.0
                self.current_phase = min(self.current_phase + 1, len(self.mode_phases) - 1)
        if self.frightened_active:
            self.frightened_timer -= delta_time
            if self.frightened_timer <= 0:
                self.frightened_active = False
                self.game.sound_manager.stop_power()
                self.game.eaten_ghosts_count = 0

    def activate_frightened(self):
        for ghost in self.game.ghosts:
            ghost.frightened_disabled = False

        if not self.frightened_active:
            self.frightened_active = True
            self.frightened_timer = self.frightened_duration
            self.game.sound_manager.play_power(loops=-1)
            self.game.blinky.reverse_direction()
            print(f"Frightened mode activated: {self.frightened_duration}s")
        else:
            # Cộng dồn thời gian, tối đa 3 lần thời lượng
            self.frightened_timer = min(self.frightened_timer + self.frightened_duration,
                                        self.frightened_duration * 3)
            print(f"Frightened mode extended: {self.frightened_timer:.1f}s total")
