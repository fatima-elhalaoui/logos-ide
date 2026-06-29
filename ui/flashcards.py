"""Flashcard review (Leitner spaced repetition) and management dialogs."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QListWidget, QPlainTextEdit,
    QPushButton, QVBoxLayout,
)


class FlashcardReviewDialog(QDialog):
    """Step through due cards; grading updates each card's schedule."""

    def __init__(self, parent, strings, store, cards, speak=None):
        super().__init__(parent)
        self.strings = strings
        self.store = store
        self.cards = cards
        self.speak = speak or (lambda t: None)
        self.index = 0
        self.reviewed = 0
        self.showing_answer = False

        self.setWindowTitle(strings["flash_review_title"])
        self.setModal(True)
        self.setAccessibleName(strings["flash_review_title"])
        self.resize(520, 360)

        layout = QVBoxLayout(self)
        self.progress = QLabel()
        layout.addWidget(self.progress)

        self.prompt = QPlainTextEdit()
        self.prompt.setReadOnly(True)
        self.prompt.setAccessibleName(strings["flash_review_title"])
        layout.addWidget(self.prompt)

        row = QHBoxLayout()
        self.show_btn = QPushButton(strings["flash_show_answer"])
        self.correct_btn = QPushButton(strings["flash_correct"])
        self.wrong_btn = QPushButton(strings["flash_wrong"])
        self.close_btn = QPushButton(strings["close"])
        self.show_btn.clicked.connect(self._show_answer)
        self.correct_btn.clicked.connect(lambda: self._grade(True))
        self.wrong_btn.clicked.connect(lambda: self._grade(False))
        self.close_btn.clicked.connect(self.reject)
        for b in (self.show_btn, self.correct_btn, self.wrong_btn, self.close_btn):
            row.addWidget(b)
        layout.addLayout(row)

        self._render()

    def _current(self):
        return self.cards[self.index]

    def _render(self):
        if self.index >= len(self.cards):
            self._finish()
            return
        card = self._current()
        self.progress.setText(
            self.strings["flash_progress"].format(self.index + 1, len(self.cards))
        )
        self.showing_answer = False
        front = self.strings["flash_front"].format(card["front"])
        self.prompt.setPlainText(front)
        self.show_btn.setEnabled(True)
        self.correct_btn.setEnabled(False)
        self.wrong_btn.setEnabled(False)
        self.show_btn.setFocus()

    def _show_answer(self):
        card = self._current()
        back = card["back"]
        if card.get("morphology"):
            back = f"{back}  [{card['morphology']}]"
        text = (self.strings["flash_front"].format(card["front"]) + "\n" +
                self.strings["flash_answer"].format(back))
        self.prompt.setPlainText(text)
        self.showing_answer = True
        self.show_btn.setEnabled(False)
        self.correct_btn.setEnabled(True)
        self.wrong_btn.setEnabled(True)
        self.prompt.setFocus()  # screen reader reads the revealed answer

    def _grade(self, correct):
        card = self._current()
        self.store.review_flashcard(card["id"], correct)
        self.reviewed += 1
        self.index += 1
        self._render()

    def _finish(self):
        self.prompt.setPlainText(self.strings["flash_done"].format(self.reviewed))
        self.progress.setText("")
        self.show_btn.setEnabled(False)
        self.correct_btn.setEnabled(False)
        self.wrong_btn.setEnabled(False)
        self.close_btn.setFocus()


class ManageFlashcardsDialog(QDialog):
    def __init__(self, parent, strings, store):
        super().__init__(parent)
        self.strings = strings
        self.store = store
        self.setWindowTitle(strings["flash_manage_title"])
        self.setModal(True)
        self.setAccessibleName(strings["flash_manage_title"])
        self.resize(560, 440)

        layout = QVBoxLayout(self)
        self.list = QListWidget()
        self.list.setAccessibleName(strings["flash_manage_title"])
        layout.addWidget(self.list)
        self._reload()

        row = QHBoxLayout()
        self.del_btn = QPushButton(strings["delete"])
        self.close_btn = QPushButton(strings["close"])
        self.del_btn.clicked.connect(self._delete)
        self.close_btn.clicked.connect(self.accept)
        row.addWidget(self.del_btn)
        row.addWidget(self.close_btn)
        layout.addLayout(row)
        (self.list if self.list.count() else self.close_btn).setFocus()

    def _reload(self):
        self.list.clear()
        self.cards = self.store.get_flashcards()
        if not self.cards:
            self.list.addItem(self.strings["flash_none"])
            self.list.setEnabled(False)
            return
        self.list.setEnabled(True)
        for c in self.cards:
            self.list.addItem(self.strings["flash_word"].format(c["front"], c["back"]))
        self.list.setCurrentRow(0)

    def _delete(self):
        if not self.list.isEnabled():
            return
        idx = self.list.currentRow()
        if 0 <= idx < len(self.cards):
            self.store.delete_flashcard(self.cards[idx]["id"])
            self._reload()
