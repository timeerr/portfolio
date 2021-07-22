

class GradientStyle:
    @staticmethod
    def get(object_name, color1, color2):
        return (
            """#{} {{
            background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.273, stop:0 {}, stop:1 {});
            border-radius: 15px}}""".format(object_name, color1, color2))


class LinearStyle:
    @staticmethod
    def get(object_name, color):
        return (
            """#{} {{
            background-color: {};
            border-radius: 15px}}
            """.format(object_name, color))


class DistributionButtonStyle:
    colors = {1: "#325059", 2: "#3C6361", 3: "#65B585"}

    @classmethod
    def get(cls, color_num: int):
        if color_num not in range(1, 4):
            raise ValueError(f"{color_num=} must be in {list(range(1,4))}")
        color = cls.colors[color_num]
        return (
            f"""QPushButton {{
            background-color: {color} ; border-width: 2px; border-radius: 15px;
            border-color: {color}; padding-top:8px; padding-bottom:8px}}

            QPushButton::hover {{
            background-color: {color}; border-width: 1px; border-radius: 15px;
            border-color: white; border-style: solid; padding-top:8px; padding-bottom:8px}}

            QPushButton::checked{{
            background-color: white; border-width: 2px; border-radius: 15px;
            border-color: {color} ; border-style: solid; padding-top:8px; padding-bottom:8px;
            color: {color}}}
            """
        )
