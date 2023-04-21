from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.pickers import MDTimePicker
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivy.properties import StringProperty
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.anchorlayout import MDAnchorLayout

KV = '''
<ListItemWithCheckbox>:

    IconLeftWidget:
        icon: root.icon

    RightCheckbox:
        id: checkbox

BoxLayout:
    orientation: "vertical"
    MDTopAppBar:
        title: "Scheduling Assistant"
        right_action_items: [["clock-plus-outline", lambda x: app.show_time_picker(1)], ["delete", lambda x: app.remove_schedule()]]

    ScrollView:
        MDList:
            id: schedule_list

    

'''

class ListItemWithCheckbox(OneLineAvatarIconListItem):
    '''Custom list item.'''

    icon = StringProperty("clock")


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''

class FanScheduleApp(MDApp):
    def build(self):
        self.time1 = None
        self.time2 = None
        return Builder.load_string(KV)

    def show_time_picker(self, step):
        if step == 1:
            on_save = self.on_time1_set
        elif step == 2:
            on_save = self.on_time2_set

        time_picker = MDTimePicker()
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
            schedule_item = ListItemWithCheckbox(text=f"{time1_str} - {time2_str}", icon="clock")
            self.root.ids.schedule_list.add_widget(schedule_item)

        self.time1 = None
        self.time2 = None

    def remove_schedule(self):
        for child in reversed(self.root.ids.schedule_list.children):
            if child.ids.checkbox.active:
                self.root.ids.schedule_list.remove_widget(child)
            # if self.root.ids.schedule_list.children[0].ids.checkbox.active:
            #     self.root.ids.schedule_list.remove_widget(self.root.ids.schedule_list.children[0])

if __name__ == "__main__":
    FanScheduleApp().run()

kv ="""
<ListItemWithCheckbox>:

    IconLeftWidget:
        icon: root.icon

    RightCheckbox:
    """

class ListItemWithCheckbox(OneLineAvatarIconListItem):
    '''Custom list item.'''

    icon = StringProperty("clock")


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    '''Custom right container.'''