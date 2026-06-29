# Logos IDE

**Un entorno accesible de estudio de griego antiguo y koiné para estudiantes ciegos y con baja visión.**

[🇬🇧 English](README.md) · 🇪🇸 Español

Logos IDE permite a un estudiante ciego **leer, escribir, escuchar y estudiar**
griego antiguo enteramente desde el teclado, con compatibilidad total con
**NVDA** y **JAWS**. Aspira a ser para el griego lo que
[EDICO](https://www.once.es) es para las ciencias: no una demostración, sino una
herramienta de estudio diaria y completa, y una compañera justa y ética en el
examen.

---

## Por qué existe

Estudiar griego es especialmente difícil sin vista:

- La **escritura politónica** acumula espíritus, acentos, iotas suscritas y
  diéresis sobre cada vocal. Quien ve los percibe de un vistazo; un lector de
  pantalla normalmente solo dice «alfa» y los signos diacríticos se pierden.
- **Las voces del sistema no saben pronunciar griego.** Una voz TTS en español o
  inglés lee las letras griegas por su nombre o las destroza.
- **Los diccionarios y las tablas de morfología en papel son visuales** y, en la
  práctica, inaccesibles.

Logos IDE resuelve cada uno de estos problemas directamente.

## Qué hace

- **Escribir griego desde un teclado latino.** `a`→α, `q`→θ, `w`→ω. Añada acentos
  y espíritus *después* de la vocal: `a)/` → ἄ, `w|` → ῳ. Las combinaciones no
  válidas se rechazan, de modo que nunca produce griego mal formado.
- **Escuchar la pronunciación correcta.** Un motor de transliteración convierte el
  griego en una grafía fonética que la voz de su lector de pantalla sí puede
  pronunciar, en cuatro esquemas conmutables: **erasmiana a la española** (por
  defecto), **erasmiana académica inglesa**, **griego moderno** y **ática
  restituida**.
- **Diccionario y morfología instantáneos.** Sitúe el cursor sobre una palabra y
  aparece su entrada del léxico Liddell‑Scott‑Jones (más de 575 000 formas). La
  búsqueda no distingue acentos, las abreviaturas se expanden para una lectura
  clara («indecl.» → «indeclinable») y los códigos de análisis se convierten en
  lenguaje llano.
- **«Describir este carácter»** lee en voz alta todos los acentos y espíritus del
  signo actual — `Ctrl+;` → «alfa con espíritu suave y acento agudo».
- **Lectura a petición**: palabra, línea, selección o todo el documento, sin la
  doble locución redundante sobre su lector de pantalla.
- **Herramientas de estudio**: notas/anotaciones, **tarjetas de vocabulario con
  repetición espaciada**, exportación a Anki/CSV, historial de palabras y
  **tablas de paradigmas** a petición para declinaciones y conjugaciones
  regulares.
- **Importación** de textos griegos desde PDF, EPUB o texto plano.
- **Modo examen**: desactiva el diccionario, la morfología y las notas, para que
  la misma herramienta con la que el estudiante escribe y lee cada día pueda
  usarse de forma justa en una evaluación.
- Interfaz **totalmente bilingüe** español / inglés, conmutable en cualquier
  momento.

Consulte la **[Guía del usuario](docs/USER_GUIDE.es.md)** para la referencia
completa de teclado.

## Accesibilidad

- Diseñado y probado para **NVDA** y **JAWS** en Windows.
- 100 % manejable con teclado; no requiere ratón ni teclado numérico.
- Habla con la **propia voz y velocidad** de su lector de pantalla mediante
  `accessible_output2`, con respaldo sin conexión `pyttsx3`.
- Evita deliberadamente la **locución redundante**: la aplicación nunca repite lo
  que su lector de pantalla ya dice.
- Tamaño de letra ajustable para personas con baja visión.

## Instalación

### Opción A — ejecutar desde el código

Requiere **Python 3.11 o superior**.

```bash
git clone https://github.com/fatima-elhalaoui/logos-ide.git
cd logos-ide
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt
python run_logos.py
```

En el primer arranque la aplicación usa un **diccionario inicial integrado** y
funciona de inmediato. Para el diccionario completo de 575 000 formas, instale el
**paquete de datos** (más abajo).

### Opción B — aplicación empaquetada (sin necesidad de Python) ⭐ la más fácil

Descargue **`LogosIDE-windows-x64.zip`** desde la
[página de versiones](../../releases), descomprímalo donde quiera y ejecute
**`LogosIDE.exe`**. El diccionario completo de 575 000 formas viene incluido: no
hay que instalar nada más. (También puede generarlo usted con
`pyinstaller logos.spec`.)

### El paquete de datos completo

La base de datos completa ocupa unos 300 MB, demasiado para el repositorio git,
por lo que se distribuye como recurso de la versión. Descargue
**`logos_dict.db.zip`** desde la [página de versiones](../../releases),
descomprímalo y coloque el archivo `logos_dict.db` resultante en su carpeta de
datos de usuario:

- **Windows:** `%LOCALAPPDATA%\LogosIDE\LogosIDE\logos_dict.db`

o apunte la variable de entorno `LOGOS_DB` a su ubicación. También puede
reconstruirlo con `scripts/build_database.py` (véase
[docs/DATA_SOURCES.md](docs/DATA_SOURCES.md)).

## Inicio rápido

1. Abra la aplicación. El cursor empieza en el editor de griego.
2. Escriba `a)nqrwpos` → ἄνθρωπος.
3. Pulse **F8** para escuchar la entrada del diccionario, o **F6** para leer el
   panel del diccionario.
4. Pulse **Ctrl+R** para escuchar una selección; **Ctrl+;** para describir un
   carácter.
5. Pulse **F1** en cualquier momento para la guía completa de escritura.

## Estado del proyecto

Versión **1.0.0**: completa y lista para pruebas. Se agradecen mucho los
comentarios tanto de estudiantes de griego ciegos como videntes; abra una
[incidencia](../../issues).

## Contribuir

Véase [CONTRIBUTING.md](CONTRIBUTING.md). Las tareas para empezar están
etiquetadas como `good first issue`.

## Licencia

Código: **MIT** (véase [LICENSE](LICENSE)).
Datos del diccionario: derivados del léxico LSJ y la morfología de la Perseus
Digital Library, **CC BY‑SA 3.0** — véase
[docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).
