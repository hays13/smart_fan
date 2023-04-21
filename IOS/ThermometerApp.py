from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivymd.uix.progressbar import MDProgressBar
import numpy as np
import time

KV = '''
<Main>
    FloatLayout:
        orientation: 'vertical'
        size: root.width, root.height
        
        Label:
            id: circular_progress
            text: '0%'
            color: (0,0,0,1)
            
            size_hint: None, None
            width: 200
            height: 200
            
            progress: 0
            
            pos_hint: {'center_x':.5, 'center_y':.6}
            
            canvas.before:
                # Main ellipse as background
                Color:
                    rgba: (0,0,1,1)
                Ellipse:
                    size: self.size
                    pos: self.pos
                
                # Pie Chart ellipse as progress
                Color:
                    rgba: (1,0,0,1)
                Ellipse:
                    size: self.size
                    pos: self.pos
                    angle_end: self.progress
                
                # small ellipse that cover the center of progress
                Color:
                    rgba: (1,1,1,1)
                Ellipse:
                    size: [self.width - 30 ,self.height - 30]
                    pos: [(self.center_x - (self.width - 30)/2), (self.center_y - (self.height - 30)/2)]
                    
        Slider:
            orientation: 'horizontal'
            min: 0
            max: 360
            step: 1
            
            size_hint: None, None
            width: 500
            height: 200
            
            pos_hint: {'center_x':.5}
            
            on_value: root.controlTheProgress(*args)
'''

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder

from kivy.uix.widget import Widget

Builder.load_string(KV)

class Main(Widget):
    def controlTheProgress(self, *args):
        value = args[1]
        
        # control angle end value via progress attribute
        self.ids.circular_progress.progress = value
        # control text progress value
        self.ids.circular_progress.text = f'{int(value/3.6)}%'
        
class MyApp(App):
    def build(self):
        return Main()
    

if __name__ == '__main__':
    MyApp().run()