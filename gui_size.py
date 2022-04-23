size_base = 1
font_size_base = 1


class SizeScale(object):
    def __init__(self, screen_pix):
        base_size = (1920/1.2, 1080/1.2)
        self.g = max(screen_pix[0] / base_size[0], screen_pix[1] / base_size[1])
        self.f = self.g


class WindowSize(object):
    def __init__(self, size_scale: SizeScale):
        # TODO high dip
        s = size_scale
        self.main_width = 800 * s.g
        self.main_padding = (8 * s.g, 10 * s.g)

        self.editor_height = 48 * s.g
        self.editor_font_size = 30 * s.f

        self.result_margin_top = 10 * s.g


class ItemSize(object):
    def __init__(self, size_scale: SizeScale):
        s = size_scale

        self.height = 48 * s.g
        self.width = 100 * s.g

        self.icon_size = (32 * s.g, 32 * s.g)
        self.icon_margin = (8 * s.g, 8 * s.g)

        # main title
        self.font_size = 18 * s.f
        self.font_weight = 60
        self.title_height = 24 * s.g
        self.title_margin = (self.height, 4 * s.g)

        # subtitle
        self.sub_font_size = 12 * s.f
        self.sub_title_height = 16 * s.g

        # menu drop icon
        self.drop_size = (24 * s.g, 24 * s.g)
        self.drop_margin = (12 * s.g, 12 * s.g)

        # menu item
        self.menu_height = 24 * s.g
        self.menu_left_margin = 6 * s.g


class GuiSize(object):
    def __init__(self):
        self.main = WindowSize()
        self.item = ItemSize()
