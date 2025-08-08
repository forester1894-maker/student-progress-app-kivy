# main.py
import os
import json
import csv
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen  # Исправлено: добавлен импорт Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.checkbox import CheckBox
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.properties import NumericProperty, ListProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex

# === Папка для сохранения ===
DATA_DIR = "groups"
os.makedirs(DATA_DIR, exist_ok=True)

# === Современные цвета (адаптированы для Kivy RGBA из оригинального Tkinter) ===
COLOR_PRIMARY = get_color_from_hex("#2c3e50")      # Темно-синий #2c3e50
COLOR_SECONDARY = get_color_from_hex("#3498db")    # Голубой #3498db
COLOR_ACCENT = get_color_from_hex("#e74c3c")       # Красный #e74c3c
COLOR_SUCCESS = get_color_from_hex("#27ae60")      # Зеленый #27ae60
COLOR_WARNING = get_color_from_hex("#f39c12")      # Оранжевый #f39c12
COLOR_DANGER = get_color_from_hex("#c0392b")       # Темно-красный #c0392b
COLOR_LIGHT = get_color_from_hex("#ecf0f1")        # Светло-серый #ecf0f1
COLOR_DARK = get_color_from_hex("#34495e")         # Серо-синий #34495e
COLOR_WHITE = get_color_from_hex("#ffffff")        # Белый #ffffff
COLOR_GRAY = get_color_from_hex("#bdc3c7")         # Серый #bdc3c7
COLOR_CHECKED = get_color_from_hex("#aed6f1")      # Светло-голубой #aed6f1
COLOR_CHECKED_ACTIVE = COLOR_SUCCESS                # Зеленый для подтвержденных
COLOR_BUTTON_DANGER = COLOR_ACCENT                 # Красный для Т.Б.
COLOR_BUTTON_SUCCESS = COLOR_SUCCESS               # Зеленый для Работоспособности
COLOR_BUTTON_PRIMARY = COLOR_SECONDARY            # Голубой для основных кнопок
COLOR_BUTTON_GRAY = COLOR_GRAY                     # Серый для неактивных кнопок
COLOR_BG_LIGHT = COLOR_LIGHT                       # Фон приложения
COLOR_HEADER_BG = COLOR_PRIMARY                    # Фон заголовка
COLOR_TEXT_DARK = COLOR_DARK                       # Темный текст
COLOR_TEXT_LIGHT = COLOR_WHITE                     # Светлый текст

# === Глобальные переменные (для совместимости с логикой оригинала) ===
students = []
group_name = "Группа"
num_shifts = 4

# === Инициализация студентов (оригинальная логика) ===
def init_students():
    global students
    students.clear()
    for i in range(30):
        s = {
            "name": f"Студент {i+1}",
            "total_score": 0,
            "tb_pressed": False,
            "work_pressed": False,
            "history": []
        }
        # Инициализируем смены
        for j in range(1, num_shifts + 1):
            s[f"s{j}"] = 0
        students.append(s)

# === Виджет для ячейки оценки (слайдер + значение + чекбокс) ===
class ScoreSliderWidget(BoxLayout):
    score_value = NumericProperty(0)
    student_index = NumericProperty(0)
    shift_index = NumericProperty(0)
    owner = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_x = None
        self.width = dp(120)
        self.spacing = dp(1)
        
        # Фон для ячейки
        with self.canvas.before:
            Color(*COLOR_GRAY)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Слайдер
        self.slider = Slider(min=0, max=100, value=int(self.score_value), step=1)
        self.slider.student_index = self.student_index
        self.slider.shift_index = self.shift_index
        self.slider.bind(value=self.on_slider_change)
        self.add_widget(self.slider)

        # Информационная панель
        self.info_layout = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(2))
        
        # Метка со значением
        self.label = Label(text=str(int(self.score_value)), font_size=sp(8), size_hint_x=None, width=dp(30), color=COLOR_TEXT_DARK)
        self.info_layout.add_widget(self.label)
        
        # Чекбокс
        self.checkbox = CheckBox(active=True) # Упрощено, всегда активен в этой реализации
        self.checkbox.student_index = self.student_index
        self.checkbox.shift_index = self.shift_index
        self.checkbox.bind(active=self.on_checkbox_active)
        self.info_layout.add_widget(self.checkbox)
        
        self.add_widget(self.info_layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_slider_change(self, instance, value):
        i = self.student_index
        j = self.shift_index
        key = f"s{j+1}"
        students[i][key] = int(value)
        self.label.text = str(int(value))
        # Цветовая индикация упрощена в этой реализации
        # В оригинале она зависит от чекбокса и значения
        # Здесь обновляется в update_status
        self.owner.update_status()

    def on_checkbox_active(self, instance, value):
        # Логика подтверждения упрощена
        # В оригинальном коде это влияло на расчет, но в Kivy-версии
        # мы используем упрощенную модель, где все значения учитываются
        pass

# === Главный экран ===
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # === Верхняя панель (Header) ===
        self.create_header(main_layout)

        # === Панель управления (Control Panel) ===
        self.create_control_panel(main_layout)

        # === Таблица (прокручиваемая) ===
        self.create_table(main_layout)

        # === Статистика группы ===
        self.create_statistics(main_layout)

        self.add_widget(main_layout)
        self.create_table_ui()
        self.update_status()

    def create_header(self, parent_layout):
        """Создает заголовок приложения."""
        header_frame = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60), padding=dp(5))
        with header_frame.canvas.before:
            Color(*COLOR_HEADER_BG)
            self.header_rect = Rectangle(pos=header_frame.pos, size=header_frame.size)
        header_frame.bind(pos=self._update_header_rect, size=self._update_header_rect)

        header_frame.add_widget(Label(text="🎓 Флагманский центр «Руднево»", font_size=sp(16), bold=True, color=COLOR_WHITE))
        header_frame.add_widget(Label(text="📊 Система оценки успеваемости студентов", font_size=sp(11), color=(0.7, 0.7, 0.7, 1)))
        parent_layout.add_widget(header_frame)

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def create_control_panel(self, parent_layout):
        """Создает панель управления."""
        ctrl_scroll = ScrollView(size_hint_y=None, height=dp(120))
        ctrl_frame = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_x=None)
        ctrl_frame.bind(minimum_width=ctrl_frame.setter('width'))

        # Группировка элементов управления
        group_frame = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(250), spacing=dp(5))
        group_frame.add_widget(Label(text="Настройки группы", font_size=sp(10), bold=True, size_hint_y=None, height=dp(20), color=COLOR_DARK, halign='left'))

        group_input_layout = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(5))
        group_input_layout.add_widget(Label(text="Название группы:", font_size=sp(9), size_hint_x=None, width=dp(100), color=COLOR_DARK, halign='left'))
        self.group_entry = TextInput(text=group_name, multiline=False, font_size=sp(9))
        group_input_layout.add_widget(self.group_entry)
        self.apply_btn = Button(text="✅ Сохранить", font_size=sp(9), size_hint_x=None, width=dp(80), background_color=COLOR_SUCCESS)
        self.apply_btn.bind(on_press=self.apply_group)
        group_input_layout.add_widget(self.apply_btn)
        group_frame.add_widget(group_input_layout)

        shifts_input_layout = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(5))
        shifts_input_layout.add_widget(Label(text="Количество смен:", font_size=sp(9), size_hint_x=None, width=dp(120), color=COLOR_DARK, halign='left'))
        self.shifts_entry = TextInput(text=str(num_shifts), multiline=False, font_size=sp(9), size_hint_x=None, width=dp(40))
        shifts_input_layout.add_widget(self.shifts_entry)
        self.update_btn = Button(text="🔄 Обновить", font_size=sp(9), size_hint_x=None, width=dp(80), background_color=COLOR_SECONDARY)
        self.update_btn.bind(on_press=self.update_shifts)
        shifts_input_layout.add_widget(self.update_btn)
        group_frame.add_widget(shifts_input_layout)
        ctrl_frame.add_widget(group_frame)

        # Кнопки действий
        actions_frame = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(800), spacing=dp(5))
        actions_frame.add_widget(Label(text="Действия", font_size=sp(10), bold=True, size_hint_y=None, height=dp(20), color=COLOR_DARK, halign='left'))
        actions_btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(3))
        self.enter_names_btn = Button(text="📝 Ввести ФИО", font_size=sp(8), background_color=COLOR_BUTTON_PRIMARY)
        self.enter_names_btn.bind(on_press=self.enter_names)
        actions_btn_layout.add_widget(self.enter_names_btn)

        self.student_chart_btn = Button(text="📊 График студентов", font_size=sp(8), background_color=COLOR_DARK)
        self.student_chart_btn.bind(on_press=self.show_student_chart)
        actions_btn_layout.add_widget(self.student_chart_btn)

        self.shift_chart_btn = Button(text="📈 График смен", font_size=sp(8), background_color=COLOR_DARK)
        self.shift_chart_btn.bind(on_press=self.show_shift_avg_chart)
        actions_btn_layout.add_widget(self.shift_chart_btn)

        self.save_btn = Button(text="💾 Сохранить данные", font_size=sp(8), background_color=COLOR_SUCCESS)
        self.save_btn.bind(on_press=self.save_current)
        actions_btn_layout.add_widget(self.save_btn)

        self.load_btn = Button(text="📂 Загрузить", font_size=sp(8), background_color=get_color_from_hex("#17a2b8"))
        self.load_btn.bind(on_press=self.load_group)
        actions_btn_layout.add_widget(self.load_btn)

        self.delete_btn = Button(text="🗑️ Удалить", font_size=sp(8), background_color=COLOR_ACCENT)
        self.delete_btn.bind(on_press=self.delete_group)
        actions_btn_layout.add_widget(self.delete_btn)

        self.export_btn = Button(text="📤 Экспорт CSV", font_size=sp(8), background_color=get_color_from_hex("#ffc107"), color=get_color_from_hex("#000000"))
        self.export_btn.bind(on_press=self.export_to_csv)
        actions_btn_layout.add_widget(self.export_btn)

        self.print_btn = Button(text="🖨️ Печать", font_size=sp(8), background_color=get_color_from_hex("#6c757d"), color=COLOR_WHITE)
        self.print_btn.bind(on_press=self.print_table)
        actions_btn_layout.add_widget(self.print_btn)
        
        actions_frame.add_widget(actions_btn_layout)
        ctrl_frame.add_widget(actions_frame)

        ctrl_scroll.add_widget(ctrl_frame)
        parent_layout.add_widget(ctrl_scroll)

    def create_table(self, parent_layout):
        """Создает область таблицы."""
        table_container = BoxLayout(orientation='vertical', size_hint_y=0.7)
        table_container.add_widget(Label(text="📋 Таблица успеваемости студентов", font_size=sp(12), bold=True, size_hint_y=None, height=dp(30), halign='left', color=COLOR_DARK))

        self.table_scroll = ScrollView()
        self.main_table = GridLayout(cols=1, spacing=dp(1), size_hint_y=None)
        self.main_table.bind(minimum_height=self.main_table.setter('height'))
        self.table_scroll.add_widget(self.main_table)
        table_container.add_widget(self.table_scroll)
        parent_layout.add_widget(table_container)

    def create_statistics(self, parent_layout):
        """Создает панель статистики."""
        stats_frame = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(5))
        with stats_frame.canvas.before:
            Color(*COLOR_DARK)
            self.stats_rect = Rectangle(pos=stats_frame.pos, size=stats_frame.size)
        stats_frame.bind(pos=self._update_stats_rect, size=self._update_stats_rect)

        stats_frame.add_widget(Label(text="📈 Средний балл по группе:", font_size=sp(11), bold=True, color=COLOR_WHITE))
        self.avg_label_global = Label(text="–", font_size=sp(14), bold=True, color=COLOR_SECONDARY)
        stats_frame.add_widget(self.avg_label_global)
        stats_frame.add_widget(Label(text="📊 Прогресс: (визуализация упрощена)", font_size=sp(9), color=(0.7, 0.7, 0.7, 1)))
        parent_layout.add_widget(stats_frame)

    def _update_stats_rect(self, instance, value):
        self.stats_rect.pos = instance.pos
        self.stats_rect.size = instance.size

    # === Создание таблицы ===
    def create_table_ui(self):
        """Создает UI элементы таблицы."""
        self.main_table.clear_widgets()
        self.name_labels = []
        self.sliders = [[] for _ in range(30)]
        self.labels = [[] for _ in range(30)]
        self.checkboxes = [[] for _ in range(30)]
        self.grade_labels = [None] * 30
        self.tb_buttons = [None] * 30
        self.work_buttons = [None] * 30

        # Заголовки таблицы
        header_frame = BoxLayout(size_hint_y=None, height=dp(30), spacing=dp(2))
        with header_frame.canvas.before:
            Color(*COLOR_DARK)
            Rectangle(pos=header_frame.pos, size=header_frame.size)
        header_frame.bind(pos=lambda instance, value: setattr(instance.canvas.before.children[-1], 'pos', value),
                        size=lambda instance, value: setattr(instance.canvas.before.children[-1], 'size', value))

        header_frame.add_widget(Label(text="👤 ФИО студента", font_size=sp(9), bold=True, size_hint_x=None, width=dp(150), color=COLOR_WHITE))
        for j in range(num_shifts):
            header_frame.add_widget(Label(text=f"Смена {j+1}", font_size=sp(9), bold=True, size_hint_x=None, width=dp(120), color=COLOR_WHITE))
        header_frame.add_widget(Label(text="Т.Б.", font_size=sp(9), bold=True, size_hint_x=None, width=dp(60), color=COLOR_WHITE))
        header_frame.add_widget(Label(text="Работа", font_size=sp(9), bold=True, size_hint_x=None, width=dp(80), color=COLOR_WHITE))
        header_frame.add_widget(Label(text="📊 Итог", font_size=sp(9), bold=True, size_hint_x=None, width=dp(80), color=COLOR_WHITE))
        self.main_table.add_widget(header_frame)

        # Строки таблицы
        for i in range(30):
            row_color = (0.9, 0.9, 0.9, 1) if i % 2 == 0 else COLOR_WHITE
            row_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(2))
            with row_layout.canvas.before:
                Color(*row_color)
                Rectangle(pos=row_layout.pos, size=row_layout.size)
            row_layout.bind(pos=lambda instance, value: setattr(instance.canvas.before.children[-1], 'pos', value),
                            size=lambda instance, value: setattr(instance.canvas.before.children[-1], 'size', value))

            # ФИО студента
            def make_name_click_handler(index):
                def handler(instance):
                    self.change_single_name(index)
                return handler
            name_label = Button(
                text=students[i]["name"],
                font_size=sp(9),
                halign='left',
                valign='middle',
                background_normal='',
                background_color=row_color,
                color=COLOR_DARK,
                text_size=(dp(140), None)
            )
            name_label.bind(on_press=make_name_click_handler(i))
            name_label.size_hint_x = None
            name_label.width = dp(150)
            row_layout.add_widget(name_label)
            self.name_labels.append(name_label)

            # Смены
            for j in range(num_shifts):
                cell_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(120), spacing=dp(1))
                with cell_layout.canvas.before:
                    Color(0.8, 0.8, 0.8, 1)
                    Rectangle(pos=cell_layout.pos, size=cell_layout.size)
                cell_layout.bind(pos=lambda instance, value: setattr(instance.canvas.before.children[-1], 'pos', value),
                                size=lambda instance, value: setattr(instance.canvas.before.children[-1], 'size', value))

                slider = Slider(min=0, max=100, value=students[i].get(f"s{j+1}", 0), step=1)
                slider.student_index = i
                slider.shift_index = j
                slider.bind(value=self.on_slider_change)
                cell_layout.add_widget(slider)
                self.sliders[i].append(slider)

                info_layout = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(2))
                initial_value = int(slider.value) if slider.value is not None else 0
                label = Label(text=str(initial_value), font_size=sp(8), size_hint_x=None, width=dp(30), color=COLOR_DARK)
                info_layout.add_widget(label)
                self.labels[i].append(label)

                checkbox = CheckBox(active=True)
                checkbox.student_index = i
                checkbox.shift_index = j
                checkbox.bind(active=self.on_checkbox_active)
                info_layout.add_widget(checkbox)
                self.checkboxes[i].append(checkbox)

                cell_layout.add_widget(info_layout)
                row_layout.add_widget(cell_layout)

            # Кнопки Т.Б. и Работа
            def make_tb_cmd(index):
                def cmd(instance):
                    students[index]["history"].append({
                        "action": "Т.Б.",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "change": -20 if not students[index]["tb_pressed"] else 20
                    })
                    students[index]["tb_pressed"] = not students[index]["tb_pressed"]
                    instance.background_color = COLOR_BUTTON_DANGER if students[index]["tb_pressed"] else COLOR_GRAY
                    self.update_status()
                return cmd

            tb_btn = Button(text="Т.Б.", font_size=sp(8), size_hint_x=None, width=dp(60))
            tb_btn.background_color = COLOR_BUTTON_DANGER if students[i]["tb_pressed"] else COLOR_GRAY
            tb_btn.bind(on_press=make_tb_cmd(i))
            row_layout.add_widget(tb_btn)
            self.tb_buttons[i] = tb_btn

            def make_work_cmd(index):
                def cmd(instance):
                    students[index]["history"].append({
                        "action": "Работоспособность",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "change": 20 if not students[index]["work_pressed"] else -20
                    })
                    students[index]["work_pressed"] = not students[index]["work_pressed"]
                    instance.background_color = COLOR_BUTTON_SUCCESS if students[index]["work_pressed"] else COLOR_GRAY
                    self.update_status()
                return cmd

            work_btn = Button(text="Работа", font_size=sp(8), size_hint_x=None, width=dp(80))
            work_btn.background_color = COLOR_BUTTON_SUCCESS if students[i]["work_pressed"] else COLOR_GRAY
            work_btn.bind(on_press=make_work_cmd(i))
            row_layout.add_widget(work_btn)
            self.work_buttons[i] = work_btn

            # Итоговый балл
            grade_label = Label(text="0.0", font_size=sp(10), bold=True, size_hint_x=None, width=dp(80), color=COLOR_DARK)
            row_layout.add_widget(grade_label)
            self.grade_labels[i] = grade_label

            self.main_table.add_widget(row_layout)

    def on_slider_change(self, instance, value):
        i = instance.student_index
        j = instance.shift_index
        key = f"s{j+1}"
        students[i][key] = int(value)
        if i < len(self.labels) and j < len(self.labels[i]):
            self.labels[i][j].text = str(int(value))
        self.update_status()

    def on_checkbox_active(self, instance, value):
        # Логика подтверждения упрощена
        pass

    # === Применение названия группы ===
    def apply_group(self, instance):
        global group_name
        new_name = self.group_entry.text.strip()
        if new_name:
            group_name = new_name
            # В Kivy заголовок окна не меняется напрямую через ScreenManager
            # self.manager.get_screen('main').name = f"main_{group_name}" 

    # === Обновление количества смен ===
    def update_shifts(self, instance):
        global num_shifts
        try:
            new_num = int(self.shifts_entry.text)
            if 1 <= new_num <= 30:
                old_num = num_shifts
                num_shifts = new_num
                init_students()
                if new_num != old_num:
                    self.rebuild_ui()
            else:
                self.show_popup("Ошибка", "Введите число от 1 до 30")
        except ValueError:
            self.show_popup("Ошибка", "Введите число")

    # === Перестроение таблицы ===
    def rebuild_ui(self):
        self.main_table.clear_widgets()
        self.create_table_ui()
        self.update_status()

    # === Изменение имени одного студента ===
    def change_single_name(self, index):
        def on_text_validate(text_input, popup):
            new_name = text_input.text.strip()
            if new_name:
                students[index]["name"] = new_name
                self.name_labels[index].text = new_name
            popup.dismiss()

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        content.add_widget(Label(text=f"Введите ФИО студента {index+1}:"))
        text_input = TextInput(text=students[index]["name"], multiline=False, font_size=sp(10))
        content.add_widget(text_input)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        cancel_btn = Button(text="Отмена")
        ok_btn = Button(text="OK", background_color=COLOR_SUCCESS)
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(ok_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="ФИО студента", content=content, size_hint=(0.8, 0.4))
        cancel_btn.bind(on_press=popup.dismiss)
        ok_btn.bind(on_press=lambda x: on_text_validate(text_input, popup))
        text_input.bind(on_text_validate=lambda x: on_text_validate(text_input, popup)) # Enter тоже работает
        popup.open()

    # === Ввод ФИО ===
    def enter_names(self, instance):
        def create_name_input(i, scroll_layout):
            input_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
            input_layout.add_widget(Label(text=f"{i+1}:", size_hint_x=None, width=dp(30), halign='right', color=COLOR_DARK))
            ti = TextInput(text=students[i]["name"], multiline=False, font_size=sp(9))
            ti.student_index = i
            input_layout.add_widget(ti)
            scroll_layout.add_widget(input_layout)
            return ti

        def on_popup_dismiss(popup, text_inputs):
            for ti in text_inputs:
                if ti.text.strip():
                    students[ti.student_index]["name"] = ti.text.strip()
                    self.name_labels[ti.student_index].text = ti.text.strip()
            popup.dismiss()

        content = BoxLayout(orientation='vertical')
        scroll = ScrollView()
        scroll_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        
        text_inputs = []
        for i in range(30):
            ti = create_name_input(i, scroll_layout)
            text_inputs.append(ti)
        
        scroll.add_widget(scroll_layout)
        content.add_widget(scroll)

        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_btn = Button(text="Отмена")
        ok_btn = Button(text="Сохранить", background_color=COLOR_SUCCESS)
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(ok_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Ввод ФИО студентов", content=content, size_hint=(0.9, 0.9))
        cancel_btn.bind(on_press=popup.dismiss)
        ok_btn.bind(on_press=lambda x: on_popup_dismiss(popup, text_inputs))
        popup.open()

    # === Обновление статуса ===
    def update_status(self, *args):
        """Обновляет статус (баллы, цвета) в UI. Аргументы для Clock.trigger."""
        total_scores = []
        shift_sums = [0] * num_shifts
        shift_counts = [0] * num_shifts
        
        for i in range(30):
            student = students[i]
            # Обновление цветов и значений в ячейках смен
            for j in range(num_shifts):
                val = int(self.sliders[i][j].value)
                is_checked = self.checkboxes[i][j].active
                if is_checked:
                    if i < len(self.labels) and j < len(self.labels[i]):
                        if val >= 80:
                            self.labels[i][j].color = COLOR_SUCCESS
                        elif val >= 60:
                            self.labels[i][j].color = COLOR_WARNING
                        else:
                            self.labels[i][j].color = COLOR_DANGER
                else:
                    if i < len(self.labels) and j < len(self.labels[i]):
                        self.labels[i][j].color = COLOR_TEXT_DARK # Черный

            # Расчет итогового балла студента
            completed_values = [int(self.sliders[i][j].value) for j in range(num_shifts) if self.checkboxes[i][j].active]
            base_avg = sum(completed_values) / len(completed_values) if completed_values else 0
            final_score = base_avg
            if student["tb_pressed"]:
                final_score -= 20
            if student["work_pressed"]:
                final_score += 20
            final_score = max(0, min(100, final_score))
            student['total_score'] = final_score

            # Обновление итогового балла и его цвета
            if i < len(self.grade_labels):
                self.grade_labels[i].text = f"{final_score:.1f}"
                if final_score >= 80:
                    self.grade_labels[i].color = COLOR_SUCCESS
                elif final_score >= 60:
                    self.grade_labels[i].color = COLOR_WARNING
                elif final_score > 0:
                    self.grade_labels[i].color = COLOR_DANGER
                else:
                    self.grade_labels[i].color = COLOR_TEXT_DARK # Черный

            total_scores.append(final_score)

        # Обновление среднего балла по группе
        avg_group = sum(total_scores) / len(total_scores) if total_scores else 0
        self.avg_label_global.text = f"{avg_group:.2f}"
        if avg_group >= 80:
            self.avg_label_global.color = COLOR_SUCCESS
        elif avg_group >= 60:
            self.avg_label_global.color = COLOR_WARNING
        elif avg_group > 0:
            self.avg_label_global.color = COLOR_ACCENT
        else:
            self.avg_label_global.color = COLOR_TEXT_DARK # Черный

    # === Сохранение ===
    def save_current(self, instance):
        if group_name == "Группа" and all(s["name"].startswith("Студент") for s in students):
            self.show_popup("Сохранение", "Сначала введите название и ФИО.")
            return
            
        filename = os.path.join(DATA_DIR, f"{group_name}.json")
        data = {
            "group_name": group_name,
            "num_shifts": num_shifts,
            "students": students,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.show_popup("Сохранение", f"Группа '{group_name}' сохранена.", COLOR_SUCCESS)
        except Exception as e:
            self.show_popup("Ошибка", f"Не удалось сохранить: {e}", COLOR_DANGER)

    # === Загрузка группы ===
    def load_group(self, instance):
        try:
            files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
            if not files:
                self.show_popup("Загрузка", "Нет сохраненных групп")
                return

            def on_file_selected(selected_filename, popup):
                popup.dismiss()
                if selected_filename:
                    filepath = os.path.join(DATA_DIR, f"{selected_filename}.json")
                    if os.path.exists(filepath):
                        try:
                            with open(filepath, "r", encoding="utf-8") as f:
                                data = json.load(f)
                            global group_name, num_shifts
                            group_name = data["group_name"]
                            # Убедимся, что num_shifts в допустимых пределах
                            loaded_num_shifts = data["num_shifts"]
                            num_shifts = max(1, min(30, loaded_num_shifts)) 
                            
                            global students
                            students = data["students"]
                            
                            self.group_entry.text = group_name
                            self.shifts_entry.text = str(num_shifts)
                            self.rebuild_ui()
                            self.show_popup("Загрузка", f"Группа '{group_name}' загружена.", COLOR_SUCCESS)
                        except Exception as e:
                            self.show_popup("Ошибка", f"Не удалось загрузить: {e}", COLOR_DANGER)
                    else:
                        self.show_popup("Ошибка", "Файл не найден", COLOR_DANGER)

            self._create_file_selection_popup("Выберите группу для загрузки", files, on_file_selected)

        except Exception as e:
            self.show_popup("Ошибка", f"Не удалось загрузить: {e}", COLOR_DANGER)

    # === Удаление группы ===
    def delete_group(self, instance):
        try:
            files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
            if not files:
                self.show_popup("Удаление", "Нет сохраненных групп")
                return

            def confirm_delete(selected_filename, popup):
                popup.dismiss()
                def perform_delete(confirm_popup):
                    confirm_popup.dismiss()
                    filepath = os.path.join(DATA_DIR, f"{selected_filename}.json")
                    try:
                        os.remove(filepath)
                        self.show_popup("Удаление", f"Группа '{selected_filename}' удалена.", COLOR_SUCCESS)
                    except Exception as e:
                        self.show_popup("Ошибка", f"Не удалось удалить: {e}", COLOR_DANGER)

                confirm_content = BoxLayout(orientation='vertical', spacing=dp(10))
                confirm_content.add_widget(Label(text=f"Вы уверены, что хотите удалить группу '{selected_filename}'?"))
                btn_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
                cancel_btn = Button(text="Отмена")
                delete_btn = Button(text="Удалить", background_color=COLOR_DANGER)
                btn_layout.add_widget(cancel_btn)
                btn_layout.add_widget(delete_btn)
                confirm_content.add_widget(btn_layout)

                confirm_popup = Popup(title="Подтверждение", content=confirm_content, size_hint=(0.6, 0.4))
                cancel_btn.bind(on_press=confirm_popup.dismiss)
                delete_btn.bind(on_press=lambda x: perform_delete(confirm_popup))
                confirm_popup.open()

            self._create_file_selection_popup("Выберите группу для удаления", files, confirm_delete, btn_color=COLOR_ACCENT)

        except Exception as e:
            self.show_popup("Ошибка", f"Не удалось показать список: {e}", COLOR_DANGER)

    def _create_file_selection_popup(self, title, filenames, callback, btn_color=COLOR_SECONDARY):
        """Вспомогательная функция для создания попапа выбора файла."""
        content = BoxLayout(orientation='vertical')
        scroll = ScrollView()
        files_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        files_layout.bind(minimum_height=files_layout.setter('height'))

        for filename in filenames:
            btn = Button(text=filename[:-5], size_hint_y=None, height=dp(40), background_color=btn_color)
            btn.file_name = filename[:-5]
            # Используем фабричную функцию для правильного захвата filename
            btn.bind(on_press=lambda x: callback(x.file_name, popup))
            files_layout.add_widget(btn)

        scroll.add_widget(files_layout)
        content.add_widget(scroll)

        close_btn = Button(text="Закрыть", size_hint_y=None, height=dp(40))
        content.add_widget(close_btn)

        popup = Popup(title=title, content=content, size_hint=(0.8, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    # === Экспорт в CSV ===
    def export_to_csv(self, instance):
        if group_name == "Группа" and all(s["name"].startswith("Студент") for s in students):
            self.show_popup("Экспорт", "Сначала введите название и ФИО.")
            return
        # В Kivy нет стандартного диалога сохранения файла, сохраняем в папку groups
        filename = os.path.join(DATA_DIR, f"{group_name}_export.csv")
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                headers = ["ФИО", "Средний балл"]
                for j in range(num_shifts):
                    headers.append(f"Смена {j+1}")
                headers.extend(["Т.Б.", "Работоспособность"])
                writer.writerow(headers)
                for student in students:
                    row = [student["name"], f"{student['total_score']:.1f}"]
                    for j in range(num_shifts):
                        key = f"s{j+1}"
                        val = student.get(key, "")
                        row.append(val if val is not None else "")
                    row.append("Да" if student["tb_pressed"] else "Нет")
                    row.append("Да" if student["work_pressed"] else "Нет")
                    writer.writerow(row)
            self.show_popup("Экспорт", f"Данные экспортированы в {filename}", COLOR_SUCCESS)
        except Exception as e:
            self.show_popup("Ошибка", f"Не удалось экспортировать: {e}", COLOR_DANGER)

    # === Печать таблицы (вывод в Popup) ===
    def print_table(self, instance):
        # Формирование текста для "печати"
        content_text = "ФИО".ljust(20)
        for j in range(num_shifts):
            content_text += f"См.{j+1}".ljust(8)
        content_text += "Т.Б.    Работа  Итог\n"
        content_text += "-" * len(content_text) + "\n"

        scores = [s['total_score'] for s in students]
        for i, student in enumerate(students):
            line = student["name"][:20].ljust(20)
            for j in range(num_shifts):
                key = f"s{j+1}"
                val = student.get(key, "")
                line += (str(val) if val is not None else "-").ljust(8)
            line += ("Да" if student["tb_pressed"] else "Нет").ljust(8)
            line += ("Да" if student["work_pressed"] else "Нет").ljust(8)
            line += f"{scores[i]:.1f}\n"
            content_text += line

        total_scores = [s for s in scores if s > 0]
        avg_group = sum(total_scores) / len(total_scores) if total_scores else 0
        content_text += f"\nСредний балл по группе: {avg_group:.2f}\n"

        # Отображение в Popup
        content = BoxLayout(orientation='vertical')
        scroll = ScrollView()
        # Используем один Label с большим текстом вместо множества маленьких
        text_label = Label(
            text=content_text,
            # font_name='RobotoMono', # Убираем, так как шрифт может отсутствовать
            halign='left',
            valign='top',
            text_size=(None, None), # Отключаем автоматический перенос
            size_hint_y=None,
            font_size=sp(10) # Можно настроить размер шрифта,
            # color=COLOR_DARK # Цвет текста
        )
        # Рассчитываем высоту Label в зависимости от содержимого
        # Это приближение, может потребоваться корректировка
        text_label.bind(texture_size=lambda instance, value: setattr(instance, 'size', value))
        
        scroll.add_widget(text_label)
        content.add_widget(scroll)

        close_btn = Button(text="Закрыть", size_hint_y=None, height=dp(40))
        content.add_widget(close_btn)

        popup = Popup(title="Печать таблицы", content=content, size_hint=(0.9, 0.9))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


    # === График: успеваемость студентов (заглушка) ===
    def show_student_chart(self, instance):
        # Заглушка с улучшенным сообщением
        self.show_popup("График", "График студентов. Функционал графиков требует дополнительной настройки (kivy.garden.graph или экспорт данных). Данные готовы для экспорта.", COLOR_WARNING)

    # === График: средний балл за смену (заглушка) ===
    def show_shift_avg_chart(self, instance):
        # Заглушка с улучшенным сообщением
        self.show_popup("График", "График средних баллов по сменам. Функционал графиков требует дополнительной настройки (kivy.garden.graph или экспорт данных). Данные готовы для экспорта.", COLOR_WARNING)

    # === Всплывающее окно ===
    def show_popup(self, title, message, color=COLOR_SECONDARY):
        """Показывает всплывающее окно с сообщением."""
        # Создаем попап с сообщением
        popup = Popup(
            title=title,
            content=Label(text=message, text_size=(dp(300), None)), #, color=COLOR_DARK), # Ограничиваем ширину текста
            size_hint=(0.8, 0.4),
            separator_color=color # kivy 2.0+
        )
        popup.open()

# === Приложение ===
class StudentProgressApp(App):
    def build(self):
        # Установим минимальный размер окна для desktop версии
        # Это поможет лучше видеть адаптивность
        Window.size = (1400, 850)
        Window.minimum_width, Window.minimum_height = 1000, 700
        
        # Инициализируем список студентов
        init_students()
        # Создаем менеджер экранов
        sm = ScreenManager()
        # Добавляем главный экран
        sm.add_widget(MainScreen(name='main'))
        # Возвращаем корневой виджет приложения
        return sm

if __name__ == '__main__':
    StudentProgressApp().run()

