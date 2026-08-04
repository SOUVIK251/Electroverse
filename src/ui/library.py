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
from src.core.config import config_manager
from src.core.image_loader import AsyncImageLoader

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
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(project_root, "src", "data", "components")
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
                        
        # Load image manifest if available
        self.images_manifest = {}
        manifest_path = os.path.join(project_root, "src", "data", "component_images.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as mf:
                    self.images_manifest = json.load(mf)
            except Exception as e:
                log.error(f"Error loading component_images.json manifest: {e}")
                        
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
        """Creates an async zoomable image widget with skeleton placeholder and instant rendering."""
        if not json_path or str(json_path).strip() == "":
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

        resolved_path = self.resolve_image_path(json_path) or json_path

        # 1. Memory Cache Check (<1ms instant rendering)
        cached_pixmap = AsyncImageLoader.instance().get_cached_image(resolved_path, (320, 200))
        if cached_pixmap and not cached_pixmap.isNull():
            clickable_lbl = ClickableLabel(cached_pixmap, label_text)
            clickable_lbl.setPixmap(cached_pixmap)
            clickable_lbl.setToolTip("Click to enlarge and zoom")
            clickable_lbl.clicked.connect(lambda pm, t, p=resolved_path: self.open_image_viewer_async(p, t))
            box_layout.addWidget(clickable_lbl)
            return box

        # 2. Skeleton Loading Placeholder Indicator
        placeholder = QLabel("⚡ Loading visual...")
        placeholder.setFixedSize(320, 160)
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("background-color: #0f172a; color: #64748b; border: 1px dashed #1e293b; border-radius: 6px; font-size: 9pt; font-weight: 500;")
        box_layout.addWidget(placeholder)

        def on_image_loaded(scaled_pixmap: QPixmap):
            if placeholder.parent():
                box_layout.removeWidget(placeholder)
                placeholder.deleteLater()
                
            clickable_lbl = ClickableLabel(scaled_pixmap, label_text)
            clickable_lbl.setPixmap(scaled_pixmap)
            clickable_lbl.setToolTip("Click to enlarge and zoom")
            clickable_lbl.clicked.connect(lambda pm, t, p=resolved_path: self.open_image_viewer_async(p, t))
            box_layout.addWidget(clickable_lbl)

        def on_image_failed(err_msg: str):
            if placeholder.parent():
                placeholder.setText("Visual unavailable")
                placeholder.setStyleSheet("background-color: #0f172a; color: #475569; border: 1px solid #1e293b; border-radius: 6px; font-size: 8.5pt;")

        # 3. Launch Parallel Async Background Loader
        AsyncImageLoader.instance().load_image_async(resolved_path, (320, 200), on_image_loaded, on_image_failed)

        return box

    def open_image_viewer_async(self, path_or_url, title):
        """Asynchronously loads full-resolution image and launches zoom viewer off the GUI thread."""
        cached_full = AsyncImageLoader.instance().get_cached_image(path_or_url)
        if cached_full:
            dialog = ImageViewerDialog(cached_full, title, self)
            dialog.exec()
            return

        def on_full_loaded(pixmap):
            dialog = ImageViewerDialog(pixmap, title, self)
            dialog.exec()

        AsyncImageLoader.instance().load_image_async(path_or_url, None, on_full_loaded)

    def open_image_viewer(self, pixmap, title):
        """Fallback zoomable image viewer launcher."""
        dialog = ImageViewerDialog(pixmap, title, self)
        dialog.exec()


    def on_item_clicked(self, item):
        """Displays the selected component in the redesigned details pane and preloads neighbors."""
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QRadioButton, QButtonGroup, QTabWidget, QListWidget, QListWidgetItem
        
        comp_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not comp_id or comp_id not in self.components_db:
            return
            
        comp = self.components_db[comp_id]

        # Background preloading for previous and next components in the category tree
        parent_item = item.parent()
        if parent_item:
            idx = parent_item.indexOfChild(item)
            neighbors = []
            if idx > 0:
                neighbors.append(parent_item.child(idx - 1))
            if idx < parent_item.childCount() - 1:
                neighbors.append(parent_item.child(idx + 1))

            for n_item in neighbors:
                n_id = n_item.data(0, Qt.ItemDataRole.UserRole)
                if n_id and n_id in self.components_db:
                    n_imgs = self.images_manifest.get(n_id, self.components_db[n_id].get("images", {}))
                    for img_path in n_imgs.values():
                        if img_path and str(img_path).strip():
                            res_p = self.resolve_image_path(img_path) or img_path
                            AsyncImageLoader.instance().preload_image(res_p, (320, 200))
        
        # Log this session action
        main_win = self.window()
        if main_win and hasattr(main_win, "log_session_activity"):
            main_win.log_session_activity(f"Inspected {comp['name']}")
        
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
        header_layout.setContentsMargins(15, 15, 15, 15)
        
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
        
        # Star/Favorite Toggle Button
        self.star_btn = QPushButton()
        self.star_btn.setFixedSize(32, 32)
        self.star_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        favs = config_manager.get("favorites") or []
        is_fav = comp_id in favs
        self.star_btn.setIcon(qta.icon("fa5s.star", color="#f59e0b" if is_fav else "#475569"))
        self.star_btn.setToolTip("Mark Component as Favorite")
        self.star_btn.clicked.connect(lambda: self.toggle_component_favorite(comp_id))
        title_row.addWidget(self.star_btn)
        
        header_layout.addLayout(title_row)
        
        cat_lbl = QLabel(f"Category: {comp.get('category', 'Miscellaneous')}")
        cat_lbl.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 9.5pt; margin-top: 2px;")
        header_layout.addWidget(cat_lbl)
        
        desc_lbl = QLabel(comp.get("short_description", ""))
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet("color: #94a3b8; font-size: 10.5pt; margin-top: 8px; line-height: 1.45;")
        header_layout.addWidget(desc_lbl)
        
        self.right_layout.addWidget(header_card)
        
        # 2. Component at a Glance Summary Card
        glance_card = QFrame()
        glance_card.setObjectName("glance-card")
        glance_card.setStyleSheet("""
            QFrame#glance-card {
                background-color: #111827;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        glance_layout = QGridLayout(glance_card)
        glance_layout.setSpacing(12)
        
        facts = comp.get("quick_facts", {})
        glance_items = [
            ("Category", comp.get("category", "N/A")),
            ("Difficulty", comp.get("difficulty", "Beginner")),
            ("Pins", facts.get("symbol", "N/A")),  # Fallback to symbol label or generic
            ("Default Package", "DIP" if "ic" in comp_id else "Axial/Through-hole"),
            ("Typical Supply", facts.get("typical_voltage", "N/A")),
            ("Used In", comp.get("common_uses", "N/A")[:45] + "..."),
            ("Symbol Status", "Active" if "symbol" in comp.get("images", {}) else "N/A")
        ]
        
        # Read verified pins counts if in database
        pin_list = self.get_component_pins_metadata(comp_id)
        if pin_list:
            glance_items[2] = ("Pins Count", f"{len(pin_list)} Pins")
            glance_items[3] = ("Default Package", pin_list[0].get("package", "DIP-8"))
            
        for index, (k, v) in enumerate(glance_items):
            col = index % 4
            row = index // 4
            cell = QWidget()
            c_lay = QVBoxLayout(cell)
            c_lay.setContentsMargins(0, 0, 0, 0)
            c_lay.setSpacing(2)
            k_lbl = QLabel(k)
            k_lbl.setStyleSheet("color: #64748b; font-size: 7.5pt; text-transform: uppercase; font-weight: bold;")
            v_lbl = QLabel(str(v))
            v_lbl.setStyleSheet("color: #e2e8f0; font-size: 9.5pt; font-weight: 500;")
            v_lbl.setWordWrap(True)
            c_lay.addWidget(k_lbl)
            c_lay.addWidget(v_lbl)
            glance_layout.addWidget(cell, row, col)
            
        self.right_layout.addWidget(glance_card)
        
        # 3. Interactive Component Explorer Widget
        explorer_card = QFrame()
        explorer_card.setObjectName("explorer-card")
        explorer_card.setStyleSheet("""
            QFrame#explorer-card {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        explorer_layout = QVBoxLayout(explorer_card)
        
        exp_title = QLabel("Interactive Component Explorer")
        exp_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt; margin-bottom: 8px;")
        explorer_layout.addWidget(exp_title)
        
        # Views TabWidget
        views_tabs = QTabWidget()
        views_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1e293b;
                background-color: #0b0f19;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #1e293b;
                color: #94a3b8;
                padding: 6px 12px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #06b6d4;
                color: #ffffff;
            }
        """)
        
        # Retrieve images from manifest (with fallback to comp['images'])
        images_config = {}
        if hasattr(self, "images_manifest") and comp_id in self.images_manifest:
            images_config = self.images_manifest[comp_id]
        else:
            images_config = comp.get("images", {})
            
        category_mappings = [
            ("real_photo", "Real Photo"),
            ("symbol", "Circuit Symbol"),
            ("internal_structure", "Internal Structure"),
            ("example_circuit", "Example Circuit"),
            ("optocoupler_example", "Optocoupler Example"),
            ("application_schematic", "Application Schematic"),
            ("pin_diagram", "Pin Diagram"),
            ("vi_characteristics", "V-I Characteristics"),
            ("waveform_diagram", "Waveform Diagram"),
            ("equivalent_circuit", "Equivalent Circuit"),
            ("types_diagram", "Component Types")
        ]
        
        valid_tabs_count = 0
        for key, name in category_mappings:
            path = images_config.get(key)
            if path and str(path).strip():
                box = self.create_image_container(name, path)
                if box:
                    tab_widget = QWidget()
                    t_lay = QVBoxLayout(tab_widget)
                    t_lay.setContentsMargins(10, 10, 10, 10)
                    t_lay.addWidget(box)
                    views_tabs.addTab(tab_widget, name)
                    valid_tabs_count += 1
                    
        if valid_tabs_count == 0:
            tab_widget = QWidget()
            t_lay = QVBoxLayout(tab_widget)
            t_lay.setContentsMargins(10, 10, 10, 10)
            empty_lbl = QLabel("Educational visuals for this component are currently being compiled.")
            empty_lbl.setStyleSheet("color: #64748b; font-style: italic; font-size: 9.5pt;")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t_lay.addWidget(empty_lbl)
            views_tabs.addTab(tab_widget, "Overview")
            
        explorer_layout.addWidget(views_tabs)
        self.right_layout.addWidget(explorer_card)
        
        # 4. Package Comparison Matrix (if supported component)
        package_info = self.get_component_package_matrix(comp_id)
        if package_info:
            compare_card = QFrame()
            compare_card.setObjectName("compare-card")
            compare_card.setStyleSheet("""
                QFrame#compare-card {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            compare_layout = QVBoxLayout(compare_card)
            c_title = QLabel("Package Comparison Matrix")
            c_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt; margin-bottom: 8px;")
            compare_layout.addWidget(c_title)
            
            # Setup Table Widget
            headers = package_info["headers"]
            rows = package_info["rows"]
            
            tbl = QTableWidget(len(rows), len(headers))
            tbl.setHorizontalHeaderLabels(headers)
            tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            tbl.verticalHeader().setVisible(False)
            tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            tbl.setStyleSheet("""
                QTableWidget {
                    background-color: #0b0f19;
                    color: #f8fafc;
                    gridline-color: #1e293b;
                    border: 1px solid #1e293b;
                }
                QHeaderView::section {
                    background-color: #1e293b;
                    color: #06b6d4;
                    font-weight: bold;
                    padding: 6px;
                    border: none;
                }
            """)
            
            for r, row_data in enumerate(rows):
                for c, val in enumerate(row_data):
                    tbl.setItem(r, c, QTableWidgetItem(val))
                    
            compare_layout.addWidget(tbl)
            self.right_layout.addWidget(compare_card)
            
        # 5. Advanced Pinout Explorer
        if pin_list:
            pinout_card = QFrame()
            pinout_card.setObjectName("pinout-card")
            pinout_card.setStyleSheet("""
                QFrame#pinout-card {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            pinout_layout = QVBoxLayout(pinout_card)
            
            p_title = QLabel("Advanced Pinout Explorer")
            p_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt; margin-bottom: 8px;")
            pinout_layout.addWidget(p_title)
            
            splitter = QSplitter(Qt.Orientation.Horizontal)
            splitter.setStyleSheet("background: transparent;")
            
            # Left: Interactive Pin List
            pin_list_widget = QListWidget()
            pin_list_widget.setStyleSheet("""
                QListWidget {
                    background-color: #0b0f19;
                    border: 1px solid #1e293b;
                    border-radius: 6px;
                    color: #f8fafc;
                }
                QListWidget::item {
                    padding: 8px 10px;
                    border-bottom: 1px solid #1e293b;
                }
                QListWidget::item:hover {
                    background-color: #1e293b;
                    color: #06b6d4;
                }
                QListWidget::item:selected {
                    background-color: #1e293b;
                    color: #06b6d4;
                    font-weight: bold;
                }
            """)
            
            for pin in pin_list:
                pin_list_widget.addItem(f"Pin {pin['num']}: {pin['name']}")
                
            # Right: Pin Details Card
            detail_card = QFrame()
            detail_card.setStyleSheet("background-color: #111827; border: 1px solid #1e293b; border-radius: 6px;")
            dt_lay = QVBoxLayout(detail_card)
            dt_lay.setContentsMargins(10, 10, 10, 10)
            
            self.p_num_lbl = QLabel("Select a pin on the left to inspect electrical characteristics.")
            self.p_num_lbl.setStyleSheet("color: #06b6d4; font-weight: bold; font-size: 11pt;")
            self.p_num_lbl.setWordWrap(True)
            
            self.p_func_lbl = QLabel("")
            self.p_func_lbl.setStyleSheet("color: #e2e8f0; font-size: 9.5pt;")
            self.p_func_lbl.setWordWrap(True)
            
            self.p_specs_lbl = QLabel("")
            self.p_specs_lbl.setStyleSheet("color: #94a3b8; font-size: 9pt; line-height: 1.4;")
            self.p_specs_lbl.setWordWrap(True)
            
            dt_lay.addWidget(self.p_num_lbl)
            dt_lay.addWidget(self.p_func_lbl)
            dt_lay.addWidget(self.p_specs_lbl)
            dt_lay.addStretch()
            
            # Interactive selection handler
            def on_pin_selected(item_row):
                pin = pin_list[item_row]
                self.p_num_lbl.setText(f"Pin {pin['num']} — {pin['name']}")
                self.p_func_lbl.setText(f"Function:\n{pin['func']}")
                self.p_specs_lbl.setText(
                    f"Signal Type: {pin['type']}\n"
                    f"Typical Voltage: {pin['volt']}\n"
                    f"Typical Current: {pin['curr']}\n\n"
                    f"💡 Connection Tip:\n{pin['tip']}\n\n"
                    f"⚠️ Common Mistake:\n{pin['mistake']}"
                )
                
            pin_list_widget.currentRowChanged.connect(on_pin_selected)
            if pin_list:
                pin_list_widget.setCurrentRow(0) # Load first pin default
                
            splitter.addWidget(pin_list_widget)
            splitter.addWidget(detail_card)
            splitter.setSizes([120, 280])
            pinout_layout.addWidget(splitter)
            self.right_layout.addWidget(pinout_card)
            
        # 6. Equivalent, Selection Guide, and Related Parts card
        extra_info = self.get_component_extra_metadata(comp_id)
        if extra_info:
            edu_card = QFrame()
            edu_card.setObjectName("edu-card")
            edu_card.setStyleSheet("""
                QFrame#edu-card {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            edu_layout = QVBoxLayout(edu_card)
            
            # Equivalents Row
            eq_title = QLabel("Equivalent Part Numbers")
            eq_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 10.5pt;")
            edu_layout.addWidget(eq_title)
            
            eqs_str = ", ".join(extra_info["equivalents"])
            eqs_lbl = QLabel(eqs_str)
            eqs_lbl.setStyleSheet("color: #06b6d4; font-size: 9.5pt; font-weight: bold; margin-bottom: 12px;")
            edu_layout.addWidget(eqs_lbl)
            
            # Selection Guide
            sel_title = QLabel("Selection Guide")
            sel_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 10.5pt;")
            edu_layout.addWidget(sel_title)
            
            sel_lbl = QLabel(extra_info["selection_guide"])
            sel_lbl.setStyleSheet("color: #94a3b8; font-size: 9.5pt; line-height: 1.45; margin-bottom: 12px;")
            sel_lbl.setWordWrap(True)
            edu_layout.addWidget(sel_lbl)
            
            # Manufacturers Examples
            mfg_title = QLabel("Common Manufacturers")
            mfg_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 10.5pt;")
            edu_layout.addWidget(mfg_title)
            
            mfgs_str = ", ".join(extra_info["manufacturers"])
            mfg_lbl = QLabel(mfgs_str)
            mfg_lbl.setStyleSheet("color: #e2e8f0; font-size: 9.5pt; margin-bottom: 12px;")
            edu_layout.addWidget(mfg_lbl)
            
            # Related Components Links
            rel_title = QLabel("Related Parts (Click to view)")
            rel_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 10.5pt; margin-bottom: 5px;")
            edu_layout.addWidget(rel_title)
            
            btn_layout = QHBoxLayout()
            for rel_id in extra_info["related"]:
                rel_name = rel_id.replace("_", " ").title()
                rel_btn = QPushButton(rel_name)
                rel_btn.setObjectName("secondary")
                rel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                rel_btn.clicked.connect(lambda checked=False, target_cid=rel_id: self.select_component_by_id(target_cid))
                btn_layout.addWidget(rel_btn)
            edu_layout.addLayout(btn_layout)
            
            self.right_layout.addWidget(edu_card)
            
        # 7. "Where is this used?" Section
        sim_mapping = {
            "resistor": ("Voltage Divider Visual", 8),
            "capacitor": ("RC Charging/Discharging", 0),
            "inductor": ("RL Transient Response", 1),
            "pn_diode": ("Half-Wave Rectifier", 5),
            "zener_diode": ("Series RLC Resonance", 2), # Or fallback
            "led": ("RC Charging/Discharging", 0),
            "555_timer": ("RC Charging/Discharging", 0) # Fallback simulator
        }
        
        usage_card = QFrame()
        usage_card.setObjectName("usage-card")
        usage_card.setStyleSheet("""
            QFrame#usage-card {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        usage_layout = QVBoxLayout(usage_card)
        u_title = QLabel("Where is this used?")
        u_title.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 11pt; margin-bottom: 8px;")
        usage_layout.addWidget(u_title)
        
        if comp_id in sim_mapping:
            sim_name, sim_idx = sim_mapping[comp_id]
            desc_lbl = QLabel(f"This component is actively simulated in our mathematical lab engine: {sim_name}.")
            desc_lbl.setStyleSheet("color: #94a3b8; font-size: 9.5pt; margin-bottom: 8px;")
            usage_layout.addWidget(desc_lbl)
            
            try_btn = QPushButton(" Try in Simulator")
            try_btn.setIcon(qta.icon("fa5s.flask", color="#ffffff"))
            try_btn.clicked.connect(lambda: self.window().navigate_to_simulation(sim_idx))
            usage_layout.addWidget(try_btn)
        else:
            empty_desc = QLabel("Currently unavailable in Simulation Lab. Detailed explanations and waveforms are available in Learning Mode.")
            empty_desc.setStyleSheet("color: #64748b; font-style: italic; font-size: 9.5pt;")
            empty_desc.setWordWrap(True)
            usage_layout.addWidget(empty_desc)
            
        self.right_layout.addWidget(usage_card)
        
        # 8. Specifications Table Card
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
            
        # 9. Expandable Sections (Accordion)
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
                text_lbl = QLabel(str(content))
                text_lbl.setWordWrap(True)
                text_lbl.setStyleSheet("color: #e2e8f0; font-size: 9.5pt; line-height: 1.45;")
                panel.content_layout.addWidget(text_lbl)
                
            self.right_layout.addWidget(panel)
            
        self.right_layout.addStretch()

    def select_component_by_id(self, comp_id):
        """Finds and selects the target component in the category tree programmatically."""
        for i in range(self.tree_widget.topLevelItemCount()):
            cat_item = self.tree_widget.topLevelItem(i)
            for j in range(cat_item.childCount()):
                child = cat_item.child(j)
                if child.data(0, Qt.ItemDataRole.UserRole) == comp_id:
                    self.tree_widget.setCurrentItem(child)
                    self.on_item_clicked(child)
                    return

    def toggle_component_favorite(self, comp_id):
        """Mark or unmark a component as favorite."""
        favs = config_manager.get("favorites") or []
        if comp_id in favs:
            favs.remove(comp_id)
            self.show_toast_message(f"Removed {comp_id.replace('_', ' ').title()} from Favorites.")
        else:
            favs.append(comp_id)
            self.show_toast_message(f"Added {comp_id.replace('_', ' ').title()} to Favorites.")
            
        config_manager.set("favorites", favs)
        
        # Repaint star icon
        is_fav = comp_id in favs
        self.star_btn.setIcon(qta.icon("fa5s.star", color="#f59e0b" if is_fav else "#475569"))

    def show_toast_message(self, text):
        win = self.window()
        if win and hasattr(win, "show_toast"):
            win.show_toast(text)

    def open_datasheet_url(self, url):
        """Redirects to official datasheet links or alldatasheet."""
        import webbrowser
        webbrowser.open(url)

    def get_component_pins_metadata(self, comp_id):
        """Returns verified pins list metadata for the component."""
        pins_db = {
            "555_timer": [
                {"num": 1, "name": "GND", "package": "DIP-8", "func": "Ground reference.", "type": "Ground", "volt": "0V", "curr": "0A", "tip": "Connect directly to the common ground plane.", "mistake": "Leaving unconnected causes timer malfunction."},
                {"num": 2, "name": "TRIG", "package": "DIP-8", "func": "Initiates timing cycle when voltage drops below 1/3 VCC.", "type": "Analog Input", "volt": "0V - VCC", "curr": "<1uA", "tip": "Use pull-up resistor to VCC to keep it high until triggered.", "mistake": "Leaving floating causes noise triggers."},
                {"num": 3, "name": "OUT", "package": "DIP-8", "func": "Main digital timing output signal.", "type": "Digital Output", "volt": "0V - VCC", "curr": "Up to 200mA", "tip": "Can drive small relays, LEDs, or speaker transducers directly.", "mistake": "Connecting to VCC or GND without load will damage the internal output stage."},
                {"num": 4, "name": "RESET", "package": "DIP-8", "func": "Resets timing cycle when pulled below 0.4V.", "type": "Digital Input", "volt": "0V - VCC", "curr": "<1uA", "tip": "Connect to VCC if reset functionality is not needed.", "mistake": "Leaving floating triggers random resets."},
                {"num": 5, "name": "CONT", "package": "DIP-8", "func": "Accesses the internal 2/3 VCC divider node.", "type": "Analog Input", "volt": "2/3 VCC", "curr": "<1uA", "tip": "Bypass to ground with a 10nF ceramic capacitor for stability.", "mistake": "Connecting directly to a voltage supply destroys the internal divider."},
                {"num": 6, "name": "THRES", "package": "DIP-8", "func": "Ends timing cycle when voltage rises above 2/3 VCC.", "type": "Analog Input", "volt": "2/3 VCC", "curr": "<1uA", "tip": "Connect to external RC timing capacitor.", "mistake": "Leaving floating prevents output from turning off."},
                {"num": 7, "name": "DISCH", "package": "DIP-8", "func": "Discharges external timing capacitor.", "type": "Open-Collector", "volt": "0V - VCC", "curr": "15mA max", "tip": "Connects to capacitor junction. Discharges cap during reset phase.", "mistake": "Connecting directly to VCC causes a direct short circuit when activated."},
                {"num": 8, "name": "VCC", "package": "DIP-8", "func": "Positive supply voltage input.", "type": "Power Input", "volt": "4.5V - 16V", "curr": "10mA - 15mA", "tip": "Place a 0.1uF bypass capacitor close to this pin.", "mistake": "Reversing polarity or exceeding 18V will destroy the IC."}
            ],
            "op_amp": [
                {"num": 1, "name": "OFFSET NULL", "package": "DIP-8", "func": "Offset voltage nulling.", "type": "Analog Input", "volt": "N/A", "curr": "N/A", "tip": "Connect to offset pot ends.", "mistake": "Applying supply voltages directly destroys inputs."},
                {"num": 2, "name": "IN-", "package": "DIP-8", "func": "Inverting input terminal.", "type": "Analog Input", "volt": "-Vcc to +Vcc", "curr": "<1uA", "tip": "Applied feedback loops attach here.", "mistake": "Leaving floating causes op-amp to saturate."},
                {"num": 3, "name": "IN+", "package": "DIP-8", "func": "Non-inverting input terminal.", "type": "Analog Input", "volt": "-Vcc to +Vcc", "curr": "<1uA", "tip": "Reference input voltage level goes here.", "mistake": "Exceeding common mode voltage limits."},
                {"num": 4, "name": "V-", "package": "DIP-8", "func": "Negative voltage supply rail.", "type": "Power Input", "volt": "-5V to -15V", "curr": "5mA", "tip": "Connect to negative power supply rail.", "mistake": "Swapping supply rails destroys op-amp."},
                {"num": 5, "name": "OFFSET NULL", "package": "DIP-8", "func": "Offset voltage nulling.", "type": "Analog Input", "volt": "N/A", "curr": "N/A", "tip": "Connect to offset pot ends.", "mistake": "Applying supply voltages directly."},
                {"num": 6, "name": "OUT", "package": "DIP-8", "func": "Amplified analog output.", "type": "Analog Output", "volt": "-Vcc to +Vcc", "curr": "25mA", "tip": "Place small load resistor to limit output current.", "mistake": "Shorting directly to ground causes thermal overload."},
                {"num": 7, "name": "V+", "package": "DIP-8", "func": "Positive voltage supply rail.", "type": "Power Input", "volt": "5V to 15V", "curr": "5mA", "tip": "Bypass with 0.1uF capacitor.", "mistake": "Exceeding absolute maximum supply bounds."},
                {"num": 8, "name": "NC", "package": "DIP-8", "func": "No internal connection.", "type": "Unused", "volt": "N/A", "curr": "N/A", "tip": "Leave floating.", "mistake": "Using as circuit tie point."}
            ],
            "bjt": [
                {"num": 1, "name": "Collector", "package": "TO-92", "func": "Collects majority carriers.", "type": "Analog Input/Output", "volt": "0V - 45V", "curr": "100mA max", "tip": "Connect to high potential load node.", "mistake": "Exceeding breakdown collector voltage Vceo."},
                {"num": 2, "name": "Base", "package": "TO-92", "func": "Base control terminal.", "type": "Analog Input", "volt": "0.7V", "curr": "5mA max", "tip": "Always use a base series resistor to limit current.", "mistake": "Connecting directly to VCC without limit resistor destroys base junction."},
                {"num": 3, "name": "Emitter", "package": "TO-92", "func": "Emits majority carriers.", "type": "Analog Output", "volt": "0V", "curr": "105mA max", "tip": "Connect to ground in common emitter mode.", "mistake": "Applying negative voltages exceeding 6V."}
            ],
            "mosfet": [
                {"num": 1, "name": "Gate", "package": "TO-220", "func": "Voltage gate switcher.", "type": "Analog Input", "volt": "-20V to +20V", "curr": "<1uA", "tip": "Use gate damping resistor (100 Ohm) to suppress oscillations.", "mistake": "Leaving floating causes static accumulation and turns MOSFET ON unexpectedly."},
                {"num": 2, "name": "Drain", "package": "TO-220", "func": "Drain current terminal.", "type": "Power Output", "volt": "0V - 100V", "curr": "Up to 28A", "tip": "Add heatsink for continuous switching loads above 2A.", "mistake": "Exceeding drain-source breakdown threshold."},
                {"num": 3, "name": "Source", "package": "TO-220", "func": "Source current return.", "type": "Power Input", "volt": "0V", "curr": "Up to 28A", "tip": "Connect directly to common power ground return loop.", "mistake": "Poor contact creates high resistance and heating."}
            ]
        }
        
        # Generic fallback pin generator if not listed
        if comp_id not in pins_db:
            return [
                {"num": 1, "name": "Anode / Lead A", "package": "Axial/Through-hole", "func": "Positive terminal connection.", "type": "Analog Connection", "volt": "Variable", "curr": "Variable", "tip": "Connect to high potential circuit node.", "mistake": "Reversing polarized components."},
                {"num": 2, "name": "Cathode / Lead B", "package": "Axial/Through-hole", "func": "Negative terminal connection.", "type": "Analog Connection", "volt": "Variable", "curr": "Variable", "tip": "Connect to low potential or ground node.", "mistake": "Shorting terminal directly to VCC."}
            ]
            
        return pins_db[comp_id]

    def get_component_package_matrix(self, comp_id):
        """Returns comparison matrix database for component packages."""
        matrix_db = {
            "resistor": {
                "headers": ["Feature", "Axial Through-hole", "SMD (Surface Mount)"],
                "rows": [
                    ["Power Rating", "0.25W - 5W", "0.0625W - 1W"],
                    ["Heat Dissipation", "Excellent", "Moderate"],
                    ["Breadboard Prototyping", "Directly compatible", "Needs SMD breakout board"],
                    ["Common Size code", "Color bands (Length 6mm)", "0805, 0603, 1206 standard"]
                ]
            },
            "capacitor": {
                "headers": ["Feature", "Electrolytic Radial", "Ceramic Disc"],
                "rows": [
                    ["Typical Capacity", "1 uF to 10 mF", "1 pF to 1 uF"],
                    ["Polarization", "Polarized (Must match +/-)", "Non-polarized"],
                    ["Max Voltage Range", "10V to 450V", "50V to kV (High Voltage)"],
                    ["ESR & High-Freq Loss", "High loss at high-freq", "Very low ESR (Ideal bypass cap)"]
                ]
            },
            "bjt": {
                "headers": ["Feature", "TO-92 Package", "SOT-23 Package"],
                "rows": [
                    ["Power Dissipation", "625 mW max", "350 mW max"],
                    ["Mounting", "Through-hole", "Surface Mount (SMD)"],
                    ["Thermal Resistance", "140 °C/W", "350 °C/W"],
                    ["Ideal Application", "Breadboard, low power logic", "Compact PCBs, automated pick-place"]
                ]
            },
            "mosfet": {
                "headers": ["Feature", "TO-220 Package", "DPAK Package"],
                "rows": [
                    ["Power Dissipation", "Up to 150W", "Up to 50W"],
                    ["Heat Dissipation", "Requires external heatsink", "Dissipates via PCB copper pad"],
                    ["Max Continuous Current", "Up to 110A", "Up to 30A"],
                    ["Prototyping Use", "Breadboard compatible", "Surface Mount only"]
                ]
            },
            "555_timer": {
                "headers": ["Feature", "DIP-8 Package", "SOIC-8 Package"],
                "rows": [
                    ["Power Dissipation", "600 mW", "300 mW"],
                    ["Mounting Type", "Through-hole / Socket", "Surface Mount (SMD)"],
                    ["Dimensions", "9.27mm x 6.35mm", "4.9mm x 3.9mm"],
                    ["Breadboard Friendly", "Yes", "No (Needs adapter)"]
                ]
            },
            "op_amp": {
                "headers": ["Feature", "DIP-8 Package", "SOIC-8 Package"],
                "rows": [
                    ["Power Dissipation", "500 mW", "250 mW"],
                    ["Mounting Type", "Through-hole", "Surface Mount"],
                    ["Breadboard Friendly", "Yes", "No (Requires breakout adapter)"],
                    ["Temperature Rating", "-40 to +85 °C", "-40 to +85 °C"]
                ]
            }
        }
        return matrix_db.get(comp_id)

    def get_component_extra_metadata(self, comp_id):
        """Returns equivalents, selection guide, and related parts metadata."""
        extra_db = {
            "resistor": {
                "equivalents": ["Metal Film Resistor", "Carbon Film Resistor", "Wirewound Resistor"],
                "selection_guide": "Choose Carbon Film for general low-cost circuits. Choose Metal Film for low noise precision applications. Choose Wirewound for high-power loading.",
                "manufacturers": ["Yageo", "Vishay", "Panasonic", "KOA Speer"],
                "related": ["capacitor", "potentiometer", "inductor"]
            },
            "capacitor": {
                "equivalents": ["Tantalum Capacitor", "Film Capacitor", "Supercapacitor"],
                "selection_guide": "Choose Ceramic for high-frequency bypass and decoupling. Choose Electrolytic for power supply smoothing. Choose Tantalum for high-stability low-leakage.",
                "manufacturers": ["Murata", "TDK", "KEMET", "Nichicon"],
                "related": ["resistor", "inductor", "zener_diode"]
            },
            "bjt": {
                "equivalents": ["BC548", "2N3904", "2N2222", "PN2222"],
                "selection_guide": "Choose BC547 for general low-noise small-signal switching. Choose 2N2222 for higher current amplification requirements (up to 800mA).",
                "manufacturers": ["ON Semiconductor", "NXP", "STMicroelectronics", "Infineon"],
                "related": ["mosfet", "led", "op_amp"]
            },
            "mosfet": {
                "equivalents": ["IRF540N", "BUZ11", "FQP30N06L (Logic Level)"],
                "selection_guide": "Choose IRF540N for high-voltage power switching (up to 100V). Choose logic-level gates (e.g. FQP30N06L) when switching directly from 5V Arduino pins.",
                "manufacturers": ["Infineon Technologies", "STMicroelectronics", "Vishay Siliconix", "ON Semiconductor"],
                "related": ["bjt", "relay", "555_timer"]
            },
            "555_timer": {
                "equivalents": ["NE555", "LM555", "SE555", "TLC555 (CMOS low-power)"],
                "selection_guide": "Use NE555 for general purpose timing and oscillation circuits. Choose TLC555 (CMOS) for battery-operated devices to keep idle current minimal.",
                "manufacturers": ["Texas Instruments", "STMicroelectronics", "ON Semiconductor", "Microchip"],
                "related": ["op_amp", "capacitor", "resistor"]
            },
            "op_amp": {
                "equivalents": ["LM741", "TL071 (JFET input)", "NE5534 (Low noise audio)", "OP07 (Low offset)"],
                "selection_guide": "Choose LM741 for basic educational circuits. Choose TL071 for high input impedance audio preamps. Choose OP07 for precision instrumentation amplifiers.",
                "manufacturers": ["Analog Devices", "Texas Instruments", "STMicroelectronics", "Maxim Integrated"],
                "related": ["555_timer", "bjt", "resistor"]
            }
        }
        
        # Generic fallback
        if comp_id not in extra_db:
            return {
                "equivalents": ["Industry Standard Replacements"],
                "selection_guide": "Check datasheet maximum voltage, current, and temperature constraints prior to part selection.",
                "manufacturers": ["Multiple Standard Industry Vendors"],
                "related": ["resistor", "capacitor"]
            }
            
        return extra_db[comp_id]

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
            main_win.switch_view(4)
            sim_view = main_win.views[4]
            row_idx = exp_to_row.get(exp_name)
            if row_idx is not None:
                sim_view.list_widget.setCurrentRow(row_idx)

