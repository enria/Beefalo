size_base=2
font_size_base=1

class WindowSize(object):
    def __init__(self):
        # TODO high dip
        self.main_width = 800*size_base
        self.main_padding = (8*size_base, 10*size_base)

        self.editor_height = 48*size_base
        self.editor_font_size = 21*font_size_base

        self.result_margin_top = 10*size_base


class ItemSize(object):
    def __init__(self):
        self.height = 48*size_base
        self.width = 100*size_base

        self.icon_size = (32*size_base, 32*size_base)
        self.icon_margin = (8*size_base, 8*size_base)

        # main title
        self.font_size = 12*font_size_base
        self.font_weight = 60
        self.title_height = 24*size_base
        self.title_margin = (self.height, 4*size_base)

        # subtitle
        self.sub_font_size = 9*font_size_base
        self.sub_title_height = 16*size_base

        # menu drop icon
        self.drop_size = (24*size_base, 24*size_base)
        self.drop_margin = (12*size_base, 12*size_base)

        # menu item
        self.menu_height = 24*size_base
        self.menu_left_margin = 6*size_base


class GuiSize(object):
    def __init__(self):
        self.main = WindowSize()
        self.item = ItemSize()
