"""Bilingual keyboard-guide and About dialogs (accessible QTextBrowser based)."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextBrowser, QPushButton, QDialogButtonBox,
)

_GUIDE_EN = """
<h1>Polytonic Greek Typing Guide</h1>
<p>Type a Latin letter to get the matching Greek letter. Type a modifier
<strong>right after</strong> a vowel to add an accent or breathing. Modifiers can
be combined.</p>

<h2>Letters</h2>
<ul>
<li>a=α b=β g=γ d=δ e=ε z=ζ h=η q=θ i=ι k=κ l=λ m=μ</li>
<li>n=ν c=ξ o=ο p=π r=ρ s=σ t=τ u=υ f=φ x=χ y=ψ w=ω</li>
<li>v = ς (final sigma) — also added automatically at the end of a word</li>
<li>Capital Latin letters give capital Greek letters.</li>
</ul>

<h2>Accents &amp; breathings (type after the vowel)</h2>
<ul>
<li><strong>/</strong> acute (ά) &nbsp; <strong>\\</strong> grave (ὰ) &nbsp;
<strong>=</strong> circumflex (ᾶ)</li>
<li><strong>)</strong> smooth breathing (ἀ) &nbsp; <strong>(</strong> rough breathing (ἁ)</li>
<li><strong>|</strong> iota subscript (ᾳ) &nbsp; <strong>+</strong> diaeresis (ϊ)</li>
<li>Combine them: <code>a(/</code> → ἅ, &nbsp; <code>w|</code> → ῳ</li>
<li><strong>:</strong> gives the Greek high dot · (ano teleia)</li>
</ul>

<h2>Key commands</h2>
<ul>
<li><strong>Ctrl+G</strong> turn Greek input on/off (for English notes)</li>
<li><strong>F5</strong> focus the editor &nbsp; <strong>F6</strong> focus the dictionary</li>
<li><strong>F8</strong> read the dictionary entry of the current word</li>
<li><strong>Ctrl+R</strong> read the selected text aloud (Greek pronunciation)</li>
<li><strong>Ctrl+;</strong> describe the current character and its accents</li>
<li><strong>Ctrl+Shift+P</strong> show the paradigm of the current word</li>
<li><strong>Ctrl+D</strong> add the current word to flashcards</li>
<li><strong>Ctrl+Space</strong> stop speech</li>
</ul>
"""

_GUIDE_ES = """
<h1>Guía para escribir griego politónico</h1>
<p>Escriba una letra latina para obtener la letra griega correspondiente. Escriba
un modificador <strong>justo después</strong> de una vocal para añadir un acento o
espíritu. Los modificadores se pueden combinar.</p>

<h2>Letras</h2>
<ul>
<li>a=α b=β g=γ d=δ e=ε z=ζ h=η q=θ i=ι k=κ l=λ m=μ</li>
<li>n=ν c=ξ o=ο p=π r=ρ s=σ t=τ u=υ f=φ x=χ y=ψ w=ω</li>
<li>v = ς (sigma final) — también se añade automáticamente al final de palabra</li>
<li>Las mayúsculas latinas dan mayúsculas griegas.</li>
</ul>

<h2>Acentos y espíritus (escríbalos tras la vocal)</h2>
<ul>
<li><strong>/</strong> agudo (ά) &nbsp; <strong>\\</strong> grave (ὰ) &nbsp;
<strong>=</strong> circunflejo (ᾶ)</li>
<li><strong>)</strong> espíritu suave (ἀ) &nbsp; <strong>(</strong> espíritu áspero (ἁ)</li>
<li><strong>|</strong> iota suscrita (ᾳ) &nbsp; <strong>+</strong> diéresis (ϊ)</li>
<li>Combínelos: <code>a(/</code> → ἅ, &nbsp; <code>w|</code> → ῳ</li>
<li><strong>:</strong> produce el punto alto griego · (ano teleia)</li>
</ul>

<h2>Comandos de teclado</h2>
<ul>
<li><strong>Ctrl+G</strong> activar/desactivar la escritura griega (para notas en español)</li>
<li><strong>F5</strong> enfocar el editor &nbsp; <strong>F6</strong> enfocar el diccionario</li>
<li><strong>F8</strong> leer la entrada del diccionario de la palabra actual</li>
<li><strong>Ctrl+R</strong> leer en voz alta el texto seleccionado (pronunciación griega)</li>
<li><strong>Ctrl+;</strong> describir el carácter actual y sus acentos</li>
<li><strong>Ctrl+Mayús+P</strong> mostrar el paradigma de la palabra actual</li>
<li><strong>Ctrl+D</strong> añadir la palabra actual a las tarjetas</li>
<li><strong>Ctrl+Espacio</strong> detener la voz</li>
</ul>
"""


class _ReadOnlyHtmlDialog(QDialog):
    def __init__(self, parent, title, html, close_label="Close"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(560, 620)
        self.setAccessibleName(title)

        layout = QVBoxLayout(self)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setReadOnly(True)
        self.browser.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.browser.setAccessibleName(title)
        self.browser.setHtml(html)
        cur = self.browser.textCursor()
        cur.movePosition(QTextCursor.MoveOperation.Start)
        self.browser.setTextCursor(cur)
        layout.addWidget(self.browser)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn = buttons.button(QDialogButtonBox.StandardButton.Close)
        btn.setText(close_label)
        btn.setDefault(True)
        buttons.rejected.connect(self.accept)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        self.browser.setFocus()


class KeyboardGuideDialog(_ReadOnlyHtmlDialog):
    def __init__(self, parent=None, lang="en", strings=None):
        title = ("Guía del teclado politónico" if lang == "es"
                 else "Polytonic Keyboard Guide")
        html = _GUIDE_ES if lang == "es" else _GUIDE_EN
        close = strings["close"] if strings else "Close"
        super().__init__(parent, title, html, close)


class AboutDialog(_ReadOnlyHtmlDialog):
    def __init__(self, parent=None, lang="en", strings=None, version="1.0.0"):
        title = strings["about_title"] if strings else "About Logos IDE"
        body = (strings["about_text"] if strings else "Logos IDE\n\nVersion {0}").format(version)
        html = "<h1>Logos IDE</h1>" + "".join(
            f"<p>{line}</p>" for line in body.split("\n") if line.strip()
        )
        close = strings["close"] if strings else "Close"
        super().__init__(parent, title, html, close)
