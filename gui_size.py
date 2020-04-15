class WindowSize(object):
    def __init__(self):
        # TODO high dip
        self.main_width = 800
        self.main_padding = (8, 10)

        self.editor_height = 48
        self.editor_font_size = 21

        self.result_margin_top = 10


class ItemSize(object):
    def __init__(self):
        self.height = 48
        self.width = 100

        self.icon_size = (32, 32)
        self.icon_margin = (8, 8)

        # main title
        self.font_size = 12
        self.font_weight = 60
        self.title_height = 24
        self.title_margin = (self.height, 4)

        # subtitle
        self.sub_font_size = 9
        self.sub_title_height = 16

        # menu drop icon
        self.drop_size = (24, 24)
        self.drop_margin = (12, 12)

        # menu item
        self.menu_height = 24
        self.menu_left_margin = 6


class GuiSize(object):
    def __init__(self):
        self.main = WindowSize()
        self.item = ItemSize()
