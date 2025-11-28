from nicegui import ui

class VirtualKeyboard:
    RU_LAYOUT = [
        list("йцукенгшщзхъ"),
        list("фывапролджэ"),
        ["Shift"] + list("ячсмитьбю") + ["⌫"],
        ["EN", "Пробел", "⌨", "123"],
    ]

    EN_LAYOUT = [
        list("qwertyuiop"),
        list("asdfghjkl"),
        ["Shift"] + list("zxcvbnm") + ["⌫"],
        ["RU", "Space", "⌨", "123"],
    ]

    NUM_LAYOUT = [
        list("1234567890"),
        list("-/:;()$&@\""),
        ["#", "+", "=",".",",", "⌫"],
        ["RU", "Space", "⌨"],
    ]

    def __init__(self):
        self.current_layout = "RU"
        self.shift_active = False
        self.active_field = None

        # клавиатура
        #self.keyboard_area = ui.column().classes(
        #    "hidden fixed bottom-0 left-0 w-full z-50 virtual-keyboard"
        #)
        self.keyboard_area = ui.column().classes("fixed bottom-0 left-0 w-full z-50 virtual-keyboard")
        # встроенный CSS для плавного выезда
        ui.html("""
        <style>
        .virtual-keyboard {
    transform: translateY(100%); /* внизу */
    transition: transform 0.3s ease-in-out;
}

.virtual-keyboard.show {
    transform: translateY(0); /* выезжает */
}
        </style>
        """, sanitize=False)
        
    # подключение input
    def attach(self, input_field: ui.input):
        input_field.on("focus", lambda e, f=input_field: self._activate_field(f))
        return input_field

    def _activate_field(self, field: ui.input):
        self.active_field = field
        self.show()

    # обработка клавиш
    def press_key(self, key: str):
        if not self.active_field:
            return
        if key == "⌫":
            self.active_field.value = self.active_field.value[:-1]
        elif key in ("Пробел", "Space"):
            self.active_field.value += " "
        elif key == "⌨":
            self.hide()
        elif key == "Shift":
            self.shift_active = not self.shift_active
            self.render()
        else:
            char = key.upper() if self.shift_active else key
            self.active_field.value += char
            if self.shift_active:
                self.shift_active = False
                self.render()

    # переключение раскладки
    def switch_layout(self, layout: str):
        self.current_layout = layout
        self.render()

    # показать клавиатуру
    def show(self):
        self.render()
        self.keyboard_area.classes(add="show")
        # добавить паддинг снизу, чтобы клавиатура не перекрывала поля
        ui.run_javascript("""
            (function() {
                const keyboard = document.querySelector('.virtual-keyboard');
                const page = document.querySelector('.q-page');
                if (!keyboard || !page) return;

                const kbHeight = keyboard.offsetHeight || 250;
                page.style.paddingBottom = kbHeight + 'px';

                const field = document.activeElement;
                if (field) {
                    const rect = field.getBoundingClientRect();
                    if (rect.bottom > window.innerHeight - kbHeight) {
                        window.scrollBy({ top: rect.bottom - (window.innerHeight - kbHeight) + 20, behavior: 'smooth' });
                    }
                }
            })();
        """)

    # скрыть клавиатуру
    def hide(self):
        self.keyboard_area.classes(remove="show")
        # убрать паддинг после анимации
        ui.run_javascript("""
            setTimeout(() => {
                const page = document.querySelector('.q-page');
                if (page) page.style.paddingBottom = '0px';
            }, 300);
        """)

    # рендер клавиатуры
    def render(self):
        layouts = {
            "RU": self.RU_LAYOUT,
            "EN": self.EN_LAYOUT,
            "123": self.NUM_LAYOUT,
        }
        layout = layouts[self.current_layout]
        self.keyboard_area.clear()

        with self.keyboard_area:
            with ui.column().classes("w-full p-3 bg-grey-2 rounded-t-xl shadow-2xl gap-2"):
                for row in layout:
                    with ui.row().classes("w-full gap-2"):
                        for key in row:
                            grow = (
                                "flex-[2]" if key in ("Shift", "⌫") else
                                "flex-[5]" if key in ("Пробел", "Space") else
                                "flex-[1]"
                            )
                            if key in ("RU", "EN", "123"):
                                ui.button(
                                    key,
                                    on_click=lambda k=key: self.switch_layout(k)
                                ).classes(
                                    f"{grow} min-h-[60px] rounded-lg "
                                    "bg-indigo-300 hover:bg-indigo-400 text-black shadow-sm"
                                )
                            else:
                                display = key.upper() if self.shift_active else key
                                ui.button(
                                    display,
                                    on_click=lambda k=key: self.press_key(k)
                                ).classes(
                                    f"{grow} min-h-[60px] rounded-lg "
                                    "bg-grey-3 hover:bg-grey-4 text-black shadow-sm"
                                )