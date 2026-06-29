"""
The Greek text editor widget.

Design note on accessibility: the prototype spoke every navigation key through
``accessible_output2`` while NVDA/JAWS were *also* echoing the same key — double
speech, which this user explicitly dislikes. This version does the opposite: it
stays silent on navigation and lets the screen reader read the real characters
under the caret natively. Greek pronunciation is provided only on explicit
commands (read word / line / selection) driven from the main window.

Latin→Greek conversion can be toggled off (Ctrl+G) so the same editor can hold
English notes or translations without mangling them into Greek.
"""

import unicodedata

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit

from core.greek_keyboard import translate_char, try_combine_diacritic

_DIACRITIC_KEYS = (")", "(", "/", "\\", "=", "|", "+")
_STANDARD_PUNCT = ".,;:?!\"'«»·"


class SmartTextEditor(QPlainTextEdit):
    word_selected = pyqtSignal(str)    # cursor landed on a word -> dictionary lookup
    word_completed = pyqtSignal(str)   # a word was finished -> optional auto-speak

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self._original_text = ""
        self.greek_mode = True
        self.auto_speak = False
        self.last_looked_up = ""

        self.setAccessibleName("Ancient Greek text editor")
        self.setAccessibleDescription(
            "Type Latin letters to produce polytonic Greek. "
            "Press F1 for the typing guide, or Control+G to toggle Greek input."
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.cursorPositionChanged.connect(self._on_cursor_moved)

    # ----- configuration ----------------------------------------------
    def set_greek_mode(self, on):
        self.greek_mode = on

    def set_auto_speak(self, on):
        self.auto_speak = on

    def set_font_size(self, point_size):
        font = self.font()
        font.setPointSize(max(8, int(point_size)))
        self.setFont(font)

    # ----- reading helpers (used by main window commands) -------------
    def current_word(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            return cursor.selectedText()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        return cursor.selectedText()

    def current_line(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        return cursor.selectedText()

    def current_char(self):
        cursor = self.textCursor()
        cursor.movePosition(
            QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor
        )
        return cursor.selectedText()

    def selected_text(self):
        return self.textCursor().selectedText()

    # ----- dictionary trigger -----------------------------------------
    def _on_cursor_moved(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        if word and word != self.last_looked_up:
            self.last_looked_up = word
            self.word_selected.emit(word)

    # ----- input ------------------------------------------------------
    def keyPressEvent(self, event):
        # When Greek input is off, behave like a normal text box.
        if not self.greek_mode:
            super().keyPressEvent(event)
            return

        text = event.text()
        key = event.key()

        # Let the screen reader handle navigation/editing natively (no echo here).
        if not text or key in (
            Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Tab,
            Qt.Key.Key_Backspace, Qt.Key.Key_Delete,
            Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down,
            Qt.Key.Key_Home, Qt.Key.Key_End, Qt.Key.Key_PageUp, Qt.Key.Key_PageDown,
        ):
            super().keyPressEvent(event)
            return

        # Diacritic modifier typed right after a base letter.
        if text in _DIACRITIC_KEYS:
            cursor = self.textCursor()
            cursor.movePosition(
                QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor
            )
            prev_char = cursor.selectedText()
            if prev_char:
                combined = try_combine_diacritic(prev_char, text)
                if combined and combined != prev_char:
                    cursor.insertText(combined)
                    return
            # Fall through: not combinable, treat ')' '(' etc. as literal punctuation.
            super().keyPressEvent(event)
            return

        # Word boundary: auto-convert trailing σ -> final ς, then maybe speak.
        if text.isspace() or text in _STANDARD_PUNCT:
            self._finalize_word_sigma()
            if self.auto_speak:
                word = self.current_word().strip()
                if word:
                    self.word_completed.emit(word)
            super().keyPressEvent(event)
            return

        # Special single keys.
        greek = translate_char(text)
        if greek != text:
            self.textCursor().insertText(greek)
            return

        super().keyPressEvent(event)

    def _finalize_word_sigma(self):
        cursor = self.textCursor()
        cursor.movePosition(
            QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor
        )
        prev = cursor.selectedText()
        if prev and "σ" in unicodedata.normalize("NFD", prev):
            cursor.insertText(prev.replace("σ", "ς"))
