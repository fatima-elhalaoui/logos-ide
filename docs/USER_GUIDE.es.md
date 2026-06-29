# Logos IDE — Guía del usuario

Esta guía explica todo lo que Logos IDE puede hacer y cada comando de teclado.
Está redactada para leerse cómodamente con un lector de pantalla.

## 1. Lo básico

Al abrir Logos IDE, el cursor está en el **editor de griego**. Todo lo que
escriba se convierte de letras latinas a griego. A la derecha está el panel
**Diccionario y Morfología**, y hay una barra de menús con Archivo, Edición, Ver,
Griego, Audio, Estudio, Configuración y Ayuda.

Cambie toda la interfaz entre español e inglés en cualquier momento desde
**Configuración → Idioma**, o en Preferencias (`Ctrl+,`).

## 2. Escribir en griego

Escriba la letra latina que corresponde a cada letra griega:

| Escriba | Obtiene | Escriba | Obtiene | Escriba | Obtiene |
|---------|---------|---------|---------|---------|---------|
| a | α | b | β | g | γ |
| d | δ | e | ε | z | ζ |
| h | η | q | θ | i | ι |
| k | κ | l | λ | m | μ |
| n | ν | c | ξ | o | ο |
| p | π | r | ρ | s | σ |
| t | τ | u | υ | f | φ |
| x | χ | y | ψ | w | ω |

- `v` produce la sigma final **ς**. Una **σ** medial al final de palabra también
  se convierte en **ς** automáticamente al pulsar espacio o un signo de puntuación.
- Una letra latina mayúscula produce una griega mayúscula (`A` → Α).
- `:` produce el punto alto griego **·** (ano teleia).

### Acentos y espíritus

Escriba el modificador **justo después** de la vocal. Los modificadores se combinan.

| Tecla | Signo | Ejemplo |
|-------|-------|---------|
| `/` | agudo | `a/` → ά |
| `\` | grave | `a\` → ὰ |
| `=` | circunflejo | `a=` → ᾶ |
| `)` | espíritu suave | `a)` → ἀ |
| `(` | espíritu áspero | `a(` → ἁ |
| `\|` | iota suscrita | `a\|` → ᾳ |
| `+` | diéresis | `i+` → ϊ |

Combínelos en cualquier orden: `a(/` → ἅ, `w|` → ῳ, `h=|` → ῇ. Si una combinación
no es un carácter griego real (por ejemplo, una consonante con circunflejo),
Logos IDE la rechaza en lugar de producir un signo defectuoso.

### Activar/desactivar la escritura griega

Pulse **`Ctrl+G`** para desactivar la conversión a griego, de modo que pueda
escribir notas en español o inglés en el mismo documento, y vuelva a activarla
para continuar en griego.

## 3. Escuchar el texto

Su lector de pantalla lee el editor con normalidad mientras se desplaza. Para una
pronunciación antigua correcta, use estos comandos:

| Comando | Tecla |
|---------|-------|
| Leer el texto seleccionado | `Ctrl+R` |
| Leer la palabra actual | `Ctrl+Mayús+W` |
| Leer la línea actual | `Ctrl+Mayús+L` |
| Leer todo el documento | `Ctrl+Mayús+D` |
| Describir el carácter actual (sus acentos) | `Ctrl+;` |
| Leer la entrada del diccionario de la palabra actual | `F8` |
| Detener la voz | `Ctrl+Espacio` |

**Esquema de pronunciación.** Elija erasmiana a la española, erasmiana inglesa,
griego moderno o ática restituida en **Audio → Esquema de pronunciación** o en
Preferencias. La pronunciación usa la propia voz de su lector de pantalla.

Por defecto, Logos IDE **no** pronuncia cada letra al escribir: su lector de
pantalla ya lo hace. Si prefiere que la aplicación lea cada palabra griega
terminada, active **Audio → Pronunciar el griego mientras escribo**.

## 4. Diccionario y morfología

Sitúe el cursor sobre cualquier palabra griega y su entrada se carga
automáticamente en el panel del diccionario (pulse **`F6`** para ir allí y leerla,
**`F5`** para volver al editor). O pulse **`F8`** para escuchar la entrada sin
salir del editor.

- La búsqueda ignora los acentos, así que encuentra la palabra aunque no haya
  escrito todos los signos.
- Las abreviaturas del léxico se expanden para una lectura clara.
- Cuando una palabra tiene varios análisis posibles, cada uno se lista como un
  resultado distinto.

> El diccionario inicial integrado cubre el vocabulario de alta frecuencia.
> Instale el paquete de datos completo (véase el README) para el léxico completo
> de 575 000 formas.

## 5. Herramientas de estudio

| Herramienta | Cómo |
|-------------|------|
| Añadir una nota al texto seleccionado | `Ctrl+Mayús+N` |
| Ver / saltar a / eliminar notas | Estudio → Ver notas |
| Añadir la palabra actual a las tarjetas | `Ctrl+D` |
| Repasar tarjetas (repetición espaciada) | `Ctrl+Mayús+R` |
| Gestionar / eliminar tarjetas | Estudio → Gestionar tarjetas |
| Exportar tarjetas a CSV o Anki | Estudio → Exportar… |
| Historial de palabras | Estudio → Historial de palabras |
| Mostrar el paradigma de la palabra actual | `Ctrl+Mayús+P` |

**Las tarjetas** usan el método de Leitner: las que sabe vuelven menos a menudo,
las que falla vuelven antes. En el repaso, pulse **Mostrar respuesta** y luego
**La sabía** o **No la sabía**.

**Los paradigmas** generan la declinación o conjugación regular de una palabra
(las tres declinaciones del sustantivo, el verbo regular en ‑ω y εἰμί). El
diálogo es un árbol por el que puede desplazarse forma a forma.

## 6. Modo examen

**Configuración → Modo examen** (`Ctrl+Mayús+E`) desactiva el diccionario, la
morfología, los paradigmas y las notas, manteniendo la escritura y la lectura en
voz alta de su propio texto. Así puede usar el mismo editor de siempre en una
evaluación sin ninguna ayuda de consulta: la forma honesta, al estilo de EDICO,
de hacer un examen.

## 7. Archivos y documentos

| Acción | Tecla |
|--------|-------|
| Nueva pestaña | `Ctrl+N` |
| Abrir un archivo de texto | `Ctrl+O` |
| Guardar / Guardar como | `Ctrl+S` / `Ctrl+Mayús+S` |
| Importar un documento PDF / EPUB / texto | `Ctrl+I` |
| Cerrar la pestaña actual | `Ctrl+W` |
| Pestaña siguiente / anterior | `Ctrl+Tab` / `Ctrl+Mayús+Tab` |
| Buscar / Buscar siguiente | `Ctrl+F` / `F3` |
| Ir a la línea | `Ctrl+L` |
| Salir | `Ctrl+Q` |

## 8. Vista y comodidad

| Acción | Tecla |
|--------|-------|
| Aumentar el tamaño de letra | `Ctrl+=` |
| Reducir el tamaño de letra | `Ctrl+-` |
| Mostrar/ocultar el panel del diccionario | `F4` |
| Enfocar el editor | `F5` |
| Enfocar el diccionario | `F6` |
| Guía del teclado | `F1` |

## 9. Dónde se guardan sus datos

La configuración, las tarjetas, las notas y los registros se guardan en su carpeta
de datos de usuario (`%LOCALAPPDATA%\LogosIDE` en Windows), de modo que se
conservan entre actualizaciones.

## 10. Obtener ayuda

Pulse **`F1`** para la guía de escritura, o abra **Ayuda → Manual de usuario**.
Para informar de un problema o sugerir una función, abra una incidencia en la
página de GitHub del proyecto.
