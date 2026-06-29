"""
Import Greek texts from PDF / EPUB / plain-text documents on a worker thread.

PyMuPDF (``fitz``) handles both PDF and EPUB, so no extra EPUB library is
required. Extraction runs off the GUI thread; cancellation is cooperative (a
flag checked between pages) rather than a hard ``terminate()``, which could
corrupt the interpreter state.
"""

import os

from PyQt6.QtCore import QThread, pyqtSignal

from core.logger import get_logger

log = get_logger(__name__)

SUPPORTED_EXTENSIONS = (".pdf", ".epub", ".txt", ".md", ".xhtml", ".htm", ".html", ".fb2", ".xps")


class DocumentImporterWorker(QThread):
    progress_update = pyqtSignal(int, int)   # current, total
    text_extracted = pyqtSignal(str)
    finished_import = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            ext = os.path.splitext(self.filepath)[1].lower()
            if ext in (".txt", ".md"):
                self._extract_plain_text()
            else:
                self._extract_with_fitz()
        except Exception as e:  # pragma: no cover
            log.error("Import failed for %s: %s", self.filepath, e)
            self.error_occurred.emit(str(e))
        finally:
            self.finished_import.emit()

    def _extract_plain_text(self):
        with open(self.filepath, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        self.progress_update.emit(1, 1)
        if not self._cancelled:
            self.text_extracted.emit(text)

    def _extract_with_fitz(self):
        import fitz  # PyMuPDF

        doc = fitz.open(self.filepath)
        try:
            total = len(doc)
            parts = []
            for i in range(total):
                if self._cancelled:
                    return
                parts.append(doc.load_page(i).get_text())
                self.progress_update.emit(i + 1, total)
        finally:
            doc.close()

        if self._cancelled:
            return
        # Join pages with a clearly-spoken break marker.
        full_text = "\n\n".join(p.strip() for p in parts if p.strip())
        self.text_extracted.emit(full_text)
