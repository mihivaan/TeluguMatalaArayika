"""
తెలుగు మాటల అరయిక (TLRE)

Desktop Graphical User Interface — 2D Knowledge Graph View

Version: 0.2.0
Reference Point: RP-006

Interactive 2D graph workspace for visualizing word relationships,
compound roots, cognates, and variants.
"""

from __future__ import annotations

import math
import sys
from typing import Any, Optional

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models import Relationship
from src.queries import get_entry_by_id, get_relationships_for_entry


RELATIONSHIP_EDGE_COLOURS = {
    "derived_from": "#2B6CB0",
    "reconstructed_from": "#2B6CB0",
    "compound_of": "#2F855A",
    "variant_of": "#D69E2E",
    "dialect_variant": "#D69E2E",
    "synonym_of": "#805AD5",
    "antonym_of": "#805AD5",
    "semantic_shift_from": "#805AD5",
}


def relationship_colour(rel_type: str) -> QColor:
    return QColor(RELATIONSHIP_EDGE_COLOURS.get(rel_type, "#604B39"))


def _as_attr(obj: Any, *names: str, default: Any = None) -> Any:
    if obj is None:
        return default

    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
        try:
            if isinstance(obj, dict) and name in obj and obj[name] is not None:
                return obj[name]
        except Exception:
            pass
    return default


def _entry_headword(entry: Any) -> str:
    value = _as_attr(
        entry,
        "headword",
        "word",
        "lemma",
        "term",
        "name",
        "entry_name",
        "canonical_form",
        default="",
    )
    return "" if value is None else str(value)


def _entry_classification(entry: Any) -> str:
    value = _as_attr(
        entry,
        "classification",
        "category",
        "part_of_speech",
        "pos",
        "word_class",
        "entry_type",
        "type",
        "label",
        default="",
    )
    return "" if value is None else str(value)


def _relationship_label(rel: Relationship) -> str:
    confidence = f"{rel.confidence:.2f}".rstrip("0").rstrip(".")
    return f"{rel.relationship_type} · {confidence}"


def _polygon_arrow_head(end: QPointF, direction: QPointF, size: float = 12.0) -> QPolygonF:
    length = math.hypot(direction.x(), direction.y())
    if length <= 1e-9:
        return QPolygonF()

    ux = direction.x() / length
    uy = direction.y() / length

    px = -uy
    py = ux

    tip = end
    base = QPointF(end.x() - ux * size, end.y() - uy * size)
    left = QPointF(base.x() + px * (size * 0.45), base.y() + py * (size * 0.45))
    right = QPointF(base.x() - px * (size * 0.45), base.y() - py * (size * 0.45))
    return QPolygonF([tip, left, right])


class WordNodeItem(QGraphicsRectItem):
    """
    Styled 2D card/pill for a Telugu word node.
    """

    def __init__(self, entry: Any, width: float = 220.0, height: float = 74.0) -> None:
        super().__init__(0.0, 0.0, width, height)
        self.entry = entry
        self.connected_edges: list["RelationshipEdgeItem"] = []

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
            | QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
        )
        self.setAcceptHoverEvents(True)
        self.setZValue(10)

        self._headword = _entry_headword(entry)
        self._classification = _entry_classification(entry)

        self._padding = 14.0
        self._corner_radius = 18.0
        self._normal_fill = QColor("#F7F5EF")
        self._normal_border = QColor("#4A3B2E")
        self._selected_fill = QColor("#FFF3D6")
        self._selected_border = QColor("#A36A00")
        self._shadow_border = QColor("#D5CCBF")

        self._title_item = QGraphicsSimpleTextItem(self._headword, self)
        self._subtitle_item = QGraphicsSimpleTextItem(self._classification, self)

        title_font = QFont()
        title_font.setFamily("Noto Sans Telugu")
        title_font.setPointSize(12)
        title_font.setBold(True)
        self._title_item.setFont(title_font)
        self._title_item.setBrush(QColor("#1A1A1A"))

        subtitle_font = QFont()
        subtitle_font.setFamily("Noto Sans Telugu")
        subtitle_font.setPointSize(9)
        self._subtitle_item.setFont(subtitle_font)
        self._subtitle_item.setBrush(QColor("#555555"))

        self._reflow_text()
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def add_edge(self, edge: "RelationshipEdgeItem") -> None:
        if edge not in self.connected_edges:
            self.connected_edges.append(edge)

    def _reflow_text(self) -> None:
        rect = self.rect()
        left = rect.left() + self._padding
        top = rect.top() + self._padding

        self._title_item.setPos(left, top)
        title_bounds = self._title_item.boundingRect()
        subtitle_y = top + title_bounds.height() + 5.0
        self._subtitle_item.setPos(left, subtitle_y)

    def set_headword(self, text: str) -> None:
        self._headword = text
        self._title_item.setText(text)
        self._reflow_text()
        self.update()

    def set_classification(self, text: str) -> None:
        self._classification = text
        self._subtitle_item.setText(text)
        self._reflow_text()
        self.update()

    def boundingRect(self) -> QRectF:
        return super().boundingRect().adjusted(-2.0, -2.0, 2.0, 2.0)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # noqa: ANN001
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = self.rect()
        is_selected = bool(self.isSelected())

        fill = self._selected_fill if is_selected else self._normal_fill
        border = self._selected_border if is_selected else self._normal_border

        painter.setPen(QPen(self._shadow_border, 2.0))
        painter.setBrush(fill)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), self._corner_radius, self._corner_radius)

        painter.setPen(QPen(border, 2.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), self._corner_radius, self._corner_radius)

        accent = QRectF(rect.left() + 1.0, rect.top() + 1.0, 6.0, rect.height() - 2.0)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#B9833B") if not is_selected else QColor("#D48B00"))
        painter.drawRoundedRect(accent, 3.0, 3.0)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.connected_edges:
                edge.update_path()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.update()
        return super().itemChange(change, value)


class RelationshipEdgeItem(QGraphicsPathItem):
    """
    Directed arrow edge between two WordNodeItem objects, with label.
    """

    def __init__(
        self,
        from_node: WordNodeItem,
        to_node: WordNodeItem,
        relationship: Relationship,
    ) -> None:
        super().__init__()
        self.from_node = from_node
        self.to_node = to_node
        self.relationship = relationship

        self.setZValue(1)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

        self._edge_colour = relationship_colour(relationship.relationship_type)
        self._pen = QPen(self._edge_colour, 2.0)
        self._pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self._pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        self._label_item = QGraphicsSimpleTextItem(_relationship_label(relationship), self)
        label_font = QFont()
        label_font.setPointSize(8)
        label_font.setBold(True)
        self._label_item.setFont(label_font)
        self._label_item.setBrush(self._edge_colour)
        self._label_item.setZValue(3)

        self._arrow_polygon = QPolygonF()

        self.from_node.add_edge(self)
        self.to_node.add_edge(self)
        self.update_path()

    def boundingRect(self) -> QRectF:
        """
        Expand bounding box so erasing clears arrowhead and label during drag.
        """
        path_rect = super().boundingRect()
        return path_rect.adjusted(-25.0, -25.0, 25.0, 25.0)

    def _node_attachment_point(
        self,
        source_scene_point: QPointF,
        target_scene_point: QPointF,
        node: WordNodeItem,
    ) -> QPointF:
        rect = node.sceneBoundingRect()
        center = rect.center()
        dx = target_scene_point.x() - source_scene_point.x()
        dy = target_scene_point.y() - source_scene_point.y()

        if abs(dx) < 1e-9 and abs(dy) < 1e-9:
            return center

        half_w = rect.width() / 2.0
        half_h = rect.height() / 2.0
        if abs(dx) * half_h > abs(dy) * half_w:
            scale = half_w / abs(dx) if abs(dx) > 1e-9 else 0.0
        else:
            scale = half_h / abs(dy) if abs(dy) > 1e-9 else 0.0

        scale = max(0.0, scale)
        return QPointF(center.x() + dx * scale, center.y() + dy * scale)

    def update_path(self) -> None:
        # Crucial: notify Qt that edge bounds/geometry is changing BEFORE recalculating!
        self.prepareGeometryChange()

        start_center = self.from_node.sceneBoundingRect().center()
        end_center = self.to_node.sceneBoundingRect().center()

        start = self._node_attachment_point(start_center, end_center, self.from_node)
        end = self._node_attachment_point(end_center, start_center, self.to_node)

        dx = end.x() - start.x()
        dy = end.y() - start.y()
        distance = math.hypot(dx, dy)

        if distance < 40.0:
            control_1 = QPointF((start.x() + end.x()) / 2.0, (start.y() + end.y()) / 2.0)
            control_2 = control_1
        else:
            perp_x = -dy / distance
            perp_y = dx / distance
            curve = min(90.0, distance * 0.22)

            control_1 = QPointF(
                start.x() + dx * 0.33 + perp_x * curve,
                start.y() + dy * 0.33 + perp_y * curve,
            )
            control_2 = QPointF(
                start.x() + dx * 0.67 + perp_x * curve,
                start.y() + dy * 0.67 + perp_y * curve,
            )

        path = QPainterPath(start)
        path.cubicTo(control_1, control_2, end)
        self.setPath(path)

        mid = path.pointAtPercent(0.5)
        label_rect = self._label_item.boundingRect()
        self._label_item.setPos(mid.x() - label_rect.width() / 2.0, mid.y() - label_rect.height() - 6.0)

        end_pct = 0.995
        tail_pct = 0.965
        end_pt = path.pointAtPercent(end_pct)
        tail_pt = path.pointAtPercent(tail_pct)
        direction = QPointF(end_pt.x() - tail_pt.x(), end_pt.y() - tail_pt.y())
        self._arrow_polygon = _polygon_arrow_head(end_pt, direction, size=13.0)

        self.update()

    def paint(self, painter: QPainter, option, widget=None) -> None:  # noqa: ANN001
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.setPen(self._pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())

        if not self._arrow_polygon.isEmpty():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._pen.color())
            painter.drawPolygon(self._arrow_polygon)


class LinguisticGraphView(QGraphicsView):
    """
    Graph view with grid background, wheel zooming, and middle-mouse panning.
    """

    def __init__(self, scene: Optional[QGraphicsScene] = None, parent: Optional[QWidget] = None) -> None:
        super().__init__(scene, parent)
        self._zoom_factor_min = 0.18
        self._zoom_factor_max = 4.5
        self._current_zoom = 1.0
        self._panning = False
        self._pan_start = QPoint()

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        # FullViewportUpdate ensures clean repainting without ghosting during node drag
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
        self.setBackgroundBrush(QColor("#F6F1E8"))

    def wheelEvent(self, event) -> None:  # noqa: ANN001
        delta = event.angleDelta().y()
        if delta == 0:
            event.ignore()
            return

        factor = 1.15 if delta > 0 else 1 / 1.15
        new_zoom = self._current_zoom * factor

        if not (self._zoom_factor_min <= new_zoom <= self._zoom_factor_max):
            event.accept()
            return

        self.scale(factor, factor)
        self._current_zoom = new_zoom
        event.accept()

    def mousePressEvent(self, event) -> None:  # noqa: ANN001
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: ANN001
        if self._panning:
            delta = event.position().toPoint() - self._pan_start
            self._pan_start = event.position().toPoint()

            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: ANN001
        if event.button() == Qt.MouseButton.MiddleButton and self._panning:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawBackground(painter, rect)

        grid_size = 30.0
        fine_pen = QPen(QColor(225, 220, 210), 1.0)
        coarse_pen = QPen(QColor(205, 198, 186), 1.0)

        left = math.floor(rect.left() / grid_size) * grid_size
        top = math.floor(rect.top() / grid_size) * grid_size

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        x = left
        while x < rect.right():
            is_coarse = int(round(x / grid_size)) % 5 == 0
            painter.setPen(coarse_pen if is_coarse else fine_pen)
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x += grid_size

        y = top
        while y < rect.bottom():
            is_coarse = int(round(y / grid_size)) % 5 == 0
            painter.setPen(coarse_pen if is_coarse else fine_pen)
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y += grid_size

        painter.restore()


class LinguisticGraphWindow(QMainWindow):
    """
    Main window for displaying the interactive 2D Knowledge Graph.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("TLRE — Linguistic Graph Workspace")

        # --------------------------------------------------
        # Screen-Aware Dynamic Sizing & Centering
        # --------------------------------------------------
        screen = QApplication.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            width = min(1200, int(geo.width() * 0.85))
            height = min(750, int(geo.height() * 0.85))
            self.resize(width, height)

            center_x = geo.left() + (geo.width() - width) // 2
            center_y = geo.top() + (geo.height() - height) // 2
            self.move(center_x, max(40, center_y))
        else:
            self.resize(1000, 650)

        # --------------------------------------------------
        # Main Layout & Clean Top Control Bar
        # --------------------------------------------------
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        control_bar = QWidget()
        control_bar.setStyleSheet("background: #EAE3D2; border-bottom: 1px solid #D5CCBF;")
        control_layout = QHBoxLayout(control_bar)
        control_layout.setContentsMargins(12, 6, 12, 6)

        title_label = QLabel("<b>Linguistic Knowledge Graph</b> (Drag nodes • Wheel zoom • Middle-mouse pan • Press <b>Esc</b> to close)")
        title_label.setStyleSheet("color: #4A3B2E; font-size: 13px;")

        control_layout.addWidget(title_label)
        control_layout.addStretch(1)

        main_layout.addWidget(control_bar)

        # --------------------------------------------------
        # Scene and View Setup
        # --------------------------------------------------
        self.scene = QGraphicsScene(self)
        self.scene.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        self.scene.setSceneRect(-2000.0, -2000.0, 4000.0, 4000.0)

        self.view = LinguisticGraphView(self.scene, self)
        main_layout.addWidget(self.view)

        self._node_cache: dict[int, WordNodeItem] = {}

    def keyPressEvent(self, event) -> None:  # noqa: ANN001
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def _entry_id(self, entry: Any) -> Optional[int]:
        raw = _as_attr(entry, "id", "entry_id", "pk", default=None)
        if raw is None:
            return None
        try:
            return int(raw)
        except Exception:
            return None

    def _make_node(self, entry: Any) -> WordNodeItem:
        node = WordNodeItem(entry)

        title_bounds = node._title_item.boundingRect()
        sub_bounds = node._subtitle_item.boundingRect()
        width = max(220.0, title_bounds.width() + 32.0, sub_bounds.width() + 32.0)
        height = 74.0
        node.setRect(0.0, 0.0, width, height)
        node._reflow_text()

        self.scene.addItem(node)
        return node

    def _get_or_create_node(self, entry: Any) -> Optional[WordNodeItem]:
        entry_id = self._entry_id(entry)
        if entry_id is None:
            return None

        node = self._node_cache.get(entry_id)
        if node is not None:
            return node

        node = self._make_node(entry)
        self._node_cache[entry_id] = node
        return node

    def load_graph_for_entry(self, entry_id: int) -> None:
        self.scene.clear()
        self._node_cache.clear()

        center_entry = get_entry_by_id(entry_id)
        if center_entry is None:
            placeholder = QGraphicsSimpleTextItem(f"Entry {entry_id} not found")
            placeholder.setBrush(QColor("#7A2E2E"))
            placeholder.setFont(QFont("Sans Serif", 14, QFont.Weight.Bold))
            placeholder.setPos(-120.0, -20.0)
            self.scene.addItem(placeholder)
            return

        center_node = self._make_node(center_entry)
        center_node.setPos(-center_node.rect().width() / 2.0, -center_node.rect().height() / 2.0)
        self._node_cache[entry_id] = center_node

        relationships = get_relationships_for_entry(entry_id) or []

        connected: list[tuple[Relationship, Any, int]] = []
        seen_other_ids: set[int] = set()

        for rel in relationships:
            if rel.from_entry_id == entry_id:
                other_id = rel.to_entry_id
            elif rel.to_entry_id == entry_id:
                other_id = rel.from_entry_id
            else:
                continue

            if other_id in seen_other_ids:
                continue

            other_entry = get_entry_by_id(other_id)
            if other_entry is None:
                continue

            seen_other_ids.add(other_id)
            connected.append((rel, other_entry, other_id))

        count = len(connected)
        if count == 0:
            self.scene.setSceneRect(-800.0, -600.0, 1600.0, 1200.0)
            self.view.resetTransform()
            self.view.centerOn(center_node)
            return

        base_radius = 310.0
        outer_radius = 420.0

        outgoing = []
        incoming = []
        for rel, other_entry, other_id in connected:
            if rel.from_entry_id == entry_id and rel.to_entry_id != entry_id:
                outgoing.append((rel, other_entry, other_id))
            else:
                incoming.append((rel, other_entry, other_id))

        ordered = outgoing + incoming
        count = len(ordered)

        for idx, (_rel, other_entry, other_id) in enumerate(ordered):
            node = self._get_or_create_node(other_entry)
            if node is None:
                continue

            angle = (2.0 * math.pi * idx) / max(1, count)
            radius = base_radius if idx < len(outgoing) else outer_radius

            x = math.cos(angle) * radius
            y = math.sin(angle) * radius

            node_width = node.rect().width()
            node_height = node.rect().height()
            pos = QPointF(x - node_width / 2.0, y - node_height / 2.0)
            node.setPos(pos)

        for rel in relationships:
            if rel.from_entry_id == entry_id:
                from_id, to_id = rel.from_entry_id, rel.to_entry_id
            elif rel.to_entry_id == entry_id:
                from_id, to_id = rel.from_entry_id, rel.to_entry_id
            else:
                continue

            from_entry = get_entry_by_id(from_id)
            to_entry = get_entry_by_id(to_id)
            if from_entry is None or to_entry is None:
                continue

            from_node = self._get_or_create_node(from_entry)
            to_node = self._get_or_create_node(to_entry)
            if from_node is None or to_node is None:
                continue

            edge = RelationshipEdgeItem(from_node, to_node, rel)
            self.scene.addItem(edge)

        bounds = self.scene.itemsBoundingRect().adjusted(-220.0, -220.0, 220.0, 220.0)
        self.scene.setSceneRect(bounds)

        self.view.resetTransform()
        self.view._current_zoom = 1.0
        self.view.centerOn(center_node)

        for item in self.scene.items():
            if isinstance(item, RelationshipEdgeItem):
                item.update_path()


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = LinguisticGraphWindow()
    window.load_graph_for_entry(1)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())