"""
Interactive charts using Plotly for modern, web-based visualizations.
These charts are more engaging and have hover effects, animations, and better styling.
"""
from typing import Dict, List, Tuple, Optional
import json

from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, pyqtSlot, Signal, QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QHBoxLayout

from models import FileCategory
from modern_styles import CATEGORY_COLORS, COLORS


class ChartBridge(QObject):
    """Bridge for communication between Python and JavaScript."""
    
    sliceClicked = Signal(str, float)
    barClicked = Signal(str, float)
    
    @pyqtSlot(str, float)
    def onSliceClick(self, label: str, value: float):
        self.sliceClicked.emit(label, value)
    
    @pyqtSlot(str, float)
    def onBarClick(self, label: str, value: float):
        self.barClicked.emit(label, value)


class BaseInteractiveChart(QWebEngineView):
    """Base class for interactive Plotly charts."""
    
    chartClicked = Signal(str, float)
    
    def __init__(self, parent=None, height: int = 400):
        super().__init__(parent)
        self.setMinimumHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Setup web channel for communication
        self.channel = QWebChannel(self.page())
        self.bridge = ChartBridge()
        self.channel.registerObject("bridge", self.bridge)
        self.page().setWebChannel(self.channel)
        
        # Connect signals
        self.bridge.sliceClicked.connect(self._on_chart_click)
        self.bridge.barClicked.connect(self._on_chart_click)
        
        # Dark theme base HTML
        self._base_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: {bg_color};
                    font-family: 'Segoe UI', sans-serif;
                }}
                #chart {{
                    width: 100%;
                    height: 100vh;
                }}
            </style>
        </head>
        <body>
            <div id="chart"></div>
            <script>
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    window.bridge = channel.objects.bridge;
                }});
                
                const layout = {layout};
                const config = {config};
                const data = {data};
                
                Plotly.newPlot('chart', data, layout, config);
                
                // Handle click events
                document.getElementById('chart').on('plotly_click', function(data) {{
                    if (data.points.length > 0) {
                        const pt = data.points[0];
                        const label = pt.label || pt.x || pt.name || '';
                        const value = pt.value || pt.y || pt.z || 0;
                        if (window.bridge) {{
                            window.bridge.onSliceClick(label, value);
                        }}
                    }
                }});
            </script>
        </body>
        </html>
        """
    
    def _on_chart_click(self, label: str, value: float):
        self.chartClicked.emit(label, value)
    
    def _get_common_layout(self, title: str) -> Dict:
        """Get common layout settings."""
        return {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#cdd6f4", "family": "Segoe UI, sans-serif"},
            "margin": {"t": 50, "b": 50, "l": 50, "r": 50},
            "title": {
                "text": title,
                "font": {"size": 16, "color": "#cdd6f4"},
                "x": 0.5,
                "xanchor": "center"
            },
            "hoverlabel": {
                "bgcolor": "#252536",
                "bordercolor": "#313244",
                "font": {"color": "#f8f8f8"}
            }
        }
    
    def _get_common_config(self) -> Dict:
        """Get common config settings."""
        return {
            "displayModeBar": False,
            "responsive": True,
            "displaylogo": False
        }
    
    def update_chart(self, data: List[Dict], layout: Dict, title: str = ""):
        """Update the chart with new data."""
        if title:
            layout = self._get_common_layout(title)
        else:
            layout["paper_bgcolor"] = "rgba(0,0,0,0)"
            layout["plot_bgcolor"] = "rgba(0,0,0,0)"
            layout["font"] = {"color": "#cdd6f4", "family": "Segoe UI, sans-serif"}
        
        config = self._get_common_config()
        
        html = self._base_html.format(
            bg_color=COLORS['bg_primary'],
            layout=json.dumps(layout),
            config=json.dumps(config),
            data=json.dumps(data)
        )
        
        self.setHtml(html)


class InteractivePieChart(BaseInteractiveChart):
    """Interactive donut chart for category distribution."""
    
    def __init__(self, parent=None):
        super().__init__(parent, height=380)
    
    def update_data(self, categories: Dict[FileCategory, float]):
        """Update chart with category data."""
        if not categories:
            self._show_empty()
            return
        
        labels = [cat.value for cat in categories.keys()]
        values = list(categories.values())
        colors = [CATEGORY_COLORS.get(cat.value, ("#94a3b8", "#64748b"))[0] 
                  for cat in categories.keys()]
        
        data = [{
            "type": "pie",
            "labels": labels,
            "values": values,
            "hole": 0.6,
            "marker": {
                "colors": colors,
                "line": {"color": "#0d0d12", "width": 2}
            },
            "textinfo": "label+percent",
            "textposition": "outside",
            "textfont": {"size": 12},
            "hovertemplate": "<b>%{label}</b><br>%{percent}<br>%{value:.1f}%<extra></extra>",
            "pull": [0.02] * len(labels),
            "rotation": 90
        }]
        
        layout = self._get_common_layout("")
        layout["showlegend"] = False
        layout["annotations"] = [{
            "text": "Storage",
            "x": 0.5,
            "y": 0.5,
            "font": {"size": 16, "color": "#cdd6f4", "weight": "bold"},
            "showarrow": False
        }]
        
        self.update_chart(data, layout)
    
    def _show_empty(self):
        """Show empty state."""
        data = [{
            "type": "pie",
            "labels": ["No Data"],
            "values": [1],
            "hole": 0.6,
            "marker": {"colors": ["#313244"]},
            "textinfo": "none",
            "hoverinfo": "none"
        }]
        layout = self._get_common_layout("No data available")
        layout["showlegend"] = False
        self.update_chart(data, layout)


class InteractiveBarChart(BaseInteractiveChart):
    """Interactive horizontal bar chart for folder sizes."""
    
    def __init__(self, parent=None):
        super().__init__(parent, height=400)
    
    def update_data(self, folders: List[Tuple[str, int, str]]):
        """Update chart with folder data."""
        if not folders:
            self._show_empty()
            return
        
        # Sort and limit to top 10
        folders = sorted(folders, key=lambda x: x[1], reverse=True)[:10]
        
        names = [f[0][:25] + "..." if len(f[0]) > 25 else f[0] for f in folders]
        sizes = [f[1] / (1024**2) for f in folders]  # Convert to MB
        size_labels = [f[2] for f in folders]
        
        # Generate gradient colors
        colors = []
        for i in range(len(names)):
            ratio = i / max(len(names) - 1, 1)
            # Gradient from blue to purple
            r = int(96 + (192 - 96) * ratio)
            g = int(165 + (132 - 165) * ratio)
            b = int(250 + (252 - 250) * ratio)
            colors.append(f"rgb({r}, {g}, {b})")
        
        data = [{
            "type": "bar",
            "x": sizes,
            "y": names,
            "orientation": "h",
            "marker": {
                "color": colors,
                "line": {"color": "#0d0d12", "width": 1},
                "cornerradius": 6
            },
            "text": size_labels,
            "textposition": "outside",
            "textfont": {"color": "#cdd6f4", "size": 11},
            "hovertemplate": "<b>%{y}</b><br>Size: %{text}<extra></extra>",
            "cliponaxis": False
        }]
        
        layout = self._get_common_layout("")
        layout["xaxis"] = {
            "showgrid": True,
            "gridcolor": "#252536",
            "zeroline": False,
            "showticklabels": False,
            "title": ""
        }
        layout["yaxis"] = {
            "showgrid": False,
            "zeroline": False,
            "tickfont": {"color": "#a6adc8", "size": 12},
            "autorange": "reversed"
        }
        layout["margin"] = {"t": 20, "b": 30, "l": 150, "r": 80}
        
        self.update_chart(data, layout)
    
    def _show_empty(self):
        data = [{
            "type": "bar",
            "x": [0],
            "y": ["No data"],
            "orientation": "h",
            "marker": {"color": "#313244"}
        }]
        layout = self._get_common_layout("No folders found")
        self.update_chart(data, layout)


class InteractiveTreemap(BaseInteractiveChart):
    """Interactive treemap for storage visualization."""
    
    def __init__(self, parent=None):
        super().__init__(parent, height=400)
    
    def update_data(self, categories: Dict[FileCategory, float]):
        """Update treemap with category data."""
        if not categories:
            self._show_empty()
            return
        
        labels = [cat.value for cat in categories.keys()]
        values = list(categories.values())
        parents = [""] * len(labels)
        colors = [CATEGORY_COLORS.get(cat.value, ("#94a3b8", "#64748b"))[0] 
                  for cat in categories.keys()]
        
        data = [{
            "type": "treemap",
            "labels": labels,
            "values": values,
            "parents": parents,
            "marker": {
                "colors": colors,
                "cornerradius": 8,
                "line": {"color": "#0d0d12", "width": 2}
            },
            "textfont": {"color": "#ffffff", "size": 14},
            "hovertemplate": "<b>%{label}</b><br>%{percentRoot:.1%}<br>%{value:.1f}%<extra></extra>",
            "texttemplate": "<b>%{label}</b><br>%{percentRoot:.0%}",
            "pathbar": {"visible": False}
        }]
        
        layout = self._get_common_layout("")
        layout["margin"] = {"t": 10, "b": 10, "l": 10, "r": 10}
        
        self.update_chart(data, layout)
    
    def _show_empty(self):
        data = [{
            "type": "treemap",
            "labels": ["No Data"],
            "values": [1],
            "parents": [""],
            "marker": {"color": "#313244"}
        }]
        layout = self._get_common_layout("No data available")
        self.update_chart(data, layout)


class InteractiveExtensionChart(BaseInteractiveChart):
    """Interactive bar chart for file extensions."""
    
    def __init__(self, parent=None):
        super().__init__(parent, height=350)
    
    def update_data(self, extensions: Dict[str, int]):
        """Update chart with extension data."""
        if not extensions:
            self._show_empty()
            return
        
        # Sort by count and take top 12
        sorted_exts = sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:12]
        exts = [ext for ext, count in sorted_exts]
        counts = [count for ext, count in sorted_exts]
        
        # Generate gradient colors
        colors = []
        for i in range(len(exts)):
            ratio = i / max(len(exts) - 1, 1)
            r = int(96 + (192 - 96) * (1 - ratio))
            g = int(165 + (132 - 165) * (1 - ratio))
            b = int(250 + (252 - 250) * (1 - ratio))
            colors.append(f"rgb({r}, {g}, {b})")
        
        data = [{
            "type": "bar",
            "x": exts,
            "y": counts,
            "marker": {
                "color": colors,
                "line": {"color": "#0d0d12", "width": 1},
                "cornerradius": 6
            },
            "text": [str(c) for c in counts],
            "textposition": "outside",
            "textfont": {"color": "#cdd6f4", "size": 11},
            "hovertemplate": "<b>%{x}</b><br>Files: %{y:,}<extra></extra>"
        }]
        
        layout = self._get_common_layout("")
        layout["xaxis"] = {
            "showgrid": False,
            "tickfont": {"color": "#a6adc8", "size": 11},
            "tickangle": -30
        }
        layout["yaxis"] = {
            "showgrid": True,
            "gridcolor": "#252536",
            "zeroline": False,
            "showticklabels": False
        }
        layout["margin"] = {"t": 20, "b": 60, "l": 40, "r": 30}
        
        self.update_chart(data, layout)
    
    def _show_empty(self):
        data = [{
            "type": "bar",
            "x": ["No Data"],
            "y": [0],
            "marker": {"color": "#313244"}
        }]
        layout = self._get_common_layout("No extension data")
        self.update_chart(data, layout)


class InteractiveSunburst(BaseInteractiveChart):
    """Interactive sunburst chart showing category -> extension hierarchy."""
    
    def __init__(self, parent=None):
        super().__init__(parent, height=400)
    
    def update_data(self, categories: Dict[FileCategory, Dict]):
        """Update sunburst with hierarchical data."""
        if not categories:
            self._show_empty()
            return
        
        ids = ["root"]
        labels = ["Storage"]
        parents = [""]
        values = [0]
        colors = ["#313244"]
        
        for cat, data in categories.items():
            cat_id = cat.value
            cat_value = sum(data.get('extensions', {}).values()) if isinstance(data, dict) else 0
            
            ids.append(cat_id)
            labels.append(cat.value)
            parents.append("root")
            values.append(max(cat_value, 1))
            colors.append(CATEGORY_COLORS.get(cat.value, ("#94a3b8", "#64748b"))[0])
            
            # Add extensions
            if isinstance(data, dict) and 'extensions' in data:
                for ext, count in list(data['extensions'].items())[:5]:
                    ext_id = f"{cat_id}_{ext}"
                    ids.append(ext_id)
                    labels.append(ext)
                    parents.append(cat_id)
                    values.append(count)
                    colors.append(CATEGORY_COLORS.get(cat.value, ("#94a3b8", "#64748b"))[1])
        
        data = [{
            "type": "sunburst",
            "ids": ids,
            "labels": labels,
            "parents": parents,
            "values": values,
            "branchvalues": "total",
            "marker": {
                "colors": colors,
                "line": {"color": "#0d0d12", "width": 1}
            },
            "textfont": {"color": "#ffffff", "size": 12},
            "hovertemplate": "<b>%{label}</b><br>Files: %{value:,}<extra></extra>"
        }]
        
        layout = self._get_common_layout("")
        layout["margin"] = {"t": 10, "b": 10, "l": 10, "r": 10}
        layout["sunburstcolorway"] = colors
        
        self.update_chart(data, layout)
    
    def _show_empty(self):
        data = [{
            "type": "sunburst",
            "ids": ["root"],
            "labels": ["No Data"],
            "parents": [""],
            "values": [1],
            "marker": {"colors": ["#313244"]}
        }]
        layout = self._get_common_layout("No data available")
        self.update_chart(data, layout)


class ChartContainer(QWidget):
    """Container for interactive charts with title and controls."""
    
    def __init__(self, title: str, chart: BaseInteractiveChart, parent=None):
        super().__init__(parent)
        self.setObjectName("glass-card")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Chart
        self.chart = chart
        layout.addWidget(chart, 1)
        
        self.setStyleSheet(f"""
            QWidget#glass-card {{
                background-color: rgba(37, 37, 54, 0.6);
                border: 1px solid rgba(137, 180, 250, 0.15);
                border-radius: 20px;
            }}
        """)


