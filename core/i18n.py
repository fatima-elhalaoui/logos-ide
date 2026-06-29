"""
All user-facing strings for Logos IDE, in English and Spanish.

Every visible label, menu item, dialog and spoken status message has a key here.
Use :func:`get_strings` (or ``UI_STRINGS[lang]``) to fetch the active table.
Missing keys fall back to English so nothing ever renders blank.
"""

EN = {
    # --- window / panels ---
    "window_title": "Logos IDE — Ancient Greek Study Tool",
    "dict_title": "Dictionary & Morphology",
    "dict_hint": "Place the cursor on a Greek word to see its dictionary entry.",
    "dict_preparing": "Preparing the dictionary, please wait…",
    "dict_ready": "Dictionary ready.",
    "editor_hint": "Greek editor. Type Latin letters to write Greek. Use ) ( / \\ = | + after a vowel for breathings and accents. Press F1 for the full guide.",
    "editor_name": "Ancient Greek text editor",
    "editor_desc": "Type Latin letters to produce polytonic Greek. Press F1 for the typing guide.",

    # --- menus ---
    "file_menu": "&File",
    "edit_menu": "&Edit",
    "view_menu": "&View",
    "greek_menu": "&Greek",
    "audio_menu": "&Audio",
    "study_menu": "S&tudy",
    "settings_menu": "&Settings",
    "help_menu": "&Help",

    # --- file menu ---
    "new": "&New",
    "open": "&Open…",
    "save": "&Save",
    "save_as": "Save &As…",
    "import": "&Import Document (PDF/EPUB)…",
    "close_tab": "&Close Tab",
    "exit": "E&xit",

    # --- edit menu ---
    "find": "&Find…",
    "find_next": "Find &Next",
    "goto_line": "&Go to Line…",
    "select_all": "Select &All",

    # --- view menu ---
    "increase_font": "&Increase Font Size",
    "decrease_font": "&Decrease Font Size",
    "toggle_dict": "Toggle &Dictionary Panel",
    "focus_editor": "Focus &Editor",
    "focus_dict": "Focus &Dictionary",

    # --- greek menu ---
    "describe_char": "Describe Current &Character",
    "read_word": "Read Current &Word",
    "read_line": "Read Current &Line",
    "read_document": "Read Whole &Document",
    "keyboard_guide": "Polytonic &Keyboard Guide",
    "show_paradigm": "Show &Paradigm of Current Word",

    # --- audio menu ---
    "read": "&Read Selected Text",
    "read_entry": "Read &Dictionary Entry",
    "stop_speech": "&Stop Speech",
    "pron_scheme": "&Pronunciation Scheme",
    "auto_speak": "Speak Greek &As I Type",
    "greek_input": "&Greek Input (on/off)",

    # --- study menu ---
    "add_note": "Add &Note to Selection…",
    "view_notes": "&View Notes for This File…",
    "note_jump": "&Jump to Note Here",
    "add_flashcard": "Add Current Word to &Flashcards",
    "review_flashcards": "&Review Flashcards…",
    "manage_flashcards": "&Manage Flashcards…",
    "export_flashcards": "&Export Flashcards (CSV)…",
    "export_anki": "Export for &Anki…",
    "history": "Word &History…",

    # --- settings menu ---
    "open_settings": "&Preferences…",
    "language": "&Language",
    "exam_mode": "&Exam Mode",
    "exam_mode_on": "Exam mode is ON. Dictionary, morphology and notes are disabled.",
    "exam_mode_off": "Exam mode is OFF. All study aids are available.",

    # --- help menu ---
    "guide": "Keyboard &Shortcuts",
    "user_guide": "&User Guide",
    "about": "&About Logos IDE",

    # --- dictionary results ---
    "result_of": "Result {0} of {1} — {2}",
    "lemma": "Lemma: {0}",
    "morphology": "Form: {0}",
    "definition": "Definition: {0}",
    "not_found": "No dictionary entry found for “{0}”.",
    "exam_blocked": "Dictionary lookup is disabled in exam mode.",

    # --- dialogs: settings ---
    "settings_title": "Preferences",
    "settings_language": "Interface language",
    "settings_scheme": "Greek pronunciation",
    "settings_rate": "Speech rate (blank = use screen reader default)",
    "settings_autospeak": "Speak Greek pronunciation when I finish a word",
    "settings_font": "Editor font size",
    "settings_exam": "Exam mode (disable dictionary, morphology and notes)",
    "settings_show_dict": "Show the dictionary panel",
    "ok": "OK",
    "cancel": "Cancel",
    "close": "Close",
    "save_btn": "Save",
    "delete": "Delete",

    # --- dialogs: annotation ---
    "note_title": "Add Note",
    "note_prompt": "Note for the selected text:",
    "note_added": "Note added.",
    "note_none_selected": "Select some text first, then add a note.",
    "notes_title": "Notes",
    "notes_empty": "There are no notes for this file yet.",
    "note_present": "Note here. Press {0} to read it.",
    "note_at": "Note: {0}",

    # --- dialogs: flashcards ---
    "flash_added": "Added “{0}” to your flashcards.",
    "flash_exists": "“{0}” is already in your flashcards.",
    "flash_none": "You have no flashcards yet. Add words from the dictionary first.",
    "flash_none_due": "No flashcards are due for review right now. Well done!",
    "flash_review_title": "Review Flashcards",
    "flash_front": "Front: {0}",
    "flash_show_answer": "Show Answer",
    "flash_answer": "Answer: {0}",
    "flash_correct": "I knew it",
    "flash_wrong": "I missed it",
    "flash_progress": "Card {0} of {1}",
    "flash_done": "Review finished. You reviewed {0} cards.",
    "flash_manage_title": "Manage Flashcards",
    "flash_exported": "Exported {0} flashcards to {1}.",
    "flash_word": "{0} — {1}",

    # --- dialogs: paradigm ---
    "paradigm_title": "Paradigm",
    "paradigm_none": "No regular paradigm is available for “{0}”.",
    "paradigm_for": "Paradigm of {0}",

    # --- dialogs: find / goto ---
    "find_title": "Find",
    "find_label": "Find what:",
    "find_not_found": "“{0}” was not found.",
    "find_wrapped": "Reached the end; search continued from the top.",
    "goto_title": "Go to Line",
    "goto_label": "Line number:",

    # --- dialogs: history ---
    "history_title": "Word History",
    "history_empty": "No words have been looked up yet.",
    "history_clear": "Clear History",

    # --- dialogs: about ---
    "about_title": "About Logos IDE",
    "about_text": (
        "Logos IDE — an accessible Ancient & Koine Greek study environment for "
        "blind and low-vision students.\n\nVersion {0}\n\nFree and open source. "
        "Built to be fully usable with NVDA and JAWS."
    ),

    # --- file ops / errors ---
    "untitled": "Untitled",
    "open_error": "Could not open the file:\n{0}",
    "save_error": "Could not save the file:\n{0}",
    "import_error": "Could not import the document:\n{0}",
    "import_title": "Importing",
    "import_progress": "Importing document…",
    "unsaved_title": "Unsaved Changes",
    "unsaved_msg": "This tab has unsaved changes. Save them before closing?",
    "save_choice": "Save",
    "discard_choice": "Discard",
    "saved": "Saved.",
    "language_changed": "Interface language set to English.",
    "scheme_changed": "Pronunciation scheme: {0}.",
    "speech_stopped": "Speech stopped.",
    "nothing_selected": "Nothing is selected.",
    "seed_db_notice": "Using the built-in starter dictionary. Install the full data pack for complete coverage.",
}

ES = {
    # --- ventana / paneles ---
    "window_title": "Logos IDE — Herramienta de Estudio de Griego Antiguo",
    "dict_title": "Diccionario y Morfología",
    "dict_hint": "Coloque el cursor sobre una palabra griega para ver su entrada.",
    "dict_preparing": "Preparando el diccionario, espere por favor…",
    "dict_ready": "Diccionario listo.",
    "editor_hint": "Editor de griego. Escriba letras latinas para producir griego. Use ) ( / \\ = | + después de una vocal para espíritus y acentos. Pulse F1 para la guía completa.",
    "editor_name": "Editor de texto en griego antiguo",
    "editor_desc": "Escriba letras latinas para producir griego politónico. Pulse F1 para la guía de escritura.",

    # --- menús ---
    "file_menu": "&Archivo",
    "edit_menu": "&Edición",
    "view_menu": "&Ver",
    "greek_menu": "&Griego",
    "audio_menu": "&Audio",
    "study_menu": "Es&tudio",
    "settings_menu": "&Configuración",
    "help_menu": "A&yuda",

    # --- archivo ---
    "new": "&Nuevo",
    "open": "&Abrir…",
    "save": "&Guardar",
    "save_as": "Guardar &como…",
    "import": "&Importar documento (PDF/EPUB)…",
    "close_tab": "&Cerrar pestaña",
    "exit": "&Salir",

    # --- edición ---
    "find": "&Buscar…",
    "find_next": "Buscar &siguiente",
    "goto_line": "&Ir a la línea…",
    "select_all": "Seleccionar &todo",

    # --- ver ---
    "increase_font": "&Aumentar tamaño de letra",
    "decrease_font": "&Reducir tamaño de letra",
    "toggle_dict": "Mostrar/ocultar panel del &diccionario",
    "focus_editor": "Enfocar el &editor",
    "focus_dict": "Enfocar el &diccionario",

    # --- griego ---
    "describe_char": "Describir el &carácter actual",
    "read_word": "Leer la &palabra actual",
    "read_line": "Leer la &línea actual",
    "read_document": "Leer todo el &documento",
    "keyboard_guide": "Guía del &teclado politónico",
    "show_paradigm": "Mostrar el &paradigma de la palabra actual",

    # --- audio ---
    "read": "&Leer el texto seleccionado",
    "read_entry": "Leer la entrada del &diccionario",
    "stop_speech": "&Detener la voz",
    "pron_scheme": "&Esquema de pronunciación",
    "auto_speak": "Pronunciar el griego &mientras escribo",
    "greek_input": "Escritura &griega (activar/desactivar)",

    # --- estudio ---
    "add_note": "Añadir &nota a la selección…",
    "view_notes": "&Ver notas de este archivo…",
    "note_jump": "&Saltar a la nota aquí",
    "add_flashcard": "Añadir la palabra actual a las &tarjetas",
    "review_flashcards": "&Repasar tarjetas…",
    "manage_flashcards": "&Gestionar tarjetas…",
    "export_flashcards": "&Exportar tarjetas (CSV)…",
    "export_anki": "Exportar para &Anki…",
    "history": "&Historial de palabras…",

    # --- configuración ---
    "open_settings": "&Preferencias…",
    "language": "&Idioma",
    "exam_mode": "Modo &examen",
    "exam_mode_on": "El modo examen está ACTIVADO. El diccionario, la morfología y las notas están desactivados.",
    "exam_mode_off": "El modo examen está DESACTIVADO. Todas las ayudas de estudio están disponibles.",

    # --- ayuda ---
    "guide": "&Atajos de teclado",
    "user_guide": "&Manual de usuario",
    "about": "&Acerca de Logos IDE",

    # --- resultados del diccionario ---
    "result_of": "Resultado {0} de {1} — {2}",
    "lemma": "Lema: {0}",
    "morphology": "Forma: {0}",
    "definition": "Definición: {0}",
    "not_found": "No se encontró ninguna entrada para «{0}».",
    "exam_blocked": "La consulta del diccionario está desactivada en el modo examen.",

    # --- diálogos: preferencias ---
    "settings_title": "Preferencias",
    "settings_language": "Idioma de la interfaz",
    "settings_scheme": "Pronunciación del griego",
    "settings_rate": "Velocidad de la voz (vacío = usar la del lector de pantalla)",
    "settings_autospeak": "Pronunciar el griego al terminar una palabra",
    "settings_font": "Tamaño de letra del editor",
    "settings_exam": "Modo examen (desactiva diccionario, morfología y notas)",
    "settings_show_dict": "Mostrar el panel del diccionario",
    "ok": "Aceptar",
    "cancel": "Cancelar",
    "close": "Cerrar",
    "save_btn": "Guardar",
    "delete": "Eliminar",

    # --- diálogos: nota ---
    "note_title": "Añadir nota",
    "note_prompt": "Nota para el texto seleccionado:",
    "note_added": "Nota añadida.",
    "note_none_selected": "Seleccione primero un texto y luego añada la nota.",
    "notes_title": "Notas",
    "notes_empty": "Todavía no hay notas para este archivo.",
    "note_present": "Hay una nota aquí. Pulse {0} para leerla.",
    "note_at": "Nota: {0}",

    # --- diálogos: tarjetas ---
    "flash_added": "Se añadió «{0}» a sus tarjetas.",
    "flash_exists": "«{0}» ya está en sus tarjetas.",
    "flash_none": "Aún no tiene tarjetas. Añada palabras desde el diccionario.",
    "flash_none_due": "No hay tarjetas para repasar ahora. ¡Bien hecho!",
    "flash_review_title": "Repasar tarjetas",
    "flash_front": "Anverso: {0}",
    "flash_show_answer": "Mostrar respuesta",
    "flash_answer": "Respuesta: {0}",
    "flash_correct": "La sabía",
    "flash_wrong": "No la sabía",
    "flash_progress": "Tarjeta {0} de {1}",
    "flash_done": "Repaso terminado. Repasó {0} tarjetas.",
    "flash_manage_title": "Gestionar tarjetas",
    "flash_exported": "Se exportaron {0} tarjetas a {1}.",
    "flash_word": "{0} — {1}",

    # --- diálogos: paradigma ---
    "paradigm_title": "Paradigma",
    "paradigm_none": "No hay un paradigma regular disponible para «{0}».",
    "paradigm_for": "Paradigma de {0}",

    # --- diálogos: buscar / ir a ---
    "find_title": "Buscar",
    "find_label": "Buscar:",
    "find_not_found": "No se encontró «{0}».",
    "find_wrapped": "Se llegó al final; la búsqueda continuó desde el principio.",
    "goto_title": "Ir a la línea",
    "goto_label": "Número de línea:",

    # --- diálogos: historial ---
    "history_title": "Historial de palabras",
    "history_empty": "Todavía no se ha consultado ninguna palabra.",
    "history_clear": "Borrar historial",

    # --- diálogos: acerca de ---
    "about_title": "Acerca de Logos IDE",
    "about_text": (
        "Logos IDE — un entorno accesible de estudio de griego antiguo y koiné "
        "para estudiantes ciegos y con baja visión.\n\nVersión {0}\n\nLibre y de "
        "código abierto. Diseñado para usarse plenamente con NVDA y JAWS."
    ),

    # --- archivos / errores ---
    "untitled": "Sin título",
    "open_error": "No se pudo abrir el archivo:\n{0}",
    "save_error": "No se pudo guardar el archivo:\n{0}",
    "import_error": "No se pudo importar el documento:\n{0}",
    "import_title": "Importando",
    "import_progress": "Importando documento…",
    "unsaved_title": "Cambios sin guardar",
    "unsaved_msg": "Esta pestaña tiene cambios sin guardar. ¿Desea guardarlos antes de cerrar?",
    "save_choice": "Guardar",
    "discard_choice": "Descartar",
    "saved": "Guardado.",
    "language_changed": "Idioma de la interfaz establecido en español.",
    "scheme_changed": "Esquema de pronunciación: {0}.",
    "speech_stopped": "Voz detenida.",
    "nothing_selected": "No hay nada seleccionado.",
    "seed_db_notice": "Usando el diccionario inicial integrado. Instale el paquete de datos completo para una cobertura total.",
}

UI_STRINGS = {"en": EN, "es": ES}


class _Strings:
    """Dict-like accessor that falls back to English for missing keys."""

    def __init__(self, lang):
        self._lang = lang if lang in UI_STRINGS else "en"

    def __getitem__(self, key):
        return UI_STRINGS[self._lang].get(key, EN.get(key, key))

    def get(self, key, default=None):
        return UI_STRINGS[self._lang].get(key, EN.get(key, default))


def get_strings(lang):
    return _Strings(lang)
