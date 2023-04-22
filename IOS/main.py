from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
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
from kivy.storage.dictstore import DictStore
from kivy.storage.jsonstore import JsonStore
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
# windll.user32.SetProcessDpiAwarenessContext(c_int64(-4))





def parseData(self, result):
    global current_temp, current_hum
    resultList = result.split("/")
    current_temp = [s.split('=')[1] for s in resultList if "temp=" in s][0]
    current_hum = [s.split('=')[1] for s in resultList if "humidity=" in s][0]




class RangeSliderApp(BoxLayout):
    pass



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

    def updateServer(self):
        url = 'http://172.20.10.8/fan_speed={}/trange_en={}/hrange_en={}/min_temp={}/max_temp={}/min_hum={}/max_hum={}/'.format(int(self.ids.fan_speed.value), bool(self.ids.trange_en.active), bool(self.ids.hrange_en.active), int(self.ids.min_temp.text), int(self.ids.max_temp.text), int(self.ids.min_hum.text), int(self.ids.max_hum.text))
        print(url)
        # url_encoded = urllib.parse.quote(url, safe=':/')
        try:
            request = UrlRequest(url, method='POST')
        except:
            print("cannot connect to server")
    
    def on_pre_enter(self):
        self.event = Clock.schedule_interval(self.get_data, 1)

    def get_data(self, *args):
        url = 'http://172.20.10.8/'
        try:
            request = UrlRequest(url, on_success=parseData)
            self.controlTheProgress(current_temp, current_hum)
        except:
            print("cannot connect to server")

    def enter_data_view(self):
        self.event = Clock.schedule_interval(self.get_data, 1)
    
    def exit_data_view(self):
        self.event.cancel()  

    def on_enter(self, *args):
        self.store = DictStore(filename='settings.ini')

        if self.store.exists('temperature'):
            temperature_vars = self.store.get('temperature')
            self.ids.min_temp.text = temperature_vars.get('min_temp', 0)
            self.ids.max_temp.text = temperature_vars.get('max_temp', 0)
        
        if self.store.exists('humidity'):
            humidity_vars = self.store.get('humidity')
            self.ids.min_hum.text = humidity_vars.get('min_hum', 0)
            self.ids.max_hum.text = humidity_vars.get('max_hum', 0)

        if self.store.exists('range_enabled'):
            range_vars = self.store.get('range_enabled')
            self.ids.trange_en.active = range_vars.get('trange_en', False)
            self.ids.hrange_en.active = range_vars.get('hrange_en', False)

        if self.store.exists('fan_speed'):
            fan_vars = self.store.get('fan_speed')
            self.ids.fan_speed.value = fan_vars.get('fan_speed', 0)
        
        if self.store.exists('schedule'):
            schedule_vars = self.store.get('schedule')
            schedule_list = schedule_vars.get('schedule', 0).split(",")
            for schedule in schedule_list:
                if schedule != "":
                    self.ids.schedule_list.add_widget(ListItemWithCheckbox(text=schedule))
            

    def save_settings(self):
        
        self.store.put('temperature', min_temp=self.ids.min_temp.text, max_temp=self.ids.max_temp.text)
        self.store.put('humidity', min_hum=self.ids.min_hum.text, max_hum=self.ids.max_hum.text)
        self.store.put('range_enabled', trange_en=self.ids.trange_en.active, hrange_en=self.ids.hrange_en.active)
        self.store.put('fan_speed', fan_speed=self.ids.fan_speed.value)
        self.store.store_sync()
        self.updateServer()




    def controlTheProgress(self, temp, hum):
        
        # control angle end value via progress attribute 
        self.ids.circular_progress_top.progress = int(temp)
        # control text progress value
        self.ids.circular_progress_top.text = f'{int(temp/3.6)}°F'

        # control angle end value via progress attribute
        self.ids.circular_progress_bottom.progress = int(temp)
        # control text progress value
        self.ids.circular_progress_bottom.text = f'{int(hum/3.6)}%'
    
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

    def sendSchedule(self,schedule):
        
        url = 'http://172.20.10.8/schedule={}/'.format(schedule)
        print(url)

    def save_schedule(self):
        schedule = ""
        for child in self.ids.schedule_list.children:
            print(child.text)
            schedule += child.text + ","
        self.store.put('schedule', schedule=schedule)
        self.sendSchedule(schedule)


    def on_time2_set(self, time):
        self.time2 = time
        if self.time1 and self.time2:
            time1_str = f"{self.time1.hour:02d}:{self.time1.minute:02d}"
            time2_str = f"{self.time2.hour:02d}:{self.time2.minute:02d}"
            combo_str = f"{time1_str} - {time2_str}"
            schedule_item = ListItemWithCheckbox(text=combo_str)
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