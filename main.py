from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.core.window import Window
import random
import sqlite3

from kivy.vector import Vector

# Designate Our .kv design file
# Builder.load_file('1.kv')

# Utworzenie połączenia z bazą danych
conn = sqlite3.connect('snake_scores.db')
c = conn.cursor()

# Utworzenie tabeli wyników
c.execute('''CREATE TABLE IF NOT EXISTS scores
             (name TEXT, score INT)''')


class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=50, padding=90)

        self.name_input = TextInput(hint_text='Wpisz swoje imię', multiline=False, padding=20, size_hint=(1.0, None),
                                    height=70)
        layout.add_widget(self.name_input)

        play_button = Button(text='GRAJ',font_size='23sp')
        play_button.bind(on_press=self.start_game)
        layout.add_widget(play_button)

        ranking_button = Button(text='RANKING',font_size='23sp')
        ranking_button.bind(on_press=self.show_ranking)
        layout.add_widget(ranking_button)

        self.add_widget(layout)

    def get_name(self):
        return self.name_input

    def start_game(self, *args):
        player_name = self.name_input.text
        if player_name:
            game_screen = MainGame(player_name=player_name)
            self.manager.switch_to(game_screen)

    def show_ranking(self, *args):
        ranking_screen = RankingScreen()
        self.manager.switch_to(ranking_screen)


class RankingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title = 'Ranking'

        layout = GridLayout(cols=3, spacing=10)

        c.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
        scores = c.fetchall()

        title_label = Label(text='RANKING', size_hint=(1, 0.1),font_size='23sp')
        layout.add_widget(Label())
        layout.add_widget(title_label)
        layout.add_widget(Label())

        layout.add_widget(Label(text='Lp.'))
        layout.add_widget(Label(text='Gracz'))
        layout.add_widget(Label(text='Punkty'))


        i = 1
        for name, score in scores:
            layout.add_widget(Label(text=str(i), size_hint=(0.2, 0.2)))
            layout.add_widget(Label(text=name, size_hint=(0.3, 1)))
            layout.add_widget(Label(text=str(score), size_hint=(0.3, 1)))
            i += 1

        return_button = Button(text='Return')
        return_button.bind(on_press=self.return_to_welcome)
        layout.add_widget(return_button)

        self.add_widget(layout)

    def return_to_welcome(self, *args):
        welcome_screen = WelcomeScreen()
        self.manager.switch_to(welcome_screen)


class MainGame(Screen):
    def __init__(self, player_name, **kwargs):
        super().__init__(**kwargs)
        self.player_name = player_name
        self.score = 0
        game_screen = SnakeGame(score_callback=self.update_score)
        self.score_label = Label(text=f'Score: {self.score}', pos=(Window.width - 60, Window.height - 50))
        self.add_widget(game_screen)

    def update_score(self, score):
        self.score = score
        self.score_label.text = f'Score: {score}'


class GameOverScreen(Screen):
    def __init__(self, score, player_name, **kwargs):
        super().__init__(**kwargs)
        c.execute("INSERT INTO scores (name, score) VALUES (?, ?)",
                  (player_name, score))
        conn.commit()
        layout = BoxLayout(orientation='vertical', spacing=50, padding=90)
        text = Label(text=f'GAME OVER, {player_name}, your score: {score}',font_size='23sp')
        layout.add_widget(text)

        return_button = Button(text='Return')
        return_button.bind(on_press=self.return_to_welcome)
        layout.add_widget(return_button)

        self.add_widget(layout)

    def return_to_welcome(self, *args):
        welcome_screen = WelcomeScreen()
        self.manager.switch_to(welcome_screen)


class SnakeGame(Widget):
    def __init__(self, score_callback, **kwargs):
        super(SnakeGame, self).__init__(**kwargs)

        self.snake_size = 20
        self.food_size = 20
        self.snake = [(100, 100), (120, 100), (140, 100), (160, 100), (180, 100)]
        self.food = self.generate_food
        self.direction = Vector(1, 0)

        self.bind(size=self.resize)
        self.bind(pos=self.redraw)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down)

        self.score = 0
        self.running = True

        self.event1 = Clock.schedule_interval(self.update, 0.1)

    def resize(self, *args):
        self.redraw()

    def redraw(self, *args):
        self.canvas.clear()

        with self.canvas:
            Color(1, 1, 1)
            for segment in self.snake:
                Rectangle(pos=(segment[0], segment[1]), size=(self.snake_size, self.snake_size))

            Color(1, 0, 0)
            Rectangle(pos=(self.food[0], self.food[1]), size=(self.food_size, self.food_size))

    @property
    def generate_food(self):
        x = random.randint(1, (int(Window.width / self.snake_size) - 1)) * self.snake_size
        y = random.randint(1, (int(Window.height / self.snake_size) - 1)) * self.snake_size
        return x, y

    def update(self, dt):
        new_head = (
            self.snake[-1][0] + self.direction[0] * self.snake_size,
            self.snake[-1][1] + self.direction[1] * self.snake_size
        )
        if (
                new_head[0] < 0 or
                new_head[0] >= Window.width or
                new_head[1] < 0 or
                new_head[1] >= Window.height or
                new_head in self.snake[:-1]
        ):
            self.event1.cancel()
            gameover_screen = GameOverScreen(score=self.score,player_name=self.parent.player_name)
            print("Koniec gry")
            print(self.parent.manager)
            self.parent.manager.switch_to(gameover_screen)

        #print(new_head)
        #print(Window.width)
        #print(Window.height)
        self.snake.append(new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food
        else:
            self.snake = self.snake[1:]

        self.redraw()

    def schedule_update(self):
        return Clock.schedule_interval(self.update, 0.2)

    def do_nothing(self):
        pass

    def on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'up' and (self.direction != Vector(0, -1)):
            self.direction = Vector(0, 1)
        elif keycode[1] == 'down' and (self.direction != Vector(0, 1)):
            self.direction = Vector(0, -1)
        elif keycode[1] == 'left' and (self.direction != Vector(1, 0)):
            self.direction = Vector(-1, 0)
        elif keycode[1] == 'right' and (self.direction != Vector(-1, 0)):
            self.direction = Vector(1, 0)
        else:
            pass

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard = None


class SnakeApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget((RankingScreen(name='Ranking')))
        #sm.add_widget(MainGame(name='gra',player_name='Nowy gracz'))
        #sm.add_widget((GameOverScreen(name='gameover',score=0)))
        return sm


if __name__ == '__main__':
    SnakeApp().run()
