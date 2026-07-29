import matplotlib
matplotlib.use('QtAgg')

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QSizePolicy, QFileDialog, QMessageBox
from PySide6.QtCore import Signal
import numpy as np

from src.core.config import config_manager
from src.core.logger import log

class MathPlotCanvas(FigureCanvas):
    """A premium Matplotlib canvas integrated into PySide6.
    
    Supports:
    - Hover crosshair cursor & coordinate overlay.
    - Double click to reset zoom.
    - Dynamic light/dark theme color adjustments.
    - Methods to Save PNG, Zoom In, Zoom Out, and Reset Zoom.
    """
    coordinates_updated = Signal(str) # Emits formatted coordinate string if parent wants it

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.updateGeometry()

        # Cache for original limits to support reset zoom
        self.orig_xlim = None
        self.orig_ylim = None

        # Crosshair Lines
        self.cross_h = self.ax.axhline(0, color='#94a3b8', linestyle=':', alpha=0.5)
        self.cross_v = self.ax.axvline(0, color='#94a3b8', linestyle=':', alpha=0.5)
        self.cross_h.set_visible(False)
        self.cross_v.set_visible(False)
        
        # Coordinate overlay text
        self.coord_text = self.ax.text(
            0.02, 0.96, "",
            transform=self.ax.transAxes,
            color="#94a3b8",
            fontsize=9,
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#0f172a', alpha=0.8, edgecolor='none')
        )
        self.coord_text.set_visible(False)

        # Apply theme-appropriate colors initially
        self.apply_theme_colors()

        # Connect events
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.mpl_connect('axes_leave_event', self.on_mouse_leave)
        self.mpl_connect('button_press_event', self.on_button_press)

    def apply_theme_colors(self) -> None:
        """Applies theme background and foreground styling to the Matplotlib chart."""
        theme = config_manager.get("theme")
        
        if theme == "dark":
            bg_color = "#141B2D"       # Card panel background
            fg_color = "#C9D1E3"       # Secondary text / labels
            grid_color = "#4A5675"     # Major grid lines
            minor_grid = "#2B3245"     # Minor grid lines
            axis_bg = "#0B1020"        # Premium Oscilloscope background
            bbox_color = "#111827"
        else:
            bg_color = "#FFFFFF"       # White background
            fg_color = "#0F172A"       # Slate text
            grid_color = "#CBD5E1"     # Soft gray grid lines
            minor_grid = "#E2E8F0"
            axis_bg = "#F8FAFC"        # Soft off-white plot area
            bbox_color = "#F1F5F9"

        self.fig.patch.set_facecolor(bg_color)
        self.ax.set_facecolor(axis_bg)
        
        self.ax.grid(True, which='major', color=grid_color, linestyle="-", linewidth=0.6, alpha=0.7)
        self.ax.grid(True, which='minor', color=minor_grid, linestyle=":", linewidth=0.4, alpha=0.5)
        self.ax.minorticks_on()
        
        for spine in self.ax.spines.values():
            spine.set_color("#26334D" if theme == "dark" else "#CBD5E1")

        self.ax.xaxis.label.set_color(fg_color)
        self.ax.yaxis.label.set_color(fg_color)
        self.ax.title.set_color("#FFFFFF" if theme == "dark" else "#0F172A")
        self.ax.tick_params(colors=fg_color, which='both')
        
        # Style guide crosshairs & coordinate overlay dynamically
        self.cross_h.set_color("#FFFFFF" if theme == "dark" else "#0F172A")
        self.cross_v.set_color("#FFFFFF" if theme == "dark" else "#0F172A")
        self.coord_text.set_color("#06B6D4" if theme == "dark" else "#2563EB")
        self.coord_text.get_bbox_patch().set_facecolor(bbox_color)
        self.coord_text.get_bbox_patch().set_edgecolor("#26334D" if theme == "dark" else "#CBD5E1")
        self.coord_text.get_bbox_patch().set_alpha(0.9)

        legend = self.ax.get_legend()
        if legend:
            legend.get_frame().set_facecolor(bg_color)
            legend.get_frame().set_edgecolor("#26334D" if theme == "dark" else "#CBD5E1")
            for text in legend.get_texts():
                text.set_color(fg_color)
                
        self.fig.tight_layout()

    def refresh_plot(self) -> None:
        """Refreshes the canvas to update graphics."""
        self.apply_theme_colors()
        self.draw()

    def store_original_limits(self):
        """Saves current limits to allow reset zoom later."""
        self.orig_xlim = self.ax.get_xlim()
        self.orig_ylim = self.ax.get_ylim()

    def on_mouse_move(self, event):
        """Draws coordinate crosshairs and text overlay on mouse hover."""
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            
            # Update crosshairs
            self.cross_h.set_ydata([y, y])
            self.cross_v.set_xdata([x, x])
            self.cross_h.set_visible(True)
            self.cross_v.set_visible(True)
            
            # Format display strings
            x_str = f"{x:,.2f}" if abs(x) >= 1e-2 else f"{x:g}"
            y_str = f"{y:,.2f}" if abs(y) >= 1e-2 else f"{y:g}"
            coord_str = f"X: {x_str}  |  Y: {y_str}"
            
            self.coord_text.setText(coord_str)
            self.coord_text.set_visible(True)
            
            self.coordinates_updated.emit(coord_str)
            self.draw_idle()
        else:
            self.on_mouse_leave(None)

    def on_mouse_leave(self, event):
        """Hides crosshairs when mouse exits the plot area."""
        self.cross_h.set_visible(False)
        self.cross_v.set_visible(False)
        self.coord_text.set_visible(False)
        self.coordinates_updated.emit("")
        self.draw_idle()

    def on_button_press(self, event):
        """Resets zoom on double click."""
        if event.dblclick:
            self.reset_zoom()

    # --- Public Chart Interactions ---
    
    def zoom_in(self):
        """Zooms in by 20% on both axes."""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        dx = (xlim[1] - xlim[0]) * 0.1
        dy = (ylim[1] - ylim[0]) * 0.1
        
        self.ax.set_xlim(xlim[0] + dx, xlim[1] - dx)
        self.ax.set_ylim(ylim[0] + dy, ylim[1] - dy)
        self.draw_idle()

    def zoom_out(self):
        """Zooms out by 20% on both axes."""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        dx = (xlim[1] - xlim[0]) * 0.1
        dy = (ylim[1] - ylim[0]) * 0.1
        
        self.ax.set_xlim(xlim[0] - dx, xlim[1] + dx)
        self.ax.set_ylim(ylim[0] - dy, ylim[1] + dy)
        self.draw_idle()

    def reset_zoom(self):
        """Restores axes limits to original layout bounds."""
        if self.orig_xlim is not None and self.orig_ylim is not None:
            self.ax.set_xlim(self.orig_xlim)
            self.ax.set_ylim(self.orig_ylim)
            self.draw_idle()

    def save_graph(self):
        """Prompts user to export plot canvas image as PNG."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Graph Image", "chart.png", "PNG Image (*.png);;All Files (*)"
        )
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300)
                QMessageBox.information(self, "Export Success", f"Graph exported successfully to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save graph:\n{str(e)}")
