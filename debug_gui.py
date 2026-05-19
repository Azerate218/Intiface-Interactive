import tkinter as tk
from tkinter import font as tkfont
from collections.abc import Callable, Mapping


class DictWindow:
    def __init__(
        self,
        data: dict,
        *,
        always_on_top: bool = False,
        font_size: int = 12,
        borderless: bool = False,
        text_color: str = "black",
        text_shadow_color: str | None = None,
        text_shadow_thickness: int = 1,
        background_transparency: bool = False,
    ) -> None:
        if not isinstance(data, Mapping):
            raise TypeError("DictWindow expects a dict.")

        self.data = data
        self.always_on_top = always_on_top
        self.font_size = font_size
        self.borderless = borderless
        self.text_color = text_color
        self.text_shadow_color = text_shadow_color
        self.text_shadow_thickness = max(0, text_shadow_thickness)
        self.background_transparency = background_transparency
        self.background_color = "#010203" if self.background_transparency else None
        self.drag_start = {"x": 0, "y": 0}
        self._auto_update_callback: Callable[[], Mapping | None] | None = None
        self._auto_update_interval_ms = 100
        self._auto_update_job: str | None = None
        self._closed = False

        self.window = tk.Tk()
        self.window.title("Dictionary")
        self.window.attributes("-topmost", self.always_on_top)
        self._set_background_transparency()
        self.window.overrideredirect(self.borderless)
        self.window.bind("<Escape>", lambda _event: self.close())
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        self.font = tkfont.Font(family="Consolas", size=self.font_size)
        self.text = self._format_dict(self.data)
        self.canvas = self._build_canvas()

        self._bind_canvas()
        self._fit_to_contents()

    def update(self, data: Mapping | None = None) -> None:
        self.update_dict(data)

    def update_dict(self, data: Mapping | None = None) -> None:
        if data is None:
            data = self.data

        if not isinstance(data, Mapping):
            raise TypeError("update_dict() expects a dict.")

        text = self._format_dict(data)
        if text == self.text:
            self.data = data
            return

        self.data = data
        self.text = text
        self.canvas.destroy()
        self.canvas = self._build_canvas()
        self._bind_canvas()
        self._fit_to_contents()

    def auto_update(
        self,
        callback: Callable[[], Mapping | None] | None = None,
        *,
        interval_ms: int = 100,
    ) -> "DictWindow":
        self.stop_auto_update()
        self._auto_update_callback = callback
        self._auto_update_interval_ms = max(1, interval_ms)
        self._run_auto_update()
        return self

    def stop_auto_update(self) -> "DictWindow":
        if self._auto_update_job is not None:
            try:
                self.window.after_cancel(self._auto_update_job)
            except tk.TclError:
                pass

        self._auto_update_job = None
        return self

    def close(self) -> None:
        self._closed = True
        self.stop_auto_update()
        try:
            self.window.destroy()
        except tk.TclError:
            pass

    def _bind_canvas(self) -> None:
        self.canvas.bind("<ButtonPress-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag_window)

    def _run_auto_update(self) -> None:
        if self._closed:
            return

        data = self._auto_update_callback() if self._auto_update_callback else None
        self.update_dict(data)
        self._auto_update_job = self.window.after(
            self._auto_update_interval_ms,
            self._run_auto_update,
        )

    def _format_dict(self, data: Mapping, indent_size: int = 4) -> str:
        lines = []

        def add_dict(current: Mapping, level: int) -> None:
            indent = " " * (level * indent_size)

            for key, value in current.items():
                if isinstance(value, Mapping):
                    lines.append(f"{indent}{key}:")
                    add_dict(value, level + 1)
                else:
                    lines.append(f"{indent}{key}: {value}")

        add_dict(data, 0)
        return "\n".join(lines)

    def _set_background_transparency(self) -> None:
        if not self.background_color:
            return

        self.window.configure(bg=self.background_color)

        try:
            self.window.attributes("-transparentcolor", self.background_color)
        except tk.TclError:
            pass

    def _build_canvas(self) -> tk.Canvas:
        x_padding = 2
        y_padding = 2
        shadow_thickness = self.text_shadow_thickness if self.text_shadow_color else 0
        line_height = self.font.metrics("linespace")
        lines = self.text.splitlines() or [""]
        width = (
            max(self.font.measure(line) for line in lines)
            + x_padding * 2
            + shadow_thickness * 2
        )
        height = line_height * len(lines) + y_padding * 2 + shadow_thickness * 2

        canvas = tk.Canvas(
            self.window,
            width=width,
            height=height,
            bg=self.background_color or self.window.cget("bg"),
            bd=0,
            highlightthickness=0,
        )
        canvas.pack()

        text_x = x_padding + shadow_thickness
        text_y = y_padding + shadow_thickness

        if self.text_shadow_color and shadow_thickness:
            for x_offset in range(-shadow_thickness, shadow_thickness + 1):
                for y_offset in range(-shadow_thickness, shadow_thickness + 1):
                    if x_offset == 0 and y_offset == 0:
                        continue

                    canvas.create_text(
                        text_x + x_offset,
                        text_y + y_offset,
                        text=self.text,
                        font=self.font,
                        fill=self.text_shadow_color,
                        anchor="nw",
                    )

        canvas.create_text(
            text_x,
            text_y,
            text=self.text,
            font=self.font,
            fill=self.text_color,
            anchor="nw",
        )

        return canvas

    def _fit_to_contents(self) -> None:
        self.window.update_idletasks()
        self.window.geometry(
            f"{self.window.winfo_reqwidth()}x{self.window.winfo_reqheight()}"
        )

    def _start_drag(self, event: tk.Event) -> None:
        self.drag_start["x"] = event.x
        self.drag_start["y"] = event.y

    def _drag_window(self, event: tk.Event) -> None:
        self.window.geometry(
            f"+{event.x_root - self.drag_start['x']}+{event.y_root - self.drag_start['y']}"
        )

    def show(self) -> "DictWindow":
        self.window.mainloop()
        return self


def show_dict_window(
    data: dict,
    *,
    always_on_top: bool = False,
    font_size: int = 12,
    borderless: bool = False,
    text_color: str = "black",
    text_shadow_color: str | None = None,
    text_shadow_thickness: int = 1,
    background_transparency: bool = False,
) -> tk.Tk:
    dict_window = DictWindow(
        data,
        always_on_top=always_on_top,
        font_size=font_size,
        borderless=borderless,
        text_color=text_color,
        text_shadow_color=text_shadow_color,
        text_shadow_thickness=text_shadow_thickness,
        background_transparency=background_transparency,
    )
    dict_window.show()
    return dict_window.window


if __name__ == "__main__":
    test_dict = {
        "test_int": 123,
        "test_str": "abc",
        "test_list": [1, 2, 3],
        "test_dict": {"a": 1, "b": 2},
    }
    dct_window = DictWindow(
        test_dict,
        always_on_top=True,
        borderless=True,
        text_color="lime",
        text_shadow_color="black",
        text_shadow_thickness=2,
        background_transparency=True,
    )

    def update_test_dict() -> None:
        test_dict["test_int"] += 1

    dct_window.auto_update(update_test_dict, interval_ms=100).show()