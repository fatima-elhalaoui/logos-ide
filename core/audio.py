"""
Audio / text-to-speech for Logos IDE.

Greek is spoken by transliterating it (via :mod:`core.pronunciation`) into a
phonetic spelling and sending that to the user's active screen reader through
``accessible_output2`` — so it uses the voice, rate and device the student has
already configured in NVDA / JAWS. When no screen reader is available (e.g. a
test box or some Linux setups) it falls back to an offline ``pyttsx3`` voice.

All speech happens on a dedicated worker thread because ``pyttsx3.runAndWait``
and COM calls would otherwise block the GUI and freeze the screen reader.
"""

import queue

from PyQt6.QtCore import QThread, pyqtSignal

from core import pronunciation
from core.logger import get_logger

log = get_logger(__name__)


def greek_to_phonetic(text, scheme=pronunciation.DEFAULT_SCHEME, language="es"):
    """Transliterate Greek to a target-language phonetic spelling."""
    return pronunciation.transliterate(text, scheme, language)


# Backwards-compatible alias used by older code/tests.
def greek_to_erasmian(text, language="en"):
    return pronunciation.transliterate(text, "erasmian", language)


class _Speaker:
    """Thin abstraction over accessible_output2 with a pyttsx3 fallback."""

    def __init__(self):
        self.backend = None
        self.kind = None
        self._pyttsx = None
        try:
            from accessible_output2.outputs.auto import Auto
            self.backend = Auto()
            self.kind = "screen_reader"
        except Exception as e:  # pragma: no cover
            log.warning("accessible_output2 unavailable: %s", e)

    def _ensure_pyttsx(self):
        if self._pyttsx is None:
            import pyttsx3
            self._pyttsx = pyttsx3.init()
        return self._pyttsx

    def speak(self, text, interrupt=True, rate=None):
        if not text:
            return
        spoke = False
        if self.backend is not None:
            try:
                self.backend.speak(text, interrupt=interrupt)
                spoke = True
            except Exception as e:  # pragma: no cover
                log.warning("screen-reader speak failed, falling back: %s", e)
        if not spoke:
            try:
                eng = self._ensure_pyttsx()
                if rate:
                    eng.setProperty("rate", rate)
                eng.say(text)
                eng.runAndWait()
            except Exception as e:  # pragma: no cover
                log.error("pyttsx3 speak failed: %s", e)

    def silence(self):
        if self.backend is not None:
            try:
                self.backend.output("", interrupt=True)
            except Exception:
                pass


class TTSAudioWorker(QThread):
    """Background speech queue."""

    speech_started = pyqtSignal()
    speech_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None, language="es", scheme=pronunciation.DEFAULT_SCHEME, rate=None):
        super().__init__(parent)
        self.speech_queue = queue.Queue()
        self.is_running = True
        self.language = language
        self.scheme = scheme
        self.rate = rate
        self._speaker = None

    # ----- configuration (thread-safe scalar writes) ------------------
    def set_language(self, lang):
        self.language = lang

    def set_scheme(self, scheme):
        self.scheme = scheme

    def set_rate(self, rate):
        self.rate = rate

    # ----- public API -------------------------------------------------
    def speak_greek(self, greek_text, interrupt=True):
        """Queue Ancient Greek to be transliterated (off the GUI thread) and spoken."""
        self.speech_queue.put(("greek", greek_text, interrupt))

    def speak_text(self, text, interrupt=True):
        """Queue plain text (already in the UI language) to be spoken verbatim."""
        self.speech_queue.put(("text", text, interrupt))

    def stop(self):
        self.is_running = False
        self.speech_queue.put(None)

    # ----- thread loop ------------------------------------------------
    def run(self):
        # Some screen-reader / SAPI backends use COM, which needs an apartment
        # initialised on this worker thread (the GUI thread's does not carry over).
        _com = False
        try:
            import pythoncom
            pythoncom.CoInitialize()
            _com = True
        except Exception:
            pass

        self._speaker = _Speaker()
        while self.is_running:
            item = self.speech_queue.get()
            if item is None or not self.is_running:
                break
            kind, payload, interrupt = item
            # Heavy transliteration happens here, on the worker thread.
            if kind == "greek":
                text = pronunciation.transliterate(payload, self.scheme, self.language)
            else:
                text = payload
            if text and text.strip():
                try:
                    self.speech_started.emit()
                    self._speaker.speak(text, interrupt=interrupt, rate=self.rate)
                    self.speech_finished.emit()
                except Exception as e:  # pragma: no cover
                    # One failure must not kill the whole speech thread.
                    self.error_occurred.emit(str(e))

        if _com:
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except Exception:
                pass
