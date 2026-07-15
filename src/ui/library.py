import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QScrollArea,
    QSplitter, QPushButton, QGridLayout, QSizePolicy, QDialog,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QColor, QFont, QCursor
import qtawesome as qta
from src.core.logger import log

# Global cache for downloaded remote images
_remote_image_cache = {}


class ImageViewerDialog(QDialog):
    """A premium dark-themed modal dialog that lets users view, pan, and zoom images."""
    
    def __init__(self, pixmap: QPixmap, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)
        self.setStyleSheet("background-color: #0b0f19; color: #f8fafc;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header Info Row
        hdr = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 13pt; font-weight: bold; color: #06b6d4;")
        hdr.addWidget(title_lbl)
        hdr.addStretch()
        
        self.pct_lbl = QLabel("Zoom: 100%")
        self.pct_lbl.setStyleSheet("color: #94a3b8; font-size: 9.5pt;")
        hdr.addWidget(self.pct_lbl)
        layout.addLayout(hdr)
        
        # Interactive graphics view
        self.view = QGraphicsView()
        self.view.setStyleSheet("background-color: #0f172a; border: 1px solid #1e293b; border-radius: 8px;")
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        
        layout.addWidget(self.view)
        
        # Bottom controls row
        controls = QHBoxLayout()
        self.zoom_level = 1.0
        
        zoom_in_btn = QPushButton(" Zoom In")
        zoom_in_btn.setIcon(qta.icon("fa5s.search-plus", color="#ffffff"))
        zoom_in_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        zoom_out_btn = QPushButton(" Zoom Out")
        zoom_out_btn.setIcon(qta.icon("fa5s.search-minus", color="#ffffff"))
        zoom_out_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        reset_btn = QPushButton(" Reset Zoom")
        reset_btn.setIcon(qta.icon("fa5s.redo", color="#ffffff"))
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)
        reset_btn.clicked.connect(self.reset_zoom)
        
        close_btn = QPushButton(" Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        controls.addWidget(zoom_in_btn)
        controls.addWidget(zoom_out_btn)
        controls.addWidget(reset_btn)
        controls.addStretch()
        controls.addWidget(close_btn)
        layout.addLayout(controls)
        
        self.update_transform()
        
    def zoom_in(self):
        self.zoom_level *= 1.15
        self.update_transform()
        
    def zoom_out(self):
        if self.zoom_level > 0.15:
            self.zoom_level /= 1.15
            self.update_transform()
            
    def reset_zoom(self):
        self.zoom_level = 1.0
        self.update_transform()
        
    def update_transform(self):
        self.view.resetTransform()
        self.view.scale(self.zoom_level, self.zoom_level)
        self.pct_lbl.setText(f"Zoom: {int(self.zoom_level * 100)}%")


class ClickableLabel(QLabel):
    """A QLabel that triggers a click signal when left-clicked to launch the fullscreen image viewer."""
    clicked = Signal(QPixmap, str)
    
    def __init__(self, pixmap: QPixmap, title: str, parent=None):
        super().__init__(parent)
        self.pixmap_data = pixmap
        self.title_data = title
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setPixmap(pixmap)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.pixmap_data:
            self.clicked.emit(self.pixmap_data, self.title_data)
        super().mousePressEvent(event)


class AccordionPanel(QWidget):
    """An individual expandable section in the component details sheet."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.is_expanded = False
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(0)
        
        self.header_btn = QPushButton(f" ▶  {title}")
        self.header_btn.setObjectName("accordion-header")
        self.header_btn.setStyleSheet("""
            QPushButton#accordion-header {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 10px 15px;
                text-align: left;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton#accordion-header:hover {
                background-color: #334155;
                border-color: #475569;
            }
        """)
        self.header_btn.clicked.connect(self.toggle)
        
        self.content_widget = QFrame()
        self.content_widget.setObjectName("accordion-content")
        self.content_widget.setStyleSheet("""
            QFrame#accordion-content {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-top: none;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
            }
        """)
        self.content_widget.setVisible(False)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(15, 12, 15, 12)
        self.content_layout.setSpacing(8)
        
        layout.addWidget(self.header_btn)
        layout.addWidget(self.content_widget)
        
    def toggle(self):
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        arrow = " ▼ " if self.is_expanded else " ▶ "
        title_text = self.header_btn.text()[4:]
        self.header_btn.setText(f"{arrow} {title_text}")
        
        if self.is_expanded:
            self.header_btn.setStyleSheet("""
                QPushButton#accordion-header {
                    background-color: #1e293b;
                    color: #06b6d4;
                    border: 1px solid #06b6d4;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 0px;
                    padding: 10px 15px;
                    text-align: left;
                    font-weight: bold;
                    font-size: 10pt;
                }
            """)
        else:
            self.header_btn.setStyleSheet("""
                QPushButton#accordion-header {
                    background-color: #1e293b;
                    color: #e2e8f0;
                    border: 1px solid #334155;
                    border-radius: 4px;
                    padding: 10px 15px;
                    text-align: left;
                    font-weight: bold;
                    font-size: 10pt;
                }
                QPushButton#accordion-header:hover {
                    background-color: #334155;
                    border-color: #475569;
                }
            """)


class LibraryView(QWidget):
    """Electronics Component Encyclopedia View supporting fully dynamic data-driven image loading and zoom."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        log.info("Initializing LibraryView")
        
        # Base Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #1e293b;
                width: 2px;
            }
        """)
        main_layout.addWidget(self.splitter)
        
        # Left Panel (Category Explorer)
        self.left_panel = QFrame()
        self.left_panel.setObjectName("explorer-panel")
        self.left_panel.setStyleSheet("""
            QFrame#explorer-panel {
                background-color: #0b0f19;
                border: 1px solid #1e293b;
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(12, 12, 12, 12)
        left_layout.setSpacing(10)
        
        # Search Box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search components...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9.5pt;
            }
            QLineEdit:focus {
                border-color: #06b6d4;
            }
        """)
        self.search_input.textChanged.connect(self.filter_tree)
        left_layout.addWidget(self.search_input)
        
        # Categories Tree
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: transparent;
                border: none;
                color: #94a3b8;
                font-size: 9.5pt;
            }
            QTreeWidget::item {
                padding: 6px;
            }
            QTreeWidget::item:hover {
                background-color: #1e293b;
                border-radius: 4px;
                color: #f8fafc;
            }
            QTreeWidget::item:selected {
                background-color: #0f172a;
                color: #06b6d4;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        self.tree_widget.itemClicked.connect(self.on_item_clicked)
        left_layout.addWidget(self.tree_widget)
        
        # Right Panel (Details Viewer)
        self.right_scroll = QScrollArea()
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #1e293b;
                border-radius: 8px;
                background-color: #0b0f19;
            }
        """)
        
        self.right_container = QFrame()
        self.right_container.setObjectName("details-panel")
        self.right_container.setStyleSheet("QFrame#details-panel { background-color: #0b0f19; }")
        self.right_layout = QVBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(25, 25, 25, 25)
        self.right_layout.setSpacing(15)
        
        self.right_scroll.setWidget(self.right_container)
        
        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_scroll)
        self.splitter.setSizes([260, 740])
        
        # Load component data
        self.load_components_data()
        self.build_categories_tree()
        
        # Select first component by default
        self.select_default_component()
        
    def load_components_data(self):
        """Scans the src/data/components/ directory and loads JSON databases."""
        self.components_db = {}
        data_dir = "src/data/components"
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith(".json"):
                    try:
                        filepath = os.path.join(data_dir, file)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            self.components_db[data["id"]] = data
                    except Exception as e:
                        log.error(f"Error loading component JSON: {e}")
                        
    def build_categories_tree(self):
        """Groups loaded components into their 12 categories and populates the tree."""
        self.tree_widget.clear()
        
        categories = [
            "Passive Components", "Semiconductors", "Transistors",
            "Integrated Circuits", "Power Electronics", "Sensors",
            "Microcontrollers", "Communication Modules", "Displays",
            "Protection Devices", "Connectors", "Miscellaneous"
        ]
        
        self.category_items = {}
        for cat in categories:
            cat_item = QTreeWidgetItem(self.tree_widget)
            cat_item.setText(0, cat)
            cat_item.setFont(0, QFont("Segoe UI", 10, QFont.Weight.Bold))
            cat_item.setForeground(0, QColor("#e2e8f0"))
            self.category_items[cat] = cat_item
            
        for comp_id, comp in sorted(self.components_db.items(), key=lambda x: x[1]["name"]):
            cat = comp.get("category", "Miscellaneous")
            parent_item = self.category_items.get(cat)
            if not parent_item:
                parent_item = self.category_items["Miscellaneous"]
                
            child_item = QTreeWidgetItem(parent_item)
            child_item.setText(0, comp["name"])
            child_item.setData(0, Qt.ItemDataRole.UserRole, comp_id)
            child_item.setForeground(0, QColor("#94a3b8"))
            
        # Expand categories containing items
        for cat_item in self.category_items.values():
            if cat_item.childCount() > 0:
                cat_item.setExpanded(True)
                
    def select_default_component(self):
        """Selects the first component in the tree by default."""
        if self.tree_widget.topLevelItemCount() > 0:
            for i in range(self.tree_widget.topLevelItemCount()):
                cat_item = self.tree_widget.topLevelItem(i)
                if cat_item.childCount() > 0:
                    child = cat_item.child(0)
                    self.tree_widget.setCurrentItem(child)
                    self.on_item_clicked(child)
                    break
                    
    def filter_tree(self, text):
        """Instantly filters tree components with partial matching."""
        query = text.lower().strip()
        
        for i in range(self.tree_widget.topLevelItemCount()):
            cat_item = self.tree_widget.topLevelItem(i)
            match_count = 0
            
            for j in range(cat_item.childCount()):
                child_item = cat_item.child(j)
                comp_name = child_item.text(0).lower()
                
                if query in comp_name:
                    child_item.setHidden(False)
                    match_count += 1
                else:
                    child_item.setHidden(True)
                    
            if match_count > 0 or query == "":
                cat_item.setHidden(False)
                cat_item.setExpanded(True)
            else:
                cat_item.setHidden(True)

    def resolve_image_path(self, relative_path: str):
        """Resolves JSON relative paths into absolute paths relative to the project root on local disk."""
        if not relative_path:
            return None
            
        # Root directory of the project, calculated relative to this source file location
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Candidates checking relative to project root
        candidates = [
            os.path.abspath(os.path.join(project_root, relative_path)),
            os.path.abspath(os.path.join(project_root, "src", relative_path))
        ]
        
        for path in candidates:
            if os.path.exists(path):
                return path
                
            # Fallback to check other typical extensions
            base_no_ext, _ = os.path.splitext(path)
            for ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.JPG', '.JPEG', '.PNG', '.WEBP', '.BMP']:
                alt_path = base_no_ext + ext
                if os.path.exists(alt_path):
                    return alt_path
        return None

    def load_pixmap_from_path_or_url(self, path_or_url: str) -> QPixmap:
        """Loads a QPixmap from a local path or a remote HTTP/HTTPS URL with caching and logging."""
        if not path_or_url:
            return None
            
        # 1. Remote URL Check
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            global _remote_image_cache
            if path_or_url in _remote_image_cache:
                return _remote_image_cache[path_or_url]
                
            try:
                import requests
                response = requests.get(path_or_url, timeout=3)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(response.content):
                        _remote_image_cache[path_or_url] = pixmap
                        log.info(f"Downloaded remote image:\n{path_or_url}")
                        return pixmap
            except Exception as e:
                log.error(f"Error downloading remote image from {path_or_url}: {e}")
            log.info(f"Image not found:\n{path_or_url}")
            return None
            
        # 2. Local Path Check
        abs_path = self.resolve_image_path(path_or_url)
        if abs_path:
            log.info(f"Loaded local image:\n{path_or_url}")
            return QPixmap(abs_path)
            
        log.info(f"Image not found:\n{path_or_url}")
        return None

    def create_image_container(self, label_text, json_path):
        """Creates a zoomable image widget. Returns None if the image file is missing/unresolvable."""
        if not json_path or str(json_path).strip() == "":
            return None
            
        pixmap = self.load_pixmap_from_path_or_url(json_path)
        if not pixmap or pixmap.isNull():
            return None
            
        box = QFrame()
        box.setObjectName("image-box")
        box.setStyleSheet("""
            QFrame#image-box {
                background-color: #0b0f19;
                border: 1px solid #334155;
                border-radius: 6px;
                margin-top: 8px;
                margin-bottom: 8px;
            }
        """)
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(12, 12, 12, 12)
        box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #06b6d4; font-size: 8.5pt; font-weight: bold; text-transform: uppercase; margin-bottom: 6px;")
        box_layout.addWidget(lbl, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Create interactive clickable label
        clickable_lbl = ClickableLabel(pixmap, label_text)
        clickable_lbl.clicked.connect(self.open_image_viewer)
        
        # Scale preview
        scaled = pixmap.scaled(QSize(320, 200), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        clickable_lbl.setPixmap(scaled)
        clickable_lbl.setToolTip("Click to enlarge and zoom")
        box_layout.addWidget(clickable_lbl)
        
        return box

    def open_image_viewer(self, pixmap, title):
        """Launches the zoomable image viewer dialog."""
        dialog = ImageViewerDialog(pixmap, title, self)
        dialog.exec()

    def on_item_clicked(self, item):
        """Displays the selected component in the details pane."""
        comp_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not comp_id or comp_id not in self.components_db:
            return
            
        comp = self.components_db[comp_id]
        
        # Clear right panel
        while self.right_layout.count():
            child = self.right_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # 1. Component Header Card
        header_card = QFrame()
        header_card.setObjectName("header-card")
        header_card.setStyleSheet("""
            QFrame#header-card {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        title_row = QHBoxLayout()
        name_lbl = QLabel(comp["name"])
        name_lbl.setStyleSheet("font-size: 18pt; font-weight: bold; color: #f8fafc;")
        title_row.addWidget(name_lbl)
        
        diff_val = comp.get("difficulty", "Beginner")
        diff_color = "#10b981" if diff_val == "Beginner" else "#f59e0b" if diff_val == "Intermediate" else "#ef4444"
        diff_lbl = QLabel(diff_val)
        diff_lbl.setStyleSheet(f"""
            background-color: {diff_color}22;
            color: {diff_color};
            border: 1px solid {diff_color};
            border-radius: 4px;
            padding: 3px 8px;
            font-size: 8.5pt;
            font-weight: bold;
        """)
        title_row.addWidget(diff_lbl)
        title_row.addStretch()
        header_layout.addLayout(title_row)
        
        cat_lbl = QLabel(f"Category: {comp.get('category', 'Miscellaneous')}")
        cat_lbl.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 9.5pt; margin-top: 2px;")
        header_layout.addWidget(cat_lbl)
        
        desc_lbl = QLabel(comp.get("short_description", ""))
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #94a3b8; font-size: 10.5pt; margin-top: 8px; line-height: 1.45;")
        header_layout.addWidget(desc_lbl)
        
        uses_lbl = QLabel(f"Common Uses: {comp.get('common_uses', 'N/A')}")
        uses_lbl.setWordWrap(True)
        uses_lbl.setStyleSheet("color: #64748b; font-size: 9pt; font-style: italic; margin-top: 8px;")
        header_layout.addWidget(uses_lbl)
        
        self.right_layout.addWidget(header_card)
        
        # 2. Quick Facts Grid Card
        facts = comp.get("quick_facts", {})
        if facts:
            facts_card = QFrame()
            facts_card.setObjectName("facts-card")
            facts_card.setStyleSheet("""
                QFrame#facts-card {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            facts_layout = QVBoxLayout(facts_card)
            
            fact_title = QLabel("Quick Facts")
            fact_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt; margin-bottom: 8px;")
            facts_layout.addWidget(fact_title)
            
            grid = QGridLayout()
            grid.setSpacing(12)
            
            items = [
                ("Symbol", facts.get("symbol", "N/A")),
                ("Unit", facts.get("unit", "N/A")),
                ("Formula", facts.get("formula", "N/A")),
                ("Passive / Active", facts.get("passive_active", "N/A")),
                ("Polarized", facts.get("polarized", "N/A")),
                ("Typical Voltage", facts.get("typical_voltage", "N/A")),
                ("Typical Current", facts.get("typical_current", "N/A")),
                ("Freq Limits", facts.get("operating_frequency", "N/A"))
            ]
            
            for index, (k, v) in enumerate(items):
                col = index % 4
                row = index // 4
                
                cell = QWidget()
                cell_layout = QVBoxLayout(cell)
                cell_layout.setContentsMargins(0, 0, 0, 0)
                cell_layout.setSpacing(2)
                
                k_lbl = QLabel(k)
                k_lbl.setStyleSheet("color: #64748b; font-size: 8pt; text-transform: uppercase; font-weight: bold;")
                v_lbl = QLabel(str(v))
                v_lbl.setStyleSheet("color: #e2e8f0; font-size: 10pt; font-weight: 500;")
                
                cell_layout.addWidget(k_lbl)
                cell_layout.addWidget(v_lbl)
                grid.addWidget(cell, row, col)
                
            facts_layout.addLayout(grid)
            self.right_layout.addWidget(facts_card)
            
        # 3. Dynamic Technical Image Gallery (Adaptive UI - Hides completely if no images exist)
        images_config = comp.get("images", {})
        if images_config:
            valid_containers = []
            for label_key, path in images_config.items():
                if comp_id == "inductor" and label_key == "example_circuit":
                    friendly_label = "Types of Inductor"
                elif comp_id == "thermistor" and label_key == "example_circuit":
                    friendly_label = "Types of Thermistor"
                elif comp_id == "capacitor" and label_key == "example_circuit":
                    friendly_label = "Types of Capacitor"
                elif comp_id == "led" and label_key == "pin_diagram":
                    friendly_label = "Characteristics"
                elif comp_id == "led" and label_key == "real_photo":
                    friendly_label = "V-I Characteristics"
                elif comp_id == "resistor" and label_key == "example_circuit":
                    friendly_label = "Resistor Color Code"
                elif comp_id == "tunnel_diode" and label_key == "example_circuit":
                    friendly_label = "V-I Characteristics"
                elif comp_id == "varactor_diode" and label_key == "pin_diagram":
                    friendly_label = "Characteristics"
                elif comp_id == "jfet" and label_key == "pin_diagram":
                    friendly_label = "Types of JFET"
                elif comp_id == "mosfet" and label_key == "example_circuit":
                    friendly_label = "Types of MOSFET"
                elif comp_id == "mosfet" and label_key == "pin_diagram":
                    friendly_label = "Enhancement MOSFET vs Depletion MOSFET"
                elif comp_id == "mosfet" and label_key == "internal_structure":
                    friendly_label = "Construction Image"
                elif comp_id == "555_timer" and label_key == "real_photo":
                    friendly_label = "Real Photo and Pin Diagram"
                elif comp_id == "555_timer" and label_key == "symbol":
                    friendly_label = "Schematic View of 555 Timer"
                elif comp_id == "ultrasonic_sensor" and label_key == "symbol":
                    friendly_label = "Functions of Pin"
                elif comp_id == "diac" and label_key == "pin_diagram":
                    friendly_label = "V-I Characteristics"
                elif comp_id == "circuit_breaker_mcb" and label_key == "example_circuit":
                    friendly_label = "Types of MCB"
                else:
                    friendly_label = label_key.replace("_", " ").title()
                box = self.create_image_container(friendly_label, path)
                if box:
                    valid_containers.append(box)
                    
            if valid_containers:
                gallery_card = QFrame()
                gallery_card.setObjectName("gallery-card")
                gallery_card.setStyleSheet("""
                    QFrame#gallery-card {
                        background-color: #0f172a;
                        border: 1px solid #1e293b;
                        border-radius: 8px;
                        padding: 15px;
                    }
                """)
                gallery_layout = QVBoxLayout(gallery_card)
                
                gallery_title = QLabel("Technical Diagrams & Imagery")
                gallery_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt; margin-bottom: 8px;")
                gallery_layout.addWidget(gallery_title)
                
                gallery_grid = QGridLayout()
                gallery_grid.setSpacing(10)
                
                for index, box in enumerate(valid_containers):
                    col = index % 3
                    row = index // 3
                    gallery_grid.addWidget(box, row, col)
                    
                gallery_layout.addLayout(gallery_grid)
                self.right_layout.addWidget(gallery_card)

        # 4. Specifications Table Card
        specs = comp.get("specifications", [])
        if specs:
            specs_card = QFrame()
            specs_card.setObjectName("specs-card")
            specs_card.setStyleSheet("""
                QFrame#specs-card {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            specs_layout = QVBoxLayout(specs_card)
            
            specs_title = QLabel("Datasheet Specifications")
            specs_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt; margin-bottom: 8px;")
            specs_layout.addWidget(specs_title)
            
            table_layout = QVBoxLayout()
            table_layout.setSpacing(6)
            
            # Header Row
            hdr_widget = QWidget()
            hdr_layout = QHBoxLayout(hdr_widget)
            hdr_layout.setContentsMargins(6, 4, 6, 4)
            p_hdr = QLabel("Parameter")
            p_hdr.setStyleSheet("color: #64748b; font-weight: bold; font-size: 8.5pt;")
            v_hdr = QLabel("Typical Value")
            v_hdr.setStyleSheet("color: #64748b; font-weight: bold; font-size: 8.5pt;")
            n_hdr = QLabel("Notes")
            n_hdr.setStyleSheet("color: #64748b; font-weight: bold; font-size: 8.5pt;")
            hdr_layout.addWidget(p_hdr, 3)
            hdr_layout.addWidget(v_hdr, 2)
            hdr_layout.addWidget(n_hdr, 4)
            table_layout.addWidget(hdr_widget)
            
            divider = QFrame()
            divider.setFrameShape(QFrame.Shape.HLine)
            divider.setStyleSheet("background-color: #1e293b;")
            table_layout.addWidget(divider)
            
            for s in specs:
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(6, 4, 6, 4)
                
                p_lbl = QLabel(s.get("parameter", ""))
                p_lbl.setStyleSheet("color: #e2e8f0; font-size: 9pt; font-weight: 500;")
                val_str = f"{s.get('value', '')} {s.get('unit', '')}".strip()
                v_lbl = QLabel(val_str)
                v_lbl.setStyleSheet("color: #06b6d4; font-size: 9pt; font-weight: bold;")
                n_lbl = QLabel(s.get("notes", ""))
                n_lbl.setStyleSheet("color: #94a3b8; font-size: 9pt;")
                
                row_layout.addWidget(p_lbl, 3)
                row_layout.addWidget(v_lbl, 2)
                row_layout.addWidget(n_lbl, 4)
                table_layout.addWidget(row_widget)
                
            specs_layout.addLayout(table_layout)
            self.right_layout.addWidget(specs_card)
            
        # 5. Expandable Sections (Accordion)
        sections = [
            ("Definition", comp.get("definition")),
            ("Working Principle", comp.get("working_principle")),
            ("Types", comp.get("types")),
            ("Construction", comp.get("construction")),
            ("Electrical Characteristics", comp.get("electrical_characteristics")),
            ("Symbols", comp.get("symbol_description", "Standard circuit symbol configuration representing connectivity.")),
            ("Formula(s)", comp.get("formulas")),
            ("Applications", comp.get("applications")),
            ("Advantages", comp.get("advantages")),
            ("Disadvantages", comp.get("disadvantages")),
            ("Example Circuit Explanation", comp.get("example_circuit_operation")),
            ("Practical Tips", comp.get("practical_tips")),
            ("Interview / Viva Questions", comp.get("interview_questions")),
            ("Related Experiments", comp.get("related_experiments")),
            ("References / Datasheet", comp.get("references"))
        ]
        
        for title, content in sections:
            if not content:
                continue
                
            panel = AccordionPanel(title)
            
            if title == "Interview / Viva Questions":
                # Render question cards list
                for index, q in enumerate(content, 1):
                    q_lbl = QLabel(f"Q{index}: {q.get('question')}")
                    q_lbl.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 9.5pt;")
                    q_lbl.setWordWrap(True)
                    a_lbl = QLabel(f"Answer: {q.get('answer')}")
                    a_lbl.setStyleSheet("color: #94a3b8; font-size: 9.5pt; margin-left: 10px; margin-bottom: 8px;")
                    a_lbl.setWordWrap(True)
                    panel.content_layout.addWidget(q_lbl)
                    panel.content_layout.addWidget(a_lbl)
            elif title == "Related Experiments":
                # Render clickable buttons linking to simulator rows
                info_lbl = QLabel("Perform virtual laboratory experiments with this component:")
                info_lbl.setStyleSheet("color: #e2e8f0; font-size: 9.5pt; margin-bottom: 4px;")
                panel.content_layout.addWidget(info_lbl)
                
                for exp in content:
                    btn = QPushButton(f"  ✓  Launch Simulation: {exp.get('name')}")
                    btn.setIcon(qta.icon("fa5s.flask", color="#ffffff"))
                    btn.setIconSize(QSize(12, 12))
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #10b981;
                            color: #ffffff;
                            border: none;
                            border-radius: 4px;
                            padding: 8px 12px;
                            text-align: left;
                            font-weight: bold;
                            font-size: 9pt;
                            margin-bottom: 4px;
                        }
                        QPushButton:hover {
                            background-color: #059669;
                        }
                    """)
                    btn.clicked.connect(lambda checked=False, name=exp.get("name"): self.go_to_experiment(name))
                    panel.content_layout.addWidget(btn)
            else:
                # Standard text block
                text_lbl = QLabel(str(content))
                text_lbl.setWordWrap(True)
                text_lbl.setStyleSheet("color: #e2e8f0; font-size: 9.5pt; line-height: 1.45;")
                panel.content_layout.addWidget(text_lbl)
                
            self.right_layout.addWidget(panel)
            
        self.right_layout.addStretch()
        
    def go_to_experiment(self, exp_name: str):
        """Cross-module click router connecting library directly to simulation rows."""
        exp_to_row = {
            "RC Charging": 0,
            "RC Discharging": 0,
            "RL Transient": 1,
            "Series RLC Resonance": 2,
            "Low Pass Filter": 3,
            "High Pass Filter": 4,
            "Half Wave Rectifier": 5,
            "Full Wave Rectifier": 6,
            "Signal Attenuation": 7,
            "Voltage Divider": 8,
            "Positive Clipper": 7,
            "Negative Clipper": 7
        }
        
        main_win = self.window()
        if main_win and hasattr(main_win, "switch_view"):
            main_win.switch_view(4) # Index 4 is SimulationView (Simulation Lab)
            sim_view = main_win.views[4]
            row_idx = exp_to_row.get(exp_name)
            if row_idx is not None:
                sim_view.list_widget.setCurrentRow(row_idx)
