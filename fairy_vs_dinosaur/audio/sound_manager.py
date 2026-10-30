import pygame

from fairy_vs_dinosaur.config import asset


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        self.pellet_sound1 = pygame.mixer.Sound(asset('sounds/eat_pellet1.mp3'))
        self.pellet_sound2 = pygame.mixer.Sound(asset('sounds/eat_pellet2.mp3'))
        self.pellet_toggle = 0
        self.power_pellet_sound = pygame.mixer.Sound(asset('sounds/eat_power_pellet.mp3'))
        self.intro_sound = pygame.mixer.Sound(asset('sounds/play_game.mp3'))
        self.ghost_move_sound = pygame.mixer.Sound(asset('sounds/ghost_move.mp3'))
        self.ghost_eat_sound = pygame.mixer.Sound(asset('sounds/ghost_eat.mp3'))
        self.game_over_sound = pygame.mixer.Sound(asset('sounds/game_over1.mp3'))  # Thêm sound game over
        self.count_down = pygame.mixer.Sound(asset('sounds/count_down.mp3'))

        # Thêm sound cho button
        self.button_hover_sound = pygame.mixer.Sound(asset('sounds/button_hover.wav'))  # Giả sử bạn có file này
        self.button_click_sound = pygame.mixer.Sound(asset('sounds/button_click.mp3'))  # Giả sử bạn có file này

        # Thêm nhạc menu
        self.menu_music = asset('sounds/mainmenu_music.mp3')  # Giả sử bạn có file này
        self.magic_sound = pygame.mixer.Sound(asset('sounds/magic.wav'))

        # Thêm channel cho magic sound
        self.magic_channel = pygame.mixer.Channel(5)  # Sử dụng channel 5

        self.power_channel = pygame.mixer.Channel(1)
        self.ghost_channel = pygame.mixer.Channel(2)
        self.death_channel = pygame.mixer.Channel(3)
        self.game_over_channel = pygame.mixer.Channel(4)  # Channel riêng cho game over

        # Thêm âm thanh turn_egg
        self.turn_egg_sound = pygame.mixer.Sound(asset('sounds/turn_egg.mp3'))

        # Thêm channel cho turn_egg sound
        self.turn_egg_channel = pygame.mixer.Channel(6)  # Sử dụng channel 6

        self.egg_hatch_sound = pygame.mixer.Sound(asset('sounds/egg_hatch.mp3'))

        # Thêm channel cho egg_hatch sound
        self.egg_hatch_channel = pygame.mixer.Channel(7)  # Sử dụng channel 7

        self.intro_channel = pygame.mixer.Channel(8)  # Sử dụng channel 8 cho intro
        self.hold_sound = pygame.mixer.Sound(asset('sounds/hold.mp3'))  # Giả sử file tồn tại
        self.flick_sound = pygame.mixer.Sound(asset('sounds/flicker.mp3'))  # Giả sử file tồn tại
        self.throw_sound = pygame.mixer.Sound(asset('sounds/throw.mp3'))  # Giả sử file tồn tại

        # Thêm channels cho các sound mới
        self.hold_channel = pygame.mixer.Channel(9)  # Channel cho hold
        self.flick_channel = pygame.mixer.Channel(10)  # Channel cho flick
        self.throw_channel = pygame.mixer.Channel(11)  # Channel cho throw


    def play_menu_music(self):
        pygame.mixer.music.load(self.menu_music)
        pygame.mixer.music.play(-1)  # Lặp vô hạn

    def fade_out_menu_music(self, duration=1000):
        pygame.mixer.music.fadeout(duration)

    def play_intro(self):
        self.intro_channel.play(self.intro_sound)

    def stop_intro(self):
        self.intro_channel.stop()

    def pause_intro(self):
        self.intro_channel.pause()

    def unpause_intro(self):
        self.intro_channel.unpause()

    def play_ghost_move(self, loops=-1):
        self.ghost_channel.play(self.ghost_move_sound, loops=loops)

    def stop_ghost(self):
        self.ghost_channel.stop()

    def play_power(self, loops=-1):
        self.power_channel.play(self.power_pellet_sound, loops=loops)

    def stop_power(self):
        self.power_channel.stop()

    def play_death(self):
        self.death_channel.play(self.ghost_eat_sound)
    def play_game_over(self):
        self.game_over_channel.play(self.game_over_sound)

    def stop_all_sounds(self):
        """Dừng tất cả âm thanh đang phát"""
        # Dừng tất cả channels
        self.ghost_channel.stop()
        self.power_channel.stop()
        self.death_channel.stop()
        self.game_over_channel.stop()
        self.hold_channel.stop()  # Dừng hold
        self.flick_channel.stop()  # Dừng flick
        self.throw_channel.stop()  # Dừng throw

        # Dừng tất cả sound effects đang phát
        self.pellet_sound1.stop()
        self.pellet_sound2.stop()
        self.power_pellet_sound.stop()
        self.intro_sound.stop()
        self.ghost_move_sound.stop()
        self.ghost_eat_sound.stop()
        self.game_over_sound.stop()
        self.turn_egg_sound.stop()
        self.egg_hatch_channel.stop()
        self.hold_sound.stop()  # Dừng hold sound
        self.flick_sound.stop()  # Dừng flick sound
        self.throw_sound.stop()

        # Dừng nhạc nền nếu có
        pygame.mixer.music.stop()

    def play_magic(self):
        """Phát âm thanh magic khi ăn ghost"""
        self.magic_channel.play(self.magic_sound)

    def play_turn_egg(self, loops=-1):
        """Phát âm thanh turn_egg khi ghost về nhà"""
        self.turn_egg_channel.play(self.turn_egg_sound, loops=loops)

    def stop_turn_egg(self):
        """Dừng âm thanh turn_egg"""
        self.turn_egg_channel.stop()

    def play_egg_hatch(self):
        """Phát âm thanh egg_hatch khi ghost nở trứng"""
        self.egg_hatch_channel.play(self.egg_hatch_sound)

    def stop_egg_hatch(self):
        """Dừng âm thanh egg_hatch"""
        self.egg_hatch_channel.stop()

    def play_count_down(self):
        self.count_down.play()

    def is_intro_playing(self):
        """Kiểm tra xem intro có đang phát không"""
        return self.intro_channel.get_busy()

    def is_intro_paused(self):
        """Kiểm tra xem intro có đang bị tạm dừng không"""
        # Pygame không có phương thức trực tiếp để kiểm tra pause
        # Nhưng chúng ta có thể kiểm tra xem channel có busy nhưng không có sound nào đang phát
        return self.intro_channel.get_busy() and not self.intro_channel.get_sound()

    def pause_turn_egg(self):
        """Tạm dừng âm thanh turn_egg"""
        self.turn_egg_channel.pause()
    def unpause_turn_egg(self):
        """Tiếp tục phát âm thanh turn_egg"""
        self.turn_egg_channel.unpause()

    def play_hold(self, loops=0):
        """Phát âm thanh hold (ví dụ: khi giữ fireball)"""
        self.hold_channel.play(self.hold_sound, loops=loops)

    def stop_hold(self):
        """Dừng âm thanh hold"""
        self.hold_channel.stop()

    def play_flick(self, loops=0):
        """Phát âm thanh flick (ví dụ: khi fireball chớp)"""
        self.flick_channel.play(self.flick_sound, loops=loops)

    def stop_flick(self):
        """Dừng âm thanh flick"""
        self.flick_channel.stop()

    def play_throw(self, loops=0):
        """Phát âm thanh throw (ví dụ: khi ném fireball)"""
        self.throw_channel.play(self.throw_sound, loops=loops)

    def stop_throw(self):
        """Dừng âm thanh throw"""
        self.throw_channel.stop()
