from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from math import hypot
import random

Window.clearcolor = get_color_from_hex("#102b18")

class FootballGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = [0.28, 0.50]
        self.enemy = [0.73, 0.50]
        self.keeper = [0.91, 0.50]
        self.ball = [0.42, 0.50]
        self.ball_v = [0.0, 0.0]
        self.score = [0, 0]
        self.seconds = 90
        self.joy_touch = None
        self.joy_vec = [0.0, 0.0]
        self.message = ""
        self.message_time = 0
        self.finished = False

        self.hud = Label(text="", bold=True, font_size=dp(19),
                         size_hint=(None, None), halign="center")
        self.add_widget(self.hud)
        self.status = Label(text="", bold=True, font_size=dp(25),
                            size_hint=(None, None), halign="center")
        self.add_widget(self.status)

        Clock.schedule_interval(self.update, 1/60)
        Clock.schedule_interval(self.tick, 1)

    def on_size(self, *args):
        self.draw_scene()

    def on_pos(self, *args):
        self.draw_scene()

    def field_rect(self):
        margin = dp(18)
        return (self.x + margin, self.y + margin,
                max(1, self.width - 2*margin),
                max(1, self.height - 2*margin))

    def point(self, p):
        x, y, w, h = self.field_rect()
        return (x + p[0]*w, y + p[1]*h)

    def draw_scene(self):
        if self.width <= 0 or self.height <= 0:
            return
        self.canvas.before.clear()
        self.canvas.clear()
        x, y, w, h = self.field_rect()

        with self.canvas:
            Color(*get_color_from_hex("#174d2a"))
            Rectangle(pos=self.pos, size=self.size)

            # Pitch stripes
            for i in range(10):
                Color(*get_color_from_hex("#287b3c" if i % 2 == 0 else "#236d35"))
                Rectangle(pos=(x + i*w/10, y), size=(w/10 + 1, h))

            Color(1, 1, 1, 0.95)
            Line(rectangle=(x, y, w, h), width=1.5)
            Line(points=[x+w/2, y, x+w/2, y+h], width=1.3)
            Line(circle=(x+w/2, y+h/2, dp(42)), width=1.2)
            Ellipse(pos=(x+w/2-dp(3), y+h/2-dp(3)),
                   size=(dp(6), dp(6)))
            # Penalty boxes
            Line(rectangle=(x, y+h*.28, w*.15, h*.44), width=1.2)
            Line(rectangle=(x+w*.85, y+h*.28, w*.15, h*.44), width=1.2)
            Line(rectangle=(x, y+h*.39, w*.06, h*.22), width=1.2)
            Line(rectangle=(x+w*.94, y+h*.39, w*.06, h*.22), width=1.2)
            # Goals
            Line(rectangle=(x-dp(10), y+h*.39, dp(10), h*.22), width=2)
            Line(rectangle=(x+w, y+h*.39, dp(10), h*.22), width=2)

            self.draw_person(self.player, "#2687ff", "10")
            self.draw_person(self.enemy, "#e83e3e", "9")
            self.draw_person(self.keeper, "#ffd43b", "1")
            bx, by = self.point(self.ball)
            Color(0.05, 0.05, 0.05)
            Ellipse(pos=(bx-dp(9), by-dp(9)), size=(dp(18), dp(18)))
            Color(1, 1, 1)
            Ellipse(pos=(bx-dp(6), by-dp(6)), size=(dp(12), dp(12)))
            Color(0.05, 0.05, 0.05)
            Ellipse(pos=(bx-dp(2), by-dp(2)), size=(dp(4), dp(4)))

            # Joystick base and knob
            jx, jy = self.x + dp(85), self.y + dp(80)
            Color(.08, .08, .08, .65)
            Ellipse(pos=(jx-dp(48), jy-dp(48)), size=(dp(96), dp(96)))
            Color(.65, .65, .65, .9)
            Ellipse(pos=(jx + self.joy_vec[0]*dp(30)-dp(20),
                         jy + self.joy_vec[1]*dp(30)-dp(20)),
                   size=(dp(40), dp(40)))

            # Shoot / pass buttons
            sx, sy = self.x+self.width-dp(82), self.y+dp(78)
            Color(.82, .12, .12, .95)
            Ellipse(pos=(sx-dp(43), sy-dp(43)), size=(dp(86), dp(86)))
            px, py = self.x+self.width-dp(185), self.y+dp(55)
            Color(.12, .35, .85, .95)
            Rectangle(pos=(px-dp(42), py-dp(28)), size=(dp(84), dp(56)))

        self.hud.text = f"YOU  {self.score[0]}  -  {self.score[1]}  CPU       {self.seconds}s"
        self.hud.size = (self.width, dp(35))
        self.hud.pos = (self.x, self.y+self.height-dp(38))
        self.status.text = self.message
        self.status.size = (self.width, dp(45))
        self.status.pos = (self.x, self.y+self.height*.62)

    def draw_person(self, p, color, number):
        px, py = self.point(p)
        with self.canvas:
            Color(0, 0, 0, .35)
            Ellipse(pos=(px-dp(17), py-dp(18)), size=(dp(34), dp(13)))
            Color(*get_color_from_hex(color))
            Ellipse(pos=(px-dp(16), py-dp(16)), size=(dp(32), dp(32)))
            Color(1, 1, 1)
            Line(circle=(px, py, dp(16)), width=1.1)

    def dist(self, a, b):
        return hypot(a[0]-b[0], a[1]-b[1])

    def shoot(self, power=0.12, toward_goal=True):
        if self.dist(self.player, self.ball) < .105:
            dx = 1 if toward_goal else .65
            dy = (self.ball[1] - .5) * .45
            length = hypot(dx, dy) or 1
            self.ball_v = [dx/length*power, dy/length*power]

    def reset_positions(self):
        self.player = [.28, .50]
        self.enemy = [.73, .50]
        self.keeper = [.91, .50]
        self.ball = [.50, .50]
        self.ball_v = [0.0, 0.0]

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        x, y = touch.pos
        jx, jy = self.x+dp(85), self.y+dp(80)
        sx, sy = self.x+self.width-dp(82), self.y+dp(78)
        px, py = self.x+self.width-dp(185), self.y+dp(55)
        if hypot(x-jx, y-jy) < dp(75):
            self.joy_touch = touch.uid
            self.set_joystick(x, y)
            return True
        if hypot(x-sx, y-sy) < dp(55):
            self.shoot(.16, True)
            return True
        if abs(x-px) < dp(55) and abs(y-py) < dp(40):
            self.shoot(.105, False)
            return True
        return True

    def on_touch_move(self, touch):
        if self.joy_touch == touch.uid:
            self.set_joystick(*touch.pos)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.joy_touch == touch.uid:
            self.joy_touch = None
            self.joy_vec = [0.0, 0.0]
            self.draw_scene()
            return True
        return super().on_touch_up(touch)

    def set_joystick(self, tx, ty):
        jx, jy = self.x+dp(85), self.y+dp(80)
        dx, dy = tx-jx, ty-jy
        length = hypot(dx, dy)
        limit = dp(48)
        if length > limit:
            dx, dy = dx/length*limit, dy/length*limit
        self.joy_vec = [dx/limit, dy/limit]

    def tick(self, dt):
        if not self.finished:
            self.seconds = max(0, self.seconds-1)
            if self.seconds == 0:
                self.finished = True
                self.message = "FULL TIME"
        if self.message_time > 0:
            self.message_time -= 1
            if self.message_time == 0 and not self.finished:
                self.message = ""
        self.draw_scene()

    def update(self, dt):
        if self.finished:
            return
        # Player movement
        self.player[0] += self.joy_vec[0]*.0035
        self.player[1] += self.joy_vec[1]*.0035
        self.player[0] = max(.025, min(.975, self.player[0]))
        self.player[1] = max(.035, min(.965, self.player[1]))

        # CPU follows the ball
        dx, dy = self.ball[0]-self.enemy[0], self.ball[1]-self.enemy[1]
        d = hypot(dx, dy)
        if d > .015:
            self.enemy[0] += dx/d*.0013
            self.enemy[1] += dy/d*.0013
        self.enemy[0] = max(.53, min(.84, self.enemy[0]))
        self.enemy[1] = max(.08, min(.92, self.enemy[1]))

        # Goalkeeper tracks ball vertically
        self.keeper[1] += (self.ball[1]-self.keeper[1])*.025
        self.keeper[1] = max(.40, min(.60, self.keeper[1]))

        # Ball physics
        self.ball[0] += self.ball_v[0]
        self.ball[1] += self.ball_v[1]
        self.ball_v[0] *= .985
        self.ball_v[1] *= .985
        if hypot(*self.ball_v) < .0007:
            self.ball_v = [0.0, 0.0]

        if self.ball[1] < .025 or self.ball[1] > .975:
            self.ball_v[1] *= -.75
            self.ball[1] = max(.025, min(.975, self.ball[1]))

        # CPU kicks occasionally
        if self.dist(self.enemy, self.ball) < .055 and random.random() < .018:
            self.ball_v = [-.075, random.uniform(-.025, .025)]

        # Keeper save
        if self.ball[0] > .87 and abs(self.ball[1]-self.keeper[1]) < .065:
            if self.ball_v[0] > 0:
                self.ball_v[0] *= -.8

        # Goals
        if self.ball[0] > 1.015 and .39 < self.ball[1] < .61:
            self.score[0] += 1
            self.message = "GOAL!"
            self.message_time = 2
            self.reset_positions()
        elif self.ball[0] < -.015 and .39 < self.ball[1] < .61:
            self.score[1] += 1
            self.message = "CPU GOAL"
            self.message_time = 2
            self.reset_positions()

        self.draw_scene()

class FootballApp(App):
    def build(self):
        self.title = "FOOTBALL PRO"
        return FootballGame()

if __name__ == "__main__":
    FootballApp().run()
