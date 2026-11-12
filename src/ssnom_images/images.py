import gwyfile
import matplotlib.pyplot as plt

cmap_table = {
    'A': 'afmhot',
    'Z': 'gray',
    'P': 'viridis',
}

unit_table = {
    'Z': ('nm', 1e9),
    'O': ('mV', 1),
    'P': ('Rad', 1),
}


class GwyddionFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = self.read_gwyddion_file()
        self.channels = gwyfile.util.get_datafields(self.file)

    def read_gwyddion_file(self):
        return gwyfile.load(self.filepath)

    def plot_image(self,
                   channels: list | None,
                   ax=None,
                   scale_bar_len: float = 100e-9,
                   scale_bar_color: str = 'white',
                   scale_bar_label=True):

        plots = {}

        if channels is None:
            channels = list(self.channels.keys())
        # get pixel size from the Gwyddion file
        xreal = self.file['/0/data']['xreal']
        xres = self.file['/0/data']['xres']
        pixel_size = xreal / xres
        for channel in channels:
            data = self.channels[channel].data
            unit = next(value for key, value in unit_table.items()
                        if key in channel)
            cmap = next(value for key, value in cmap_table.items()
                        if key in channel) 
            fig, ax = plt.subplots(figsize=(4, 3))
            im = ax.imshow(data*unit[1], cmap=cmap)
            ax.set_title(channel)
            ax.set_xticks([])
            ax.set_yticks([])
            cbar = fig.colorbar(im, ax=ax)
            cbar.set_label(f"{channel} ({unit[0]})")

            # scale bar
            img_h, img_w = data.shape
            scale_bar_len_px = int(scale_bar_len / pixel_size)
            bar_x = img_w * 0.8
            bar_y = img_h * 0.92
            bar_h = img_h * 0.012

            ax.add_patch(plt.Rectangle((bar_x, bar_y),
                                       scale_bar_len_px, bar_h,
                                       color=scale_bar_color))

            if scale_bar_label:
                ax.text(bar_x + scale_bar_len_px / 2, bar_y - bar_h * 2,
                        f"{scale_bar_len*1e9:.0f} nm", color=scale_bar_color,
                        ha='center', va='bottom', fontsize=8)

            plt.show()

            plots[channel] = (fig, ax)     
        return plots

    def add_points(self, plots, points: dict, color='red', size: int = 10,
                   label=True):
        for fig, ax in plots.values():
            for loc, value in points.items():
                x_phys, y_phys = value
                x_offset, y_offset = (self.file['/0/data']['xoff'],
                                      self.file['/0/data']['yoff'])
                x_res, y_res = (self.file['/0/data']['xres'],
                                self.file['/0/data']['yres'])
                x_real, y_real = (self.file['/0/data']['xreal'],
                                  self.file['/0/data']['yreal'])
                x_px = int((x_phys - x_offset) / x_real * x_res)
                y_px = int((y_phys - y_offset) / y_real * y_res)
                ax.scatter(x_px, y_px, color=color, s=size)
                if label:
                    ax.annotate(loc, (x_px, y_px), xytext=(0, 5),
                                textcoords='offset points', color=color,
                                fontsize=8)
            plt.show()
