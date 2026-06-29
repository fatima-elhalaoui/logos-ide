"""
Logos IDE — main application window.

An accessible Ancient & Koine Greek study environment for blind and low-vision
students, fully usable with NVDA and JAWS.
"""

import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QActionGroup, QKeySequence, QShortcut, QTextCursor
from PyQt6.QtWidgets import (
    QApplication, QDockWidget, QFileDialog, QInputDialog, QMainWindow,
    QMessageBox, QProgressDialog, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget,
)

from core import pronunciation
from core.audio import TTSAudioWorker
from core.greek_keyboard import describe_char
from core.importer import DocumentImporterWorker, SUPPORTED_EXTENSIONS
from core.logger import get_logger
from core.paradigms import generate_paradigm
from core.settings import load_settings, save_settings
from core.i18n import get_strings
from core.data_paths import using_seed_database
from db.lookup import DictionaryLookupWorker, quick_lookup
from db.study import StudyStore
from ui.dialogs import (
    AnnotationDialog, HistoryDialog, NotesDialog, ParadigmDialog, SettingsDialog,
)
from ui.editor import SmartTextEditor
from ui.flashcards import FlashcardReviewDialog, ManageFlashcardsDialog
from ui.help_dialog import AboutDialog, KeyboardGuideDialog

log = get_logger(__name__)
VERSION = "1.0.0"


class LogosMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.lang = self.settings.get("language", "es")
        self.s = get_strings(self.lang)
        self.exam_mode = bool(self.settings.get("exam_mode"))
        self.store = StudyStore()
        self._last_results = []
        self._last_search = ""

        self.setWindowTitle(self.s["window_title"])
        self.resize(1024, 768)
        self.setAccessibleName(self.s["window_title"])

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(lambda _: self._update_title())
        layout.addWidget(self.tabs)

        self._build_dictionary_panel()
        self._build_menus()
        self._build_shortcuts()
        self.statusBar().setAccessibleName("Status")

        # Background workers.
        self.dict_worker = DictionaryLookupWorker(language=self.lang)
        self.dict_worker.lookup_completed.connect(self._on_lookup_completed)
        self.dict_worker.status_changed.connect(self._on_dict_status)
        self.dict_worker.start()

        self.audio_worker = TTSAudioWorker(
            language=self.lang,
            scheme=self.settings.get("pronunciation_scheme", pronunciation.DEFAULT_SCHEME),
            rate=self.settings.get("speech_rate"),
        )
        self.audio_worker.start()

        self.importer_worker = None
        self.progress_dialog = None

        self._create_new_tab()
        self._apply_exam_mode(initial=True)

        if using_seed_database():
            self.statusBar().showMessage(self.s["seed_db_notice"], 10000)

    # ==================================================================
    # UI construction
    # ==================================================================
    def _build_dictionary_panel(self):
        self.dict_dock = QDockWidget(self.s["dict_title"], self)
        self.dict_dock.setAccessibleName(self.s["dict_title"])
        self.dict_tree = QTreeWidget()
        self.dict_tree.setHeaderHidden(True)
        self.dict_tree.setAccessibleName(self.s["dict_title"])
        self._set_dict_hint()
        self.dict_dock.setWidget(self.dict_tree)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dict_dock)
        if not self.settings.get("show_dictionary_panel", True):
            self.dict_dock.hide()

    def _set_dict_hint(self):
        self.dict_tree.clear()
        item = QTreeWidgetItem([self.s["dict_hint"]])
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.dict_tree.addTopLevelItem(item)

    def _build_menus(self):
        mb = self.menuBar()
        mb.setAccessibleName("Main menu")
        s = self.s

        # --- File ---
        self.m_file = mb.addMenu(s["file_menu"])
        self.a_new = self._act(self.m_file, s["new"], "Ctrl+N", self.file_new)
        self.a_open = self._act(self.m_file, s["open"], "Ctrl+O", self.file_open)
        self.a_save = self._act(self.m_file, s["save"], "Ctrl+S", self.file_save)
        self.a_save_as = self._act(self.m_file, s["save_as"], "Ctrl+Shift+S", self.file_save_as)
        self.m_file.addSeparator()
        self.a_import = self._act(self.m_file, s["import"], "Ctrl+I", self.import_document)
        self.m_file.addSeparator()
        self.a_close_tab = self._act(self.m_file, s["close_tab"], "Ctrl+W", lambda: self.close_tab(self.tabs.currentIndex()))
        self.a_exit = self._act(self.m_file, s["exit"], "Ctrl+Q", self.close)

        # --- Edit ---
        self.m_edit = mb.addMenu(s["edit_menu"])
        self.a_find = self._act(self.m_edit, s["find"], "Ctrl+F", self.find_text)
        self.a_find_next = self._act(self.m_edit, s["find_next"], "F3", self.find_next)
        self.a_goto = self._act(self.m_edit, s["goto_line"], "Ctrl+L", self.goto_line)
        self.a_select_all = self._act(self.m_edit, s["select_all"], "Ctrl+A", self._select_all)

        # --- View ---
        self.m_view = mb.addMenu(s["view_menu"])
        self.a_font_inc = self._act(self.m_view, s["increase_font"], "Ctrl+=", lambda: self._change_font(1))
        self.a_font_dec = self._act(self.m_view, s["decrease_font"], "Ctrl+-", lambda: self._change_font(-1))
        self.a_toggle_dict = self._act(self.m_view, s["toggle_dict"], "F4", self._toggle_dict_panel)
        self.a_focus_editor = self._act(self.m_view, s["focus_editor"], "F5", self.focus_editor)
        self.a_focus_dict = self._act(self.m_view, s["focus_dict"], "F6", self.focus_dictionary)

        # --- Greek ---
        self.m_greek = mb.addMenu(s["greek_menu"])
        self.a_greek_mode = self._act(self.m_greek, s["greek_input"], "Ctrl+G", self._toggle_greek_mode, checkable=True)
        self.a_greek_mode.setChecked(True)
        self.a_describe = self._act(self.m_greek, s["describe_char"], "Ctrl+;", self.describe_current_char)
        self.a_read_word = self._act(self.m_greek, s["read_word"], "Ctrl+Shift+W", self.read_current_word)
        self.a_read_line = self._act(self.m_greek, s["read_line"], "Ctrl+Shift+L", self.read_current_line)
        self.a_read_doc = self._act(self.m_greek, s["read_document"], "Ctrl+Shift+D", self.read_document)
        self.a_paradigm = self._act(self.m_greek, s["show_paradigm"], "Ctrl+Shift+P", self.show_paradigm)
        self.m_greek.addSeparator()
        self.a_guide = self._act(self.m_greek, s["keyboard_guide"], "F1", self.show_keyboard_guide)

        # --- Audio ---
        self.m_audio = mb.addMenu(s["audio_menu"])
        self.a_read_sel = self._act(self.m_audio, s["read"], "Ctrl+R", self.read_selection)
        self.a_read_entry = self._act(self.m_audio, s["read_entry"], "F8", self.read_dict_entry)
        self.a_stop = self._act(self.m_audio, s["stop_speech"], "Ctrl+Space", self.stop_speech)
        self.m_pron = self.m_audio.addMenu(s["pron_scheme"])
        self.scheme_group = QActionGroup(self)
        self.scheme_actions = {}
        labels = pronunciation.SCHEME_LABELS.get(self.lang, pronunciation.SCHEME_LABELS["en"])
        for scheme in pronunciation.SCHEMES:
            a = self.m_pron.addAction(labels[scheme])
            a.setCheckable(True)
            a.setChecked(scheme == self.settings.get("pronunciation_scheme"))
            a.triggered.connect(lambda _checked, sc=scheme: self.change_scheme(sc))
            self.scheme_group.addAction(a)
            self.scheme_actions[scheme] = a
        self.a_auto_speak = self._act(self.m_audio, s["auto_speak"], None, self._toggle_auto_speak, checkable=True)
        self.a_auto_speak.setChecked(bool(self.settings.get("auto_speak_words")))

        # --- Study ---
        self.m_study = mb.addMenu(s["study_menu"])
        self.a_add_note = self._act(self.m_study, s["add_note"], "Ctrl+Shift+N", self.add_note)
        self.a_view_notes = self._act(self.m_study, s["view_notes"], None, self.view_notes)
        self.m_study.addSeparator()
        self.a_add_card = self._act(self.m_study, s["add_flashcard"], "Ctrl+D", self.add_flashcard)
        self.a_review = self._act(self.m_study, s["review_flashcards"], "Ctrl+Shift+R", self.review_flashcards)
        self.a_manage = self._act(self.m_study, s["manage_flashcards"], None, self.manage_flashcards)
        self.a_export_csv = self._act(self.m_study, s["export_flashcards"], None, lambda: self.export_flashcards(False))
        self.a_export_anki = self._act(self.m_study, s["export_anki"], None, lambda: self.export_flashcards(True))
        self.m_study.addSeparator()
        self.a_history = self._act(self.m_study, s["history"], None, self.show_history)

        # --- Settings ---
        self.m_settings = mb.addMenu(s["settings_menu"])
        self.a_prefs = self._act(self.m_settings, s["open_settings"], "Ctrl+,", self.open_settings)
        self.m_lang = self.m_settings.addMenu(s["language"])
        self.lang_group = QActionGroup(self)
        self.a_lang_es = self.m_lang.addAction("Español")
        self.a_lang_en = self.m_lang.addAction("English")
        for a, code in ((self.a_lang_es, "es"), (self.a_lang_en, "en")):
            a.setCheckable(True)
            a.setChecked(self.lang == code)
            a.triggered.connect(lambda _c, lc=code: self.change_language(lc))
            self.lang_group.addAction(a)
        self.a_exam = self._act(self.m_settings, s["exam_mode"], "Ctrl+Shift+E", self.toggle_exam_mode, checkable=True)
        self.a_exam.setChecked(self.exam_mode)

        # --- Help ---
        self.m_help = mb.addMenu(s["help_menu"])
        self.a_help_guide = self._act(self.m_help, s["guide"], None, self.show_keyboard_guide)
        self.a_user_guide = self._act(self.m_help, s["user_guide"], None, self.open_user_guide)
        self.a_about = self._act(self.m_help, s["about"], None, self.show_about)

    def _act(self, menu, text, shortcut, slot, checkable=False):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.setCheckable(checkable)
        if checkable:
            action.toggled.connect(slot)
        else:
            action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _build_shortcuts(self):
        # Tab navigation (do NOT bind Esc globally — it would break dialogs/menus).
        QShortcut(QKeySequence("Ctrl+Tab"), self, activated=self._next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, activated=self._prev_tab)

    # ==================================================================
    # Tabs / editors
    # ==================================================================
    def current_editor(self):
        return self.tabs.currentWidget()

    def _create_new_tab(self, filepath=None, content=""):
        editor = SmartTextEditor()
        editor.file_path = filepath
        editor.setPlainText(content)
        editor.set_greek_mode(True)
        editor.set_auto_speak(bool(self.settings.get("auto_speak_words")))
        editor.set_font_size(self.settings.get("font_point_size", 14))
        editor.setPlaceholderText(self.s["editor_hint"])
        editor.word_selected.connect(self._on_word_selected)
        editor.word_completed.connect(self._on_word_completed)
        editor.document().setModified(False)
        editor._original_text = editor.toPlainText()

        title = self.s["untitled"] if not filepath else os.path.basename(filepath)
        index = self.tabs.addTab(editor, title)
        self.tabs.setCurrentIndex(index)
        editor.setFocus()
        self._update_title()
        return editor

    def _update_title(self):
        editor = self.current_editor()
        base = self.s["window_title"]
        if editor:
            name = self.s["untitled"] if not editor.file_path else os.path.basename(editor.file_path)
            mark = "*" if (editor.document().isModified() and editor.toPlainText() != getattr(editor, "_original_text", "")) else ""
            self.setWindowTitle(f"{base} — [{name}{mark}]")
        else:
            self.setWindowTitle(base)

    def _next_tab(self):
        n = self.tabs.count()
        if n > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() + 1) % n)

    def _prev_tab(self):
        n = self.tabs.count()
        if n > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() - 1) % n)

    def close_tab(self, index):
        editor = self.tabs.widget(index)
        if not editor:
            return
        if self._maybe_save(editor, index):
            self.tabs.removeTab(index)
            editor.deleteLater()
            if self.tabs.count() == 0:
                self._create_new_tab()

    def _maybe_save(self, editor, index):
        """Return True if it is OK to proceed (saved or discarded), False to cancel."""
        changed = editor.document().isModified() and editor.toPlainText() != getattr(editor, "_original_text", "")
        if not changed:
            return True
        self.tabs.setCurrentIndex(index)
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Question)
        box.setWindowTitle(self.s["unsaved_title"])
        box.setText(self.s["unsaved_msg"])
        save = box.addButton(self.s["save_choice"], QMessageBox.ButtonRole.AcceptRole)
        box.addButton(self.s["discard_choice"], QMessageBox.ButtonRole.DestructiveRole)
        cancel = box.addButton(self.s["cancel"], QMessageBox.ButtonRole.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked == cancel:
            return False
        if clicked == save:
            return self.file_save()
        return True

    # ==================================================================
    # File operations
    # ==================================================================
    def file_new(self):
        self._create_new_tab()

    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.s["open"], "", "Text/Greek (*.txt *.md);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self._create_new_tab(path, content)
        except Exception as e:
            QMessageBox.critical(self, self.s["open_error"].split(":")[0], self.s["open_error"].format(e))

    def file_save(self):
        editor = self.current_editor()
        if not editor:
            return False
        if not editor.file_path:
            return self.file_save_as()
        return self._write(editor, editor.file_path)

    def file_save_as(self):
        editor = self.current_editor()
        if not editor:
            return False
        path, _ = QFileDialog.getSaveFileName(
            self, self.s["save_as"], "", "Text (*.txt);;Markdown (*.md);;All Files (*)"
        )
        if not path:
            return False
        return self._write(editor, path)

    def _write(self, editor, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            editor.file_path = path
            editor.document().setModified(False)
            editor._original_text = editor.toPlainText()
            idx = self.tabs.indexOf(editor)
            if idx != -1:
                self.tabs.setTabText(idx, os.path.basename(path))
            self._update_title()
            self._announce(self.s["saved"])
            return True
        except Exception as e:
            QMessageBox.critical(self, self.s["save_error"].split(":")[0], self.s["save_error"].format(e))
            return False

    def import_document(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.s["import"], "",
            "Documents (*.pdf *.epub *.txt *.md);;All Files (*)",
        )
        if not path:
            return
        self.progress_dialog = QProgressDialog(
            self.s["import_progress"], self.s["cancel"], 0, 100, self
        )
        self.progress_dialog.setWindowTitle(self.s["import_title"])
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAccessibleName(self.s["import_title"])

        self.importer_worker = DocumentImporterWorker(path)
        self.importer_worker.progress_update.connect(self._on_import_progress)
        self.importer_worker.text_extracted.connect(self._on_text_extracted)
        self.importer_worker.error_occurred.connect(self._on_import_error)
        self.importer_worker.finished_import.connect(self._on_import_finished)
        self.progress_dialog.canceled.connect(self.importer_worker.cancel)  # cooperative!
        self.importer_worker.start()
        self.progress_dialog.show()

    def _on_import_progress(self, current, total):
        if self.progress_dialog:
            self.progress_dialog.setMaximum(total)
            self.progress_dialog.setValue(current)

    def _on_text_extracted(self, text):
        self._create_new_tab(None, text)

    def _on_import_error(self, msg):
        QMessageBox.critical(self, self.s["import_error"].split(":")[0], self.s["import_error"].format(msg))

    def _on_import_finished(self):
        if self.progress_dialog:
            self.progress_dialog.reset()
            self.progress_dialog = None

    # ==================================================================
    # Dictionary
    # ==================================================================
    def _on_word_selected(self, word):
        if self.exam_mode:
            return
        self.dict_worker.search_word(word)

    def _on_word_completed(self, word):
        # Only fires when auto-speak is enabled (editor gates it).
        self.audio_worker.speak_greek(word)

    def _on_dict_status(self, status):
        if status == "preparing":
            self.statusBar().showMessage(self.s["dict_preparing"])
        elif status == "ready":
            self.statusBar().showMessage(self.s["dict_ready"], 3000)

    def _on_lookup_completed(self, json_text):
        import json
        try:
            results = json.loads(json_text)
        except json.JSONDecodeError:
            return
        self.dict_tree.clear()
        if not results:
            self._set_dict_hint()
            self._last_results = []
            return
        first = results[0]
        if "error" in first:
            self.dict_tree.addTopLevelItem(QTreeWidgetItem([first["error"]]))
            self._last_results = []
            return
        if "not_found" in first:
            self.dict_tree.addTopLevelItem(
                QTreeWidgetItem([self.s["not_found"].format(first["not_found"])])
            )
            self._last_results = []
            return

        self._last_results = results
        count = len(results)
        for i, entry in enumerate(results):
            lemma = entry.get("lemma", "")
            morph = entry.get("morphology", "") or entry.get("raw_morph", "")
            morph_str = f"  [{morph}]" if morph else ""
            if count > 1:
                header = self.s["result_of"].format(i + 1, count, lemma) + morph_str
            else:
                header = self.s["lemma"].format(lemma) + morph_str
            parent = QTreeWidgetItem([header])
            self.dict_tree.addTopLevelItem(parent)
            definition = entry.get("definition", "")
            child = QTreeWidgetItem([self.s["definition"].format(definition)])
            parent.addChild(child)
        root = self.dict_tree.invisibleRootItem()
        if root.childCount():
            self.dict_tree.setCurrentItem(root.child(0))

    def read_dict_entry(self):
        if self.exam_mode:
            self._announce(self.s["exam_blocked"])
            return
        if not self._last_results:
            self._announce(self.s["not_found"].format(self.current_editor().current_word() if self.current_editor() else ""))
            return
        entry = self._last_results[0]
        lemma = entry.get("lemma", "")
        phon = pronunciation.transliterate(lemma, self.audio_worker.scheme, self.lang)
        morph = entry.get("morphology", "")
        definition = entry.get("definition", "")
        parts = [phon]
        if morph:
            parts.append(morph)
        if definition:
            parts.append(definition)
        self.audio_worker.speak_text(". ".join(parts), interrupt=True)
        self.store.add_history(lemma, definition)

    # ==================================================================
    # Reading commands
    # ==================================================================
    def read_selection(self):
        editor = self.current_editor()
        if not editor:
            return
        text = editor.selected_text()
        if not text:
            self._announce(self.s["nothing_selected"])
            return
        self.audio_worker.speak_greek(text)

    def read_current_word(self):
        editor = self.current_editor()
        if editor:
            w = editor.current_word()
            if w:
                self.audio_worker.speak_greek(w)

    def read_current_line(self):
        editor = self.current_editor()
        if editor:
            self.audio_worker.speak_greek(editor.current_line())

    def read_document(self):
        editor = self.current_editor()
        if editor:
            self.audio_worker.speak_greek(editor.toPlainText())

    def describe_current_char(self):
        editor = self.current_editor()
        if editor:
            ch = editor.current_char()
            self.audio_worker.speak_text(describe_char(ch, self.lang), interrupt=True)

    def stop_speech(self):
        self.audio_worker.speak_text("", interrupt=True)
        self.statusBar().showMessage(self.s["speech_stopped"], 2000)

    # ==================================================================
    # Study tools
    # ==================================================================
    def _require_not_exam(self):
        if self.exam_mode:
            self._announce(self.s["exam_blocked"])
            return False
        return True

    def add_note(self):
        if not self._require_not_exam():
            return
        editor = self.current_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        if not cursor.hasSelection():
            self._announce(self.s["note_none_selected"])
            return
        dlg = AnnotationDialog(self, self.s)
        if dlg.exec() and dlg.note_text():
            self.store.add_annotation(
                editor.file_path or "", cursor.selectionStart(), cursor.selectionEnd(),
                cursor.selectedText(), dlg.note_text(),
            )
            self._announce(self.s["note_added"])

    def view_notes(self):
        if not self._require_not_exam():
            return
        editor = self.current_editor()
        if not editor:
            return
        notes = self.store.get_annotations(editor.file_path or "")
        dlg = NotesDialog(self, self.s, notes)
        dlg.exec()
        if dlg.selected_id is not None:
            self.store.delete_annotation(dlg.selected_id)
        elif dlg.jump_to is not None:
            cursor = editor.textCursor()
            cursor.setPosition(dlg.jump_to["start_pos"])
            cursor.setPosition(dlg.jump_to["end_pos"], QTextCursor.MoveMode.KeepAnchor)
            editor.setTextCursor(cursor)
            editor.setFocus()

    def add_flashcard(self):
        if not self._require_not_exam():
            return
        editor = self.current_editor()
        if not editor:
            return
        entry = self._last_results[0] if self._last_results else quick_lookup(editor.current_word(), self.lang)
        if not entry:
            self._announce(self.s["not_found"].format(editor.current_word()))
            return
        lemma = entry.get("lemma", "")
        back = entry.get("definition", "")
        added = self.store.add_flashcard(lemma, lemma, back, entry.get("morphology", ""))
        if added:
            self._announce(self.s["flash_added"].format(lemma))
        else:
            self._announce(self.s["flash_exists"].format(lemma))

    def review_flashcards(self):
        if not self._require_not_exam():
            return
        if self.store.count_flashcards() == 0:
            self._announce(self.s["flash_none"])
            return
        due = self.store.due_flashcards()
        if not due:
            self._announce(self.s["flash_none_due"])
            return
        FlashcardReviewDialog(self, self.s, self.store, due,
                              speak=lambda t: self.audio_worker.speak_text(t)).exec()

    def manage_flashcards(self):
        ManageFlashcardsDialog(self, self.s, self.store).exec()

    def export_flashcards(self, anki):
        if self.store.count_flashcards() == 0:
            self._announce(self.s["flash_none"])
            return
        default = "logos_anki.txt" if anki else "logos_flashcards.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, self.s["export_anki"] if anki else self.s["export_flashcards"],
            default, "Anki (*.txt)" if anki else "CSV (*.csv)",
        )
        if not path:
            return
        n = self.store.export_flashcards_csv(path, anki=anki)
        self._announce(self.s["flash_exported"].format(n, os.path.basename(path)))

    def show_history(self):
        dlg = HistoryDialog(self, self.s, self.store.get_history())
        dlg.exec()
        if dlg.cleared:
            self.store.clear_history()

    def show_paradigm(self):
        if not self._require_not_exam():
            return
        editor = self.current_editor()
        if not editor:
            return
        word = editor.current_word()
        entry = self._last_results[0] if self._last_results else quick_lookup(word, self.lang)
        lemma = entry.get("lemma", word) if entry else word
        paradigm = generate_paradigm(lemma) or generate_paradigm(word)
        if not paradigm:
            self._announce(self.s["paradigm_none"].format(lemma))
            return
        ParadigmDialog(self, self.s, paradigm, self.lang).exec()

    # ==================================================================
    # Edit: find / goto
    # ==================================================================
    def _select_all(self):
        e = self.current_editor()
        if e:
            e.selectAll()

    def find_text(self):
        editor = self.current_editor()
        if not editor:
            return
        term, ok = QInputDialog.getText(self, self.s["find_title"], self.s["find_label"])
        if ok and term:
            self._last_search = term
            self._do_find(term)

    def find_next(self):
        if self._last_search:
            self._do_find(self._last_search)
        else:
            self.find_text()

    def _do_find(self, term):
        editor = self.current_editor()
        if not editor:
            return
        if not editor.find(term):
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            editor.setTextCursor(cursor)
            if editor.find(term):
                self.statusBar().showMessage(self.s["find_wrapped"], 3000)
            else:
                self._announce(self.s["find_not_found"].format(term))

    def goto_line(self):
        editor = self.current_editor()
        if not editor:
            return
        total = editor.document().blockCount()
        line, ok = QInputDialog.getInt(
            self, self.s["goto_title"], self.s["goto_label"], 1, 1, total
        )
        if ok:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.Down,
                                QTextCursor.MoveMode.MoveAnchor, line - 1)
            editor.setTextCursor(cursor)
            editor.setFocus()

    # ==================================================================
    # View / focus
    # ==================================================================
    def focus_editor(self):
        e = self.current_editor()
        if e:
            e.setFocus()

    def focus_dictionary(self):
        if not self.dict_dock.isVisible():
            self.dict_dock.show()
        self.dict_tree.setFocus()
        root = self.dict_tree.invisibleRootItem()
        if root.childCount():
            self.dict_tree.setCurrentItem(root.child(0))

    def _toggle_dict_panel(self):
        self.dict_dock.setVisible(not self.dict_dock.isVisible())
        self.settings["show_dictionary_panel"] = self.dict_dock.isVisible()
        save_settings(self.settings)

    def _change_font(self, delta):
        size = max(8, int(self.settings.get("font_point_size", 14)) + delta)
        self.settings["font_point_size"] = size
        save_settings(self.settings)
        for i in range(self.tabs.count()):
            self.tabs.widget(i).set_font_size(size)

    def _toggle_greek_mode(self, checked):
        e = self.current_editor()
        if e:
            e.set_greek_mode(checked)

    def _toggle_auto_speak(self, checked):
        self.settings["auto_speak_words"] = checked
        save_settings(self.settings)
        for i in range(self.tabs.count()):
            self.tabs.widget(i).set_auto_speak(checked)

    # ==================================================================
    # Settings / language / scheme / exam mode
    # ==================================================================
    def open_settings(self):
        dlg = SettingsDialog(self, self.settings, self.s, self.lang)
        if not dlg.exec():
            return
        new = dlg.result_settings
        lang_changed = new.get("language") != self.lang
        self.settings.update(new)
        save_settings(self.settings)
        self.audio_worker.set_scheme(self.settings["pronunciation_scheme"])
        self.audio_worker.set_rate(self.settings["speech_rate"])
        for i in range(self.tabs.count()):
            ed = self.tabs.widget(i)
            ed.set_font_size(self.settings["font_point_size"])
            ed.set_auto_speak(self.settings["auto_speak_words"])
        self.dict_dock.setVisible(self.settings["show_dictionary_panel"])
        if lang_changed:
            self.change_language(self.settings["language"])
        self._set_exam_mode(self.settings.get("exam_mode", False))

    def change_language(self, code):
        if code == self.lang:
            return
        self.lang = code
        self.settings["language"] = code
        save_settings(self.settings)
        self.s = get_strings(code)
        self.dict_worker.set_language(code)
        self.audio_worker.set_language(code)
        self._retranslate()
        self._announce(self.s["language_changed"])

    def change_scheme(self, scheme):
        self.settings["pronunciation_scheme"] = scheme
        save_settings(self.settings)
        self.audio_worker.set_scheme(scheme)
        labels = pronunciation.SCHEME_LABELS.get(self.lang, pronunciation.SCHEME_LABELS["en"])
        self._announce(self.s["scheme_changed"].format(labels[scheme]))

    def toggle_exam_mode(self, checked):
        self._set_exam_mode(checked)

    def _set_exam_mode(self, on):
        self.exam_mode = on
        self.settings["exam_mode"] = on
        save_settings(self.settings)
        if self.a_exam.isChecked() != on:
            self.a_exam.setChecked(on)
        self._apply_exam_mode()

    def _apply_exam_mode(self, initial=False):
        on = self.exam_mode
        # Disable study aids.
        self.m_study.setEnabled(not on)
        self.a_paradigm.setEnabled(not on)
        self.a_read_entry.setEnabled(not on)
        if on:
            self.dict_dock.hide()
            self._set_dict_hint()
            self._last_results = []
        else:
            self.dict_dock.setVisible(self.settings.get("show_dictionary_panel", True))
        if not initial:
            self._announce(self.s["exam_mode_on"] if on else self.s["exam_mode_off"])

    def _retranslate(self):
        s = self.s
        self.setWindowTitle(s["window_title"])
        self.setAccessibleName(s["window_title"])
        self.dict_dock.setWindowTitle(s["dict_title"])
        self.dict_dock.setAccessibleName(s["dict_title"])
        self.dict_tree.setAccessibleName(s["dict_title"])
        # Rebuild menus from scratch for simplicity and correctness.
        self.menuBar().clear()
        self._build_menus()
        self.a_exam.setChecked(self.exam_mode)
        self.a_auto_speak.setChecked(bool(self.settings.get("auto_speak_words")))
        for i in range(self.tabs.count()):
            self.tabs.widget(i).setPlaceholderText(s["editor_hint"])
        self._apply_exam_mode(initial=True)
        self._update_title()

    # ==================================================================
    # Help
    # ==================================================================
    def show_keyboard_guide(self):
        KeyboardGuideDialog(self, self.lang, self.s).exec()

    def show_about(self):
        AboutDialog(self, self.lang, self.s, VERSION).exec()

    def open_user_guide(self):
        # Open the bundled user guide in the OS default viewer.
        guide = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs",
                             f"USER_GUIDE.{self.lang}.md")
        if not os.path.exists(guide):
            guide = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "USER_GUIDE.en.md")
        if os.path.exists(guide):
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(guide))
        else:
            self.show_keyboard_guide()

    # ==================================================================
    # Helpers
    # ==================================================================
    def _announce(self, text):
        """Speak a short status message through the screen reader and status bar."""
        self.statusBar().showMessage(text, 5000)
        self.audio_worker.speak_text(text, interrupt=False)

    def closeEvent(self, event):
        for i in range(self.tabs.count() - 1, -1, -1):
            editor = self.tabs.widget(i)
            if not self._maybe_save(editor, i):
                event.ignore()
                return
        self.audio_worker.stop()
        self.audio_worker.wait(2000)
        self.dict_worker.stop()
        self.store.close()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Logos IDE")
    window = LogosMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
