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
                self.current_phase += 1
                if self.current_phase >= len(self.mode_phases):
                    self.current_phase = len(self.mode_phases) - 1
        if self.frightened_active:
            self.frightened_timer -= delta_time
            if self.frightened_timer <= 0:
                self.frightened_active = False
                self.game.sound_manager.stop_power()  # Giả sử sound_manager

    def activate_frightened(self):
        # Reset disabled cho tất cả ghost khi kích hoạt frightened mới
        if hasattr(self.game, 'ghosts'):
            for ghost in self.game.ghosts:
                ghost.frightened_disabled = False

        was_already_active = self.frightened_active
        if not self.frightened_active:
            # Kích hoạt mới
            self.frightened_active = True
            self.frightened_timer = self.frightened_duration
            self.game.sound_manager.play_power(loops=-1)
            self.game.blinky.reverse_direction()
            print(f"Frightened mode activated: {self.frightened_duration}s")
        else:
            # Cộng dồn thời gian
            new_timer = self.frightened_timer + self.frightened_duration
            # Giới hạn tối đa (tuỳ chọn)
            max_duration = self.frightened_duration * 3  # Tối đa 3 lần duration
            self.frightened_timer = min(new_timer, max_duration)
            print(f"Frightened mode extended: {self.frightened_timer:.1f}s total")
