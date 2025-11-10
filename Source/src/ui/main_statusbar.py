from PyQt6.QtWidgets import QStatusBar, QLabel


def setup_status_bar(window):
    """Attach a QStatusBar and standard labels to the given MainWindow instance."""
    window.status_bar = QStatusBar()
    window.setStatusBar(window.status_bar)

    # Add permanent widgets
    window.line_col_label = QLabel("Line: 1, Col: 1")
    window.encoding_label = QLabel("UTF-8")
    window.syntax_label = QLabel("Plain Text")

    window.status_bar.addPermanentWidget(window.line_col_label)
    window.status_bar.addPermanentWidget(window.encoding_label)
    window.status_bar.addPermanentWidget(window.syntax_label)
