"""Accessible dialogs: preferences, annotations, paradigms and history."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QPlainTextEdit, QPushButton, QSpinBox,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

from core import pronunciation


class SettingsDialog(QDialog):
    """Preferences. ``result_settings`` holds the new values after accept()."""

    def __init__(self, parent, settings, strings, lang):
        super().__init__(parent)
        self.strings = strings
        self.result_settings = dict(settings)
        self.setWindowTitle(strings["settings_title"])
        self.setModal(True)
        self.setAccessibleName(strings["settings_title"])
        self.resize(480, 360)

        form = QFormLayout(self)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Español", "es")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setCurrentIndex(0 if settings.get("language") == "es" else 1)
        self.lang_combo.setAccessibleName(strings["settings_language"])
        form.addRow(strings["settings_language"], self.lang_combo)

        self.scheme_combo = QComboBox()
        labels = pronunciation.SCHEME_LABELS.get(lang, pronunciation.SCHEME_LABELS["en"])
        for s in pronunciation.SCHEMES:
            self.scheme_combo.addItem(labels[s], s)
        idx = pronunciation.SCHEMES.index(
            settings.get("pronunciation_scheme", pronunciation.DEFAULT_SCHEME)
        ) if settings.get("pronunciation_scheme") in pronunciation.SCHEMES else 0
        self.scheme_combo.setCurrentIndex(idx)
        self.scheme_combo.setAccessibleName(strings["settings_scheme"])
        form.addRow(strings["settings_scheme"], self.scheme_combo)

        self.rate_spin = QSpinBox()
        self.rate_spin.setRange(0, 100)
        self.rate_spin.setSpecialValueText("—")  # 0 shows as "—" = use SR default
        self.rate_spin.setValue(settings.get("speech_rate") or 0)
        self.rate_spin.setAccessibleName(strings["settings_rate"])
        form.addRow(strings["settings_rate"], self.rate_spin)

        self.autospeak_check = QCheckBox(strings["settings_autospeak"])
        self.autospeak_check.setChecked(bool(settings.get("auto_speak_words")))
        form.addRow(self.autospeak_check)

        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 48)
        self.font_spin.setValue(int(settings.get("font_point_size", 14)))
        self.font_spin.setAccessibleName(strings["settings_font"])
        form.addRow(strings["settings_font"], self.font_spin)

        self.showdict_check = QCheckBox(strings["settings_show_dict"])
        self.showdict_check.setChecked(bool(settings.get("show_dictionary_panel", True)))
        form.addRow(self.showdict_check)

        self.exam_check = QCheckBox(strings["settings_exam"])
        self.exam_check.setChecked(bool(settings.get("exam_mode")))
        form.addRow(self.exam_check)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(strings["ok"])
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(strings["cancel"])
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _on_accept(self):
        self.result_settings["language"] = self.lang_combo.currentData()
        self.result_settings["pronunciation_scheme"] = self.scheme_combo.currentData()
        self.result_settings["speech_rate"] = self.rate_spin.value() or None
        self.result_settings["auto_speak_words"] = self.autospeak_check.isChecked()
        self.result_settings["font_point_size"] = self.font_spin.value()
        self.result_settings["show_dictionary_panel"] = self.showdict_check.isChecked()
        self.result_settings["exam_mode"] = self.exam_check.isChecked()
        self.accept()


class AnnotationDialog(QDialog):
    """Enter the text of a note."""

    def __init__(self, parent, strings, existing=""):
        super().__init__(parent)
        self.strings = strings
        self.setWindowTitle(strings["note_title"])
        self.setModal(True)
        self.setAccessibleName(strings["note_title"])
        self.resize(460, 240)

        layout = QVBoxLayout(self)
        label = QLabel(strings["note_prompt"])
        layout.addWidget(label)
        self.edit = QPlainTextEdit()
        self.edit.setPlainText(existing)
        self.edit.setAccessibleName(strings["note_prompt"])
        label.setBuddy(self.edit)
        layout.addWidget(self.edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(strings["save_btn"])
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(strings["cancel"])
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.edit.setFocus()

    def note_text(self):
        return self.edit.toPlainText().strip()


class NotesDialog(QDialog):
    """List existing notes for a file with delete / jump."""

    def __init__(self, parent, strings, notes):
        super().__init__(parent)
        self.strings = strings
        self.notes = notes
        self.selected_id = None
        self.jump_to = None
        self.setWindowTitle(strings["notes_title"])
        self.setModal(True)
        self.setAccessibleName(strings["notes_title"])
        self.resize(520, 400)

        layout = QVBoxLayout(self)
        self.list = QListWidget()
        self.list.setAccessibleName(strings["notes_title"])
        if not notes:
            self.list.addItem(strings["notes_empty"])
            self.list.setEnabled(False)
        else:
            for n in notes:
                anchor = (n.get("anchor_text") or "").strip().replace(" ", " ")
                if len(anchor) > 40:
                    anchor = anchor[:40] + "…"
                item = QListWidgetItem(strings["note_at"].format(n["note"]) +
                                       (f"  ({anchor})" if anchor else ""))
                item.setData(Qt.ItemDataRole.UserRole, n)
                self.list.addItem(item)
        layout.addWidget(self.list)

        row = QHBoxLayout()
        self.jump_btn = QPushButton(strings["note_jump"])
        self.del_btn = QPushButton(strings["delete"])
        self.close_btn = QPushButton(strings["close"])
        self.jump_btn.clicked.connect(self._jump)
        self.del_btn.clicked.connect(self._delete)
        self.close_btn.clicked.connect(self.reject)
        row.addWidget(self.jump_btn)
        row.addWidget(self.del_btn)
        row.addWidget(self.close_btn)
        layout.addLayout(row)
        if notes:
            self.list.setCurrentRow(0)
            self.list.setFocus()
        else:
            self.close_btn.setFocus()

    def _current_note(self):
        item = self.list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _jump(self):
        n = self._current_note()
        if n:
            self.jump_to = n
            self.accept()

    def _delete(self):
        n = self._current_note()
        if n:
            self.selected_id = n["id"]
            self.accept()


class ParadigmDialog(QDialog):
    """Show a declension/conjugation table as a navigable tree."""

    def __init__(self, parent, strings, paradigm, lang):
        super().__init__(parent)
        self.setWindowTitle(strings["paradigm_title"])
        self.setModal(True)
        title = paradigm["title"][lang]
        self.setAccessibleName(title)
        self.resize(480, 520)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(title))
        note = paradigm.get("note", {}).get(lang, "")
        if note:
            layout.addWidget(QLabel(note))

        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        tree.setAccessibleName(title)
        for group in paradigm["groups"]:
            parent_item = QTreeWidgetItem([group["label"][lang]])
            tree.addTopLevelItem(parent_item)
            for r in group["rows"]:
                child = QTreeWidgetItem([f"{r['label'][lang]}: {r['form']}"])
                parent_item.addChild(child)
            parent_item.setExpanded(True)
        layout.addWidget(tree)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.button(QDialogButtonBox.StandardButton.Close).setText(strings["close"])
        buttons.rejected.connect(self.accept)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        tree.setFocus()
        if tree.topLevelItemCount():
            tree.setCurrentItem(tree.topLevelItem(0))


class HistoryDialog(QDialog):
    def __init__(self, parent, strings, history):
        super().__init__(parent)
        self.strings = strings
        self.cleared = False
        self.setWindowTitle(strings["history_title"])
        self.setModal(True)
        self.setAccessibleName(strings["history_title"])
        self.resize(520, 420)

        layout = QVBoxLayout(self)
        self.list = QListWidget()
        self.list.setAccessibleName(strings["history_title"])
        if not history:
            self.list.addItem(strings["history_empty"])
            self.list.setEnabled(False)
        else:
            for h in history:
                defn = (h.get("definition") or "").split(" ")[0]
                self.list.addItem(f"{h['lemma']} — {defn}" if defn else h["lemma"])
        layout.addWidget(self.list)

        row = QHBoxLayout()
        self.clear_btn = QPushButton(strings["history_clear"])
        self.close_btn = QPushButton(strings["close"])
        self.clear_btn.clicked.connect(self._clear)
        self.close_btn.clicked.connect(self.reject)
        row.addWidget(self.clear_btn)
        row.addWidget(self.close_btn)
        layout.addLayout(row)
        (self.list if history else self.close_btn).setFocus()

    def _clear(self):
        self.cleared = True
        self.accept()
