from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import sp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.pickers import MDTimePicker
from kivy.properties import (NumericProperty, AliasProperty, OptionProperty,
                             ReferenceListProperty, BoundedNumericProperty)
from kivy.uix.widget import Widget
# from kivymd.uix import screenmanager
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.anchorlayout import MDAnchorLayout
from ctypes import windll, c_int64
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
# windll.user32.SetProcessDpiAwarenessContext(c_int64(-4))



class RangeSliderApp(BoxLayout):
    pass

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
        if self.collide_point(touch.x, touch.y):
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
        if self.collide_point(touch.x, touch.y):
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
        if self.collide_point(touch.x, touch.y):
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
        if self.collide_point(touch.x, touch.y):
            if touch.grab_current == self:
                touch.ungrab(self)
                return True


class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

class ListItemWithCheckbox(OneLineAvatarIconListItem):
    '''Custom list item.'''
    pass

    icon = StringProperty("clock")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon_left_widget = IconLeftWidget(icon=self.icon)
        self.add_widget(self.icon_left_widget)
        self.checkbox = RightCheckbox()
        self.checkbox.color_active = (0, 0, 0, 1)
        self.add_widget(self.checkbox)
    

class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''
    pass
    


class LoginScreen(MDScreen):
    def on_login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        if(username == "" and password == ""):
            print("Logged in successfully")
            self.manager.current = "home_screen"


class HomeScreen(MDScreen):

    def controlTheProgress(self, *args):
        value = args[1]
        
        # control angle end value via progress attribute
        self.ids.circular_progress_top.progress = value
        # control text progress value
        self.ids.circular_progress_top.text = f'{int(value/3.6)}°F'

        # control angle end value via progress attribute
        self.ids.circular_progress_bottom.progress = value
        # control text progress value
        self.ids.circular_progress_bottom.text = f'{int(value/3.6)}%'
    
    def show_time_picker(self, step):
        if step == 1:
            on_save = self.on_time1_set
        elif step == 2:
            on_save = self.on_time2_set

        time_picker = MDTimePicker(
            primary_color= "white",
            accent_color="lightblue",
            text_button_color="gray",
        )
        time_picker.bind(on_save=lambda instance, value: on_save(value))
        time_picker.open()

    def on_time1_set(self, time):
        self.time1 = time
        self.show_time_picker(2)

    def on_time2_set(self, time):
        self.time2 = time
        if self.time1 and self.time2:
            time1_str = f"{self.time1.hour:02d}:{self.time1.minute:02d}"
            time2_str = f"{self.time2.hour:02d}:{self.time2.minute:02d}"
            schedule_item = ListItemWithCheckbox(text=f"{time1_str} - {time2_str}")
            self.ids.schedule_list.add_widget(schedule_item)

        self.time1 = None
        self.time2 = None

    def remove_schedule(self):
        for child in reversed(self.ids.schedule_list.children):
            if child.checkbox.active:
                self.ids.schedule_list.remove_widget(child)
    

class WindowManager(MDScreenManager):
    pass


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Gray" 
        self.theme_cls.primary_hue = "200"
        kv = Builder.load_file('mainapp.kv')
        return kv
        

if __name__ == "__main__":
    MainApp().run()