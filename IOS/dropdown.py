import os
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import sp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.pickers import MDTimePicker
from kivy.properties import (NumericProperty, AliasProperty, OptionProperty,
                             ReferenceListProperty, BoundedNumericProperty)
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd import images_path

KV = '''
<RangeSlider>:
    canvas:
        Color:
            rgb: 1, 1, 1
        BorderImage:
            # border: (0, 18, 0, 18) if self.orientation == 'horizontal' else (18, 0, 18, 0)

            pos: (self.x + self.padding, self.center_y - sp(18)) if self.orientation == 'horizontal' else (self.center_x - 18, self.y + self.padding)

            size: (self.width - self.padding * 2, sp(36)) if self.orientation == 'horizontal' else (sp(36), self.height - self.padding * 2)
            source: 'atlas://data/images/defaulttheme/slider{}_background{}'.format(self.orientation[0], '_disabled' if self.disabled else '')
        Color:
            rgba: (1,0,0,1)
        BorderImage:
            # border: (0, 18, 0, 18) if self.orientation == 'horizontal' else (18, 0, 18, 0)
            pos: (self.value1_pos[0], self.center_y - sp(18)) if self.orientation == 'horizontal' else (self.center_x - sp(18), self.value1_pos[1])
            size: (self.value2_pos[0] - self.value1_pos[0], sp(36)) if self.orientation == 'horizontal' else (sp(36), self.value2_pos[1] - self.value1_pos[1])

            source: 'atlas://data/images/defaulttheme/slider{}_background{}'.format(self.orientation[0], '_disabled' if self.disabled else '')

        Color:
            rgb: 1, 1, 1

        Rectangle:
            pos: (self.value1_pos[0] - sp(16), self.center_y - sp(17)) if self.orientation == 'horizontal' else (self.center_x - sp(16), self.value1_pos[1] - sp(16))
            size: (sp(32), sp(32))
            source: 'atlas://data/images/defaulttheme/slider_cursor{}'.format('_disabled' if self.disabled else '')
        Rectangle:
            pos: (self.value2_pos[0] - sp(16), self.center_y - sp(17)) if self.orientation == 'horizontal' else (self.center_x - sp(16), self.value2_pos[1] - sp(16))
            size: (sp(32), sp(32))
            source: 'atlas://data/images/defaulttheme/slider_cursor{}'.format('_disabled' if self.disabled else '')


<RangeSliderApp>:
    orientation: 'vertical'

    BoxLayout:
        size_hint_y: .3
        height: '48dp'
        Label:
            text: 'Default'
        Label:
            text: '{}'.format(s1.value[0])
        RangeSlider:
            id: s1
            value: 40, 80
        Label:
            text: '{}'.format(s1.value[1])
      


MDScrollView:

    MDGridLayout:
        id: box
        cols: 1
        adaptive_height: True
'''


class RangeSlider(Widget):

    def _get_value(self):
        return [self.value1, self.value2]
    def _set_value(self, value):
        self.value1, self.value2 = value

    value = AliasProperty(_get_value, _set_value, bind=('value1', 'value2'))
    value1 = NumericProperty(0.)
    value2 = NumericProperty(100.)

    min = NumericProperty(0.)
    max = NumericProperty(100.)

    padding = NumericProperty(sp(16))
    orientation = OptionProperty('horizontal', options=(
        'vertical', 'horizontal'))

    range = ReferenceListProperty(min, max)
    step = BoundedNumericProperty(0, min=0)

    def on_min(self, *largs):
        self.value1 = min(self.max, max(self.min, self.value1))
        self.value2 = min(self.max, max(self.min, self.value2))

    def on_max(self, *largs):
        self.value1 = min(self.max, max(self.min, self.value1))
        self.value2 = min(self.max, max(self.min, self.value2))

    def get_norm_value1(self):
        vmin = self.min
        d = self.max - vmin
        if d == 0:
            return 0
        return (self.value1 - vmin) / float(d)

    def get_norm_value2(self):
        vmin = self.min
        d = self.max - vmin
        if d == 0:
            return 0
        return (self.value2 - vmin) / float(d)

    def set_norm_value1(self, value):
        vmin = self.min
        step = self.step
        val = value * (self.max - vmin) + vmin
        if step == 0:
            self.value1 = val
        else:
            self.value1 = min(round((val - vmin) / step) * step + vmin,
                              self.max)

    def set_norm_value2(self, value):
        vmin = self.min
        step = self.step
        val = value * (self.max - vmin) + vmin
        if step == 0:
            self.value2 = val
        else:
            self.value2 = min(round((val - vmin) / step) * step + vmin,
                              self.max)

    value1_normalized = AliasProperty(get_norm_value1, set_norm_value1,
                                      bind=('value1', 'min', 'max', 'step'))
    value2_normalized = AliasProperty(get_norm_value2, set_norm_value2,
                                      bind=('value2', 'min', 'max', 'step'))

    def get_value1_pos(self):
        padding = self.padding
        x = self.x
        y = self.y
        nval = self.value1_normalized
        if self.orientation == 'horizontal':
            return (x + padding + nval * (self.width - 2 * padding), y)
        else:
            return (x, y + padding + nval * (self.height - 2 * padding))

    def get_value2_pos(self):
        padding = self.padding
        x = self.x
        y = self.y
        nval = self.value2_normalized
        if self.orientation == 'horizontal':
            return (x + padding + nval * (self.width - 2 * padding), y)
        else:
            return (x, y + padding + nval * (self.height - 2 * padding))

    def set_value1_pos(self, pos):
        padding = self.padding
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        if self.orientation == 'horizontal':
            if self.width == 0:
                self.value1_normalized = 0
            else:
                self.value1_normalized = (x - self.x - padding
                                          ) / float(self.width - 2 * padding)
        else:
            if self.height == 0:
                self.value1_normalized = 0
            else:
                self.value1_normalized = (y - self.y - padding
                                          ) / float(self.height - 2 * padding)

    def set_value2_pos(self, pos):
        padding = self.padding
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        if self.orientation == 'horizontal':
            if self.width == 0:
                self.value2_normalized = 0
            else:
                self.value2_normalized = (x - self.x - padding
                                          ) / float(self.width - 2 * padding)
        else:
            if self.height == 0:
                self.value2_normalized = 0
            else:
                self.value2_normalized = (y - self.y - padding
                                          ) / float(self.height - 2 * padding)

    value1_pos = AliasProperty(get_value1_pos, set_value1_pos,
                               bind=('x', 'y', 'width', 'height', 'min',
                                     'max', 'value1_normalized', 'orientation'))
    value2_pos = AliasProperty(get_value2_pos, set_value2_pos,
                               bind=('x', 'y', 'width', 'height', 'min',
                                     'max', 'value2_normalized', 'orientation'))

    def _touch_normalized_value(self, touch):
        pos = touch.pos
        padding = self.padding
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        if self.orientation == 'horizontal':
            value = (x - self.x - padding
                     ) / float(self.width - 2 * padding)
        else:
            value = (y - self.y - padding
                     ) / float(self.height - 2 * padding)
        return value

    def on_touch_down(self, touch):
        if self.disabled or not self.collide_point(*touch.pos):
            return
        touch.grab(self)
        t_value = self._touch_normalized_value(touch)
        if abs(self.value1_normalized - t_value) < abs(self.value2_normalized - t_value):
            self.value1_pos = touch.pos
            touch.ud['cursorid'] = 1
        else:
            self.value2_pos = touch.pos
            touch.ud['cursorid'] = 2
        return True

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            if 'cursorid' in touch.ud:
                if touch.ud['cursorid'] == 1:
                    self.value1_pos = touch.pos
                    if self.value1 > self.value2:
                        self.value1_pos = self.value2_pos
                elif touch.ud['cursorid'] == 2:
                    self.value2_pos = touch.pos
                    if self.value2 < self.value1:
                        self.value2_pos = self.value1_pos
                return True

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            touch.ungrab(self)
            return True
        
class RangeSliderApp(BoxLayout):
    pass


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
            self.root.ids.box.add_widget(
                MDExpansionPanel(
                    icon="fan",
                    content=RangeSliderApp(),
                    panel_cls=MDExpansionPanelOneLine(
                        text="Text",
                    )
                )
            )


Test().run()