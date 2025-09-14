from kivy.core.text import LabelBase
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
import requests
import arabic_reshaper
from bidi.algorithm import get_display

LabelBase.register(
    name="Arabic",
    fn_regular="NotoNaskhArabic-Regular.ttf"
)

def reshape_arabic(text):
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception:
        return text

SERVER_URL = "http://192.168.1.10:5000"

class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.current_id = None

        self.mah_idd_input = TextInput(
            text='',
            readonly=True,
            size_hint_y=None,
            height=40,
            halign='center',
            font_size=20
        )
        self.add_widget(self.mah_idd_input)

        btn_layout = BoxLayout(size_hint_y=None, height=50)
        self.btn_first = Button(text=reshape_arabic('السجل الأول'), font_name="Arabic")
        self.btn_next = Button(text=reshape_arabic('السجل التالي'), font_name="Arabic")
        self.btn_prev = Button(text=reshape_arabic('السجل السابق'), font_name="Arabic")

        btn_layout.add_widget(self.btn_first)
        btn_layout.add_widget(self.btn_next)
        btn_layout.add_widget(self.btn_prev)
        self.add_widget(btn_layout)

        self.btn_first.bind(on_press=self.get_first)
        self.btn_next.bind(on_press=self.get_next)
        self.btn_prev.bind(on_press=self.get_prev)

        self.table = GridLayout(cols=1, size_hint_y=None)
        self.table.bind(minimum_height=self.table.setter('height'))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.table)
        self.add_widget(self.scroll)

    def safe_request(self, endpoint, params=None):
        try:
            resp = requests.get(f"{SERVER_URL}/{endpoint}", params=params, timeout=5)
            if resp.status_code == 200:
                return resp.json()
            else:
                return None
        except Exception as e:
            self.mah_idd_input.text = f"خطأ في الاتصال: {e}"
            return None

    def get_first(self, instance):
        data = self.safe_request("first")
        if data:
            self.show_record(data)

    def get_next(self, instance):
        if self.current_id is None:
            return
        data = self.safe_request("next", params={'last_id': self.current_id})
        if data:
            self.show_record(data)

    def get_prev(self, instance):
        if self.current_id is None:
            return
        data = self.safe_request("prev", params={'last_id': self.current_id})
        if data:
            self.show_record(data)

    def show_record(self, data):
        self.current_id = data.get('id')
        mah_idd = data.get('mah_idd', '')
        self.mah_idd_input.text = str(mah_idd)
        self.load_mahal_line(mah_idd)

    def load_mahal_line(self, mah_idd):
        rows = self.safe_request("mahal_line", params={'mah_idd': mah_idd})
        self.table.clear_widgets()

        if rows and isinstance(rows, list):
            columns = list(rows[0].keys())
            self.table.cols = len(columns)
            for key in columns:
                self.table.add_widget(
                    Label(
                        text=reshape_arabic(str(key)),
                        bold=True,
                        font_size=18,
                        font_name="Arabic",
                        size_hint_x=None,
                        width=180
                    )
                )
            for row in rows:
                for value in row.values():
                    self.table.add_widget(
                        Label(
                            text=reshape_arabic(str(value)),
                            font_size=16,
                            font_name="Arabic",
                            size_hint_x=None,
                            width=180
                        )
                    )
        else:
            self.table.cols = 1
            self.table.add_widget(Label(text="لا توجد بيانات", font_name="Arabic"))


class MyApp(App):
    def build(self):
        return MainWidget()


if __name__ == '__main__':
    MyApp().run()
