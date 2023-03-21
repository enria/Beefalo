size_base = 1
font_size_base = 1


class SizeScale(object):
    def __init__(self, screen_pix):
        base_size = (1920/1, 1080/1)
        x = max(screen_pix[0] / base_size[0], screen_pix[1] / base_size[1])
        self.g = x**(1/3) # 非线性的缩放方式
        # print(screen_pix, self.g)
        self.f = self.g


class WindowSize(object):
    def __init__(self, size_scale: SizeScale):
        # TODO high dip
        s = size_scale
        self.main_width = int(700 * s.g)
        self.main_padding = (int(10 * s.g), int(10 * s.g))

        self.editor_height = 48 * s.g
        self.editor_font_size = 28 * s.f

        self.result_margin_top = 10 * s.g


class ItemSize(object):
    def __init__(self, size_scale: SizeScale):
        s = size_scale

        self.height = int(48 * s.g)
        self.width = int(100 * s.g)

        self.icon_size = (int(32 * s.g), int(32 * s.g))
        self.device_ratio = 2
        self.icon_margin = (int(8 * s.g), int(8 * s.g))

        # main title
        self.font_size = int(18 * s.f)
        self.font_weight = 60
        self.title_height = int(24 * s.g)
        self.title_margin = (self.height, int(4 * s.g))

        # subtitle
        self.sub_font_size = int(13 * s.f)
        self.sub_title_height = int(18 * s.g)

        # menu drop icon
        self.drop_size = (int(24 * s.g), int(24 * s.g))
        self.drop_margin = (int(18 * s.g), int(12 * s.g))

        # menu item
        self.menu_height = int(24 * s.g)
        self.menu_left_margin = int(6 * s.g)


class GuiSize(object):
    def __init__(self):
        self.main = WindowSize()
        self.item = ItemSize()
