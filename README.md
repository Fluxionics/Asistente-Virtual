# Fluxionics
*La Pagina Oficial es [Fluxionics](https://fluxionics.github.io)*
*Redes Sociales [Fluxionics Redes](https://fluxionics.github.io/contacto.html)*

# Sobre la version
🌟 Funciones Nuevas (Control Real)
Anti-Grabación de Nivel Kernel:

Antes: El "Modo Incógnito" solo cambiaba colores o ponía la ventana algo transparente.

Ahora: Utiliza SetWindowDisplayAffinity. Esto le dice a Windows que la ventana de Fluxi es información protegida. Si intentas grabar con OBS, hacer stream en Discord o tomar una captura de pantalla (Win + Shift + S), Fluxi aparecerá como un cuadro negro sólido. Tú la ves, pero los demás no.

Brillo de Hardware Directo:

Antes: No podía cambiar el brillo o solo lo simulaba.

Ahora: Se comunica con el monitor mediante DDC/CI. Si le pides "Brillo al 10%", la luz de tu pantalla bajará físicamente.

Control de Audio Maestro:

Antes: Podía tener errores al intentar acceder al volumen.

Ahora: Usa la API de Windows (pycaw) para controlar el volumen general del sistema con precisión de 0 a 100.

Movimiento de Mouse Físico:

Ahora: Incluimos una función para mover el cursor a coordenadas reales o puntos clave (como el centro de la pantalla) con animaciones suaves (pyautogui).

Sistema de Autorización:

Nuevo: Por seguridad, antes de mover el mouse o cambiar ajustes críticos de hardware, Fluxi te mostrará un cuadro de confirmación. Nada sucede sin tu "Sí".

🐛 Errores y Bugs Arreglados
Error de Hilo (NameError: is_generative):

Bug: En versiones anteriores, al intentar usar la IA, el programa a veces se cerraba o lanzaba un error porque la variable is_generative no estaba definida en el lugar correcto del código.

Solución: Se definió y estructuró correctamente dentro del hilo de procesamiento para que la IA siempre sepa qué modo usar.

Congelamiento de Ventana (GUI Freeze):

Bug: Al pedirle algo complejo a la IA, la ventana se quedaba "trabada" y no podías moverla hasta que la IA terminara de responder.

Solución: Implementamos un sistema de hilos (threading) más robusto. Ahora la interfaz siempre responde mientras la IA trabaja "detrás de escena".

Error de Inicialización de Audio:

Bug: Si intentabas cambiar el volumen varias veces, el sistema de audio de Windows podía dar un error de "COM" (comunicación).

Solución: Añadimos comtypes.CoInitialize() y Uninitialize(). Esto asegura que la conexión con los altavoces se abra y cierre correctamente cada vez.

Persistencia de Datos:

Bug: A veces los sitios bloqueados o recordatorios se borraban al cerrar.

Solución: Se mejoraron los bloques try-except al cargar los archivos .json para evitar que un archivo corrupto rompa todo el asistente.

# Documentación Oficial - Asistente Copiloto Fluxi

**Versión Actual del Código:** **1.0.2 (Última Consolidada con Auto-Descripción y Control de Escritura)**
**Modelo de IA:** Google Gemini 2.5 Flash

---

## 1. ¿Qué es Fluxi y Cómo te Ayuda? 🤖

**Fluxi** es un **Asistente Copiloto de PC** diseñado para interactuar con tu sistema operativo, aumentar tu productividad y proporcionar un entorno de trabajo más seguro y contextualizado, todo a través de comandos de texto, voz y análisis visual.

### **Capacidades Generales**

| Característica | Descripción |
| :--- | :--- |
| **🧠 Inteligencia General** | Responde preguntas, resume textos, traduce, genera contenido creativo y código, impulsado por Gemini 2.5 Flash. |
| **🖼️ Análisis Contextual** | Utiliza capturas de pantalla para analizar visualmente tu entorno (ventanas, aplicaciones, mensajes de error) y dar una respuesta basada en lo que ves. |
| **💻 Control de PC Directo** | Ejecuta comandos de sistema (como volumen, bloqueo, etc.) directamente, previa autorización. |
| **🛡️ Modo Piloto Proactivo** | Monitoriza tu pantalla en segundo plano para detectar errores de sistema, avisarte de sitios web peligrosos o reconocer si estás en un juego o app sensible. |
| **📝 Interacción Avanzada** | Permite adjuntar archivos de texto/código para que la IA los analice y te da la opción de escribir/pegar respuestas directamente en tu cursor. |

---

## 2. Comandos de Control de PC Ejecutables 🚀

Estos comandos son acciones directas en el sistema operativo que Fluxi puede ejecutar después de que el usuario los autorice.

| Comando | Acción del Sistema Operativo | Notas / Uso |
| :--- | :--- | :--- |
| **`bloquear pc`** | Bloquea inmediatamente la sesión de Windows. | Seguridad instantánea. |
| **`captura de pantalla`** | Realiza una captura y la guarda localmente (`screenshot_fluxi.png`). | Para documentar o analizar. |
| **`sube/baja volumen`** | Ajusta el volumen principal del sistema. | Requiere `pycaw`. |
| **`silencia pc`** | Pone el PC en estado de silencio (mute). | Requiere `pycaw`. |
| **`cerrar ventana`** | Envía la combinación de teclas `Alt+F4`. | Cierra la ventana activa. |
| **`maximizar/minimizar ventana`** | Envía `Win+Flecha Arriba/Abajo`. | Control de ventanas. |
| **`abrir explorador`** | Ejecuta el Explorador de archivos de Windows. | Rápido acceso a carpetas. |
| **`abrir configuración`** | Abre la Configuración de Windows. | Acceso a `ms-settings:`. |
| **`reproducir/pausar`** | Envía el comando de reproducción/pausa multimedia. | Controla reproductores activos. |
| **`siguiente/anterior`** | Envía el comando de pista siguiente/anterior. | Control de medios. |
| **`copiar/pegar/seleccionar todo`** | Envía los comandos `Ctrl+C`, `Ctrl+V`, `Ctrl+A`. | Automatización de tareas de texto. |
| **`sube/baja brillo`** | (Simulación) Notifica el intento de controlar el brillo. | Control del brillo (sujeto a librerías de sistema). |

### Comandos Internos de Auto-Descripción

* **`qué puedes hacer` / `qué sabes hacer` / `describe tus funciones`**: Activa el comando de **Auto-Descripción** (`_list_capabilities`) para generar esta información directamente sin consultar a Gemini.

---

## 3. Contenido Generado y Archivos Salida 📄

Fluxi maneja la generación de texto y código con un enfoque en la interactividad y la persistencia.

### Tipos de Generación

| Tipo de Salida | Mecanismo | Condiciones para Preguntar |
| :--- | :--- | :--- |
| **📝 Texto Largo/Código** | **Pregunta al usuario** si desea pegarlo en el cursor activo. | La respuesta es **código** (contiene ` ``` `), o es un **texto extenso** (más de 40 palabras), o si se usó el comando **`escribe`**. |
| **💾 Archivo Local (`.md`, `.py`, `.txt`)** | Pide al usuario una ubicación para guardar el contenido generado. | Se detecta una intención explícita en el prompt como **`genera archivo`** o **`crea un script`**. |

**Modo de Escritura:** En la configuración de Fluxi, puedes elegir cómo se inserta el texto:
* **Copiar/Pegar (Rápido):** Utiliza `Ctrl+V` (Recomendado).
* **Escribir Letra por Letra (Simulación):** Escribe usando `pyautogui.write` (Lento, simula la escritura humana).

---

## 4. Opciones de Seguridad y Privacidad 🛡️

* **Modo Incógnito:** Activa la privacidad total. Desactiva el registro de actividad (`output_text`) y aplica una transparencia a la ventana para evitar ser capturada por software de grabación (`win32con.WS_EX_LAYERED`).
* **Anclaje de Ventana:** Mantiene la ventana de Fluxi siempre visible (`wm_attributes("-topmost", True)`).
* **Lista Negra de Sitios:** Permite bloquear dominios peligrosos o distractores (`fluxi bloquea esta web ejemplo.com`). Fluxi redirigirá al usuario automáticamente si intenta acceder a una URL bloqueada.
* **Chequeo de URLs Peligrosas:** Utiliza una lista de palabras clave internas (`phishing`, `malware`, `torrent`, etc.) para cerrar proactivamente pestañas de navegador de riesgo.

---

## 5. Descarga y Dependencias 📦

Fluxi es un proyecto de código cerrado.

**Ubicación Donde Puedes Descargar y Testear (Versión 1.0.2):**

Versión 1.0.2 se encuentra disponible para su revisión e implementación.

* **Repositorio Oficial:** [Fluxi](https://fluxionics.github.io/Asistente-Virtual/)

**Instalación :**
| INTRUCIONES DE INTALACION |
| :--- |
|*Puedes descargar el archivo .rar*|
|*descomprimir el archivo .rar*|
|*abrir el acesso derecto del archivo .env colorcar su apikey*|
|*y ejecutar la archivo Asistente.exe*|

**Donde Obtener La Apikey :**
Puedes obtenerla desde esta web 
[Aqui](https://aistudio.google.com/apikey)

Completamente gratis

**Instalación de Dependencias:**

Para una funcionalidad completa (incluyendo control de volumen y voz), se requieren los siguientes paquetes para funcionalidad y recreacion:

```bash
pip install customtkinter google-genai python-dotenv pyautogui pillow pyperclip pyttsx3 comtypes pycaw
