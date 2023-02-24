from kivy.app import App
import kivy.uix
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.screenmanager import Screen, ScreenManager
import datetime
from kivy.properties import ListProperty,ObjectProperty,NumericProperty
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest

def parseData(result):
    global current_temp,current_hum,fan_speed
    resultList = result.split("/")
    current_temp = [s.split('=')[1] for s in resultList if "temp=" in s]
    current_hum = [s.split('=')[1] for s in resultList if "humidity=" in s]
    fan_speed = [s.split('=')[1] for s in resultList if "speed=" in s]

UrlRequest('178.0.0.1/actionpage?')
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create a label for the login screen
        self.label = Label(text='Please login to your Smart Fan account', font_size=24, pos_hint = {'center_x': 0.5, 'center_y': 0.8})

        self.login_button = Button(text='Login', font_size=24, size_hint_y=None, height=50)
        self.login_button.bind(on_press=self.check_login)

        # Add the widgets to the layout
        
        self.add_widget(self.label)
        self.add_widget(self.login_button)

    def check_login(self, instance):
        username = self.ids.username
        password = self.ids.password
        if username.text == '' and password.text == '':
            self.label.text = 'Login successful!'
            app.screen_manager.current = 'fan_control'
        else:
            self.label.text = 'Login information incorrect. Try again'

class FanControlScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def toggle_fan(self, instance):
        if instance.text == 'Turn Fan On':
            instance.text = 'Turn Fan Off'
        else:
            instance.text = 'Turn Fan On'
    
    def fan_on(self):
        print("Turning Fan On")
        pass
    
    def fan_off(self):
        print("Turning Fan Off")
        pass

    

class TemperatureRangeScreen(Screen):
    current_temperature_label = ObjectProperty()
    current_humidity_label = ObjectProperty(None)
    temp_min_slider = ObjectProperty(None)
    temp_max_slider = ObjectProperty(None)

    

    def on_enter(self, *args):
        # Update current temperature and humidity labels
        request = UrlRequest('178.0.0.1')
        dataList = parseData(request.result)
        current_temp = 80 #dataList[0]
        current_humidity = 15 #dataList[1]
        self.ids.current_temperature_label.text = f"Current Temperature: {current_temp} °F"
        self.ids.current_humidity_label.text = f"Current Humidity: {current_humidity} %"


    
    def on_leave(self, *args):
        send_mintemp = self.ids.temp_min_slider.value
        send_maxtemp = self.ids.temp_max_slider.value
        send_fanpower = self.ids.fan_power_slider.value
        #light status
        send_schedule = self.schedule_text
        

    def back_to_fan_control_screen(self):
        app.screen_manager.current = 'fan_control'

class ScheduleScreen(Screen):
    def add_schedule(self):
        start_time = "{}:{} {}".format(
            self.ids.start_time_hour.text,
            self.ids.start_time_minute.text,
            self.ids.start_time_am_pm.text
        )
        end_time = "{}:{} {}".format(
            self.ids.end_time_hour.text,
            self.ids.end_time_minute.text,
            self.ids.end_time_am_pm.text
        )
        schedule_text = "{} - {}".format(start_time, end_time)
        schedule_label = Label(text=schedule_text)
        self.ids.schedule_grid.add_widget(schedule_label)

    def remove_schedule(self):
        self.ids.schedule_grid.clear_widgets()

class WindowManager(ScreenManager):
    pass

class FanControlApp(App):
    def build(self):
        # Create the screen manager
        self.screen_manager = WindowManager()

        # Create the screens
        self.login_screen = LoginScreen(name='login')
        self.fan_control_screen = FanControlScreen(name='fan_control')
        self.temp_range_screen = TemperatureRangeScreen(name='temp_range')
        self.schedule_screen = ScheduleScreen(name='schedule')

        # Add the screens to the screen manager
        self.screen_manager.add_widget(self.login_screen)
        self.screen_manager.add_widget(self.fan_control_screen)
        self.screen_manager.add_widget(self.temp_range_screen)
        self.screen_manager.add_widget(self.schedule_screen)

        return self.screen_manager

if __name__ == '__main__':
    app = FanControlApp()
    app.run()