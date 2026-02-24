# fluxi_asistente_final.py
# ASISTENTE FLUXI - CÓDIGO FINAL CONSOLIDADO (v22 - EJECUCIÓN DIRECTA DE COMANDOS CORREGIDA)

import os
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog 
from dotenv import load_dotenv, set_key
import google.generativeai as genai
from google.genai.errors import APIError 
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import subprocess
import time
import re
import customtkinter as ctk
import pyautogui 
from PIL import Image, ImageGrab
import json 
import pyperclip 
import threading 
import io
import webbrowser 
import screen_brightness_control as sbc
import ctypes

# Opcionales para PC Control
try:
    import psutil
    PSUTIL_DISPONIBLE = True
except ImportError:
    PSUTIL_DISPONIBLE = False

# Importar win32api para funcionalidades de ventana de bajo nivel (Anclaje / Transparencia)
try:
    import win32gui as win32
    import win32con
    WIN32_DISPONIBLE = True
except ImportError:
    WIN32_DISPONIBLE = False
    
# Librerías de control de volumen
import comtypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    VOLUMEN_DISPONIBLE = True
except ImportError:
    VOLUMEN_DISPONIBLE = False
    
# Librerías de voz
try:
    import pyttsx3 
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    VOZ_DISPONIBLE = True
except Exception:
    VOZ_DISPONIBLE = False


# --- Configuración de Archivos y Rutas ---
CONFIG_FILE = "config.json"
DOTENV_FILE = ".env" 
BLOCKED_WEBSITES_FILE = "blocked_websites.json"
REMINDERS_FILE = "reminders.json" 
LOGO_ICON_PATH = "Logo.ico" 

# --- Constantes del Asistente ---
REDIRECT_URL = "https://fluxionics.github.io/Asistente-Virtual/Web.html" 
MIN_CAPTURE_INTERVAL = 10 
CAPTURE_CHECK_DIVISOR = 3 
# Color Clave para Anti-Grabación (Negro)
COLOR_KEY = 0x000000 
# Comandos de sistema comunes a detectar
SYSTEM_COMMAND_KEYWORDS = ["mkdir", "rmdir", "cd", "start", "ping", "ipconfig", "netsh", "tasklist", "taskkill", "git", "python", "pip", "npm", "choco", "wsl", "reg", "shutdown"]


# --- Lista Negra de Seguridad ---
DANGEROUS_KEYWORDS = ["phishing", "malware", "virus", "descargar-gratis", "apuestas", "torrent", "sexo", "porn", "xxx"]
SENSITIVE_APPS = ["whatsapp", "telegram", "outlook", "discord", "signal", "teams", "slack"] 
GAME_KEYWORDS = ["roblox", "minecraft", "steam", "valorant", "league of legends", "fortnite", "elden ring"] 


# ----------------------------------------------------------------------------------
# --- FUNCIONES DE PERSISTENCIA Y CONFIGURACIÓN ---
# ----------------------------------------------------------------------------------

def ajustar_brillo_real(self, porcentaje):
    try:
        sbc.set_brightness(porcentaje)
        self.log(f"Brillo ajustado al {porcentaje}%")
    except Exception as e:
        self.log(f"Error al acceder al monitor: {e}")

def ajustar_volumen_real(self, nivel):
    # nivel debe ser de 0.0 a 1.0
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(nivel / 100, None)
    self.log(f"Volumen real al {nivel}%")

def escribir_texto_real(self, texto):
    # Simula pulsaciones de teclas físicas
    pyautogui.write(texto, interval=0.05)

   # ------------------~.-------------------------------------------------------------------

def load_config():
    """Carga la configuración desde config.json o usa valores por defecto."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            # Asegurar valores por defecto si faltan
            if data.get("response_mode") == "Solo Texto": data["response_mode"] = "Solo Mensaje"
            if "incognito_mode" not in data: data["incognito_mode"] = False
            if "write_mode" not in data: data["write_mode"] = "Copiar/Pegar"
            if "always_on_top" not in data: data["always_on_top"] = False
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"theme": "Dark", "response_mode": "Solo Mensaje", "incognito_mode": False, "write_mode": "Copiar/Pegar", "always_on_top": False}

def save_config(config_data):
    """Guarda la configuración actual en config.json."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Error al guardar la configuración: {e}")

def load_blocked_websites():
    """Carga la lista de URLs bloqueadas desde blocked_websites.json."""
    try:
        with open(BLOCKED_WEBSITES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_blocked_websites(urls):
    """Guarda la lista de URLs bloqueadas en blocked_websites.json."""
    try:
        with open(BLOCKED_WEBSITES_FILE, 'w') as f:
            json.dump(urls, f, indent=4)
    except Exception as e:
        print(f"Error al guardar sitios bloqueados: {e}")

def load_reminders():
    """Carga la lista de recordatorios."""
    try:
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_reminders(reminders):
    """Guarda la lista de recordatorios."""
    try:
        with open(REMINDERS_FILE, 'w') as f:
            json.dump(reminders, f, indent=4)
    except Exception as e:
        print(f"Error al guardar recordatorios: {e}")


# ----------------------------------------------------------------------------------
# --- INICIALIZACIÓN DE GEMINI Y GESTIÓN DE API KEY ---
# ----------------------------------------------------------------------------------
def initialize_gemini(root_window=None):
    """Carga la API key, la pide si falta, y configura Gemini."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        if root_window:
            root_window.withdraw() 
        
        print("GEMINI_API_KEY no encontrada. Solicitando al usuario.")
        
        api_key = simpledialog.askstring(
            "🔑 API Key de Gemini",
            "Introduce tu GEMINI_API_KEY para habilitar la IA. Si cancelas, el asistente solo usará comandos de PC.",
            parent=root_window
        )
        
        if root_window:
            root_window.deiconify() 

        if api_key:
            try:
                if not os.path.exists(DOTENV_FILE):
                     with open(DOTENV_FILE, 'w') as f:
                         f.write("# Archivo de configuración de variables de entorno\n")
                         
                set_key(DOTENV_FILE, "GEMINI_API_KEY", api_key)
                os.environ["GEMINI_API_KEY"] = api_key 
                print("Clave API guardada en .env.")
            except Exception as e:
                print(f"Advertencia: No se pudo guardar la clave en .env: {e}")

    try:
        if not api_key: raise ValueError("Clave GEMINI_API_KEY no disponible.")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    except (ValueError, Exception) as e:
        print(f"Error al inicializar Gemini: {e}")
        return None 


# ----------------------------------------------------------------------------------
# --- CLASE PRINCIPAL DE LA APLICACIÓN (GUI) ---
# ----------------------------------------------------------------------------------
class AsistenteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Configuración y Carga de Preferencias 
        self.config_data = load_config()
        self.config_theme = ctk.StringVar(value=self.config_data.get("theme", "Dark"))
        self.config_response_mode = ctk.StringVar(value=self.config_data.get("response_mode", "Solo Mensaje")) 
        self.config_write_mode = ctk.StringVar(value=self.config_data.get("write_mode", "Copiar/Pegar")) 
        self.incognito_mode_active = self.config_data.get("incognito_mode", False)
        self.always_on_top_active = self.config_data.get("always_on_top", False) 

        # Variables de control
        self.pilot_mode_active = False 
        self.stop_voice_thread = threading.Event() 
        self.stop_pilot_thread = threading.Event() 
        self.last_screenshot = None 
        self.uploaded_file_content = None
        self.uploaded_file_name = None
        self._last_pilot_game_ask = 0 
        self.reminders = load_reminders() 
        self.pilot_check_count = 0 

        # Configuración inicial de la ventana
        self.title("🤖 Asistente Copiloto Fluxi")
        self.geometry("850x700") 
        ctk.set_default_color_theme("green")
        
        # Inicializar Gemini (puede mostrar el diálogo)
        self.model = initialize_gemini(self)
        
        # Aplicar tema antes de crear widgets
        if self.incognito_mode_active:
            # Forzar Dark si está en Incógnito para el Anti-Grabación
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode(self.config_theme.get())
        
        # Inicializar el mapa de comandos
        self.COMANDOS_PC_SISTEMA = {
            "brillo": 'control_brightness', "volumen": 'control_volume', "compartir": 'control_sharing', 
            "apagar": 'shutdown_pc', "reiniciar": 'reboot_pc', "bloquear": 'lock_pc', "captura": 'screenshot',
            "copiar": 'copy_text', "pegar": 'paste_text', "seleccionar todo": 'select_all',
            "cerrar ventana": 'close_window', "maximizar ventana": 'maximize_window',
            "minimizar ventana": 'minimize_window', "abrir explorador": 'open_explorer',
            "abrir configuración": 'open_settings', "reproducir": 'play_media',
            "pausar": 'pause_media', "siguiente": 'next_media', "anterior": 'previous_media',
            "búsqueda local": 'search_local', "mueve archivo": 'simulate_file_management', "abre carpeta": 'simulate_file_management',
            "calcula": 'simulate_math_conversion', "traduce": 'simulate_translation', "clima": 'simulate_weather',
            "noticias": 'simulate_news', "historial": 'simulate_command_history', "monitor sistema": 'simulate_system_monitor',
            "definición": 'simulate_definition', "generar contraseña": 'simulate_password_gen'
        }
        
        if os.path.exists(LOGO_ICON_PATH):
            try: self.iconbitmap(LOGO_ICON_PATH)
            except tk.TclError: pass 
        
        self.create_widgets()
        
        # Aplicar estado de anclaje y transparencia al inicio
        self.set_always_on_top(self.always_on_top_active)
        self.set_incognito_visuals(self.incognito_mode_active) 
        
        # --- Hilos y Comprobaciones ---
        self.schedule_capture() 
        self.protocol("WM_DELETE_WINDOW", self.hide_window) 
        
        self.update_log_state() 
        if self.model:
            self.update_status("Asistente Fluxi listo. El sistema está completamente operativo.")
        else:
            self.update_status("🚨 Advertencia: Gemini NO está disponible. Solo comandos locales de PC.")
            
        save_config(self.config_data)

    def create_widgets(self):
        
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        left_panel = ctk.CTkFrame(main_frame, width=550)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        
        right_panel = ctk.CTkFrame(main_frame, width=250)
        right_panel.pack(side="right", fill="both", expand=True)

        # ---------------- Panel Izquierdo ----------------
        title_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        title_frame.pack(fill="x", pady=(15, 5), padx=10)
        
        ctk.CTkLabel(title_frame, text="ASISTENTE DE PC | FLUXI", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        self.btn_pin = ctk.CTkButton(title_frame, text="📌 Anclar", width=80, height=30, 
                                      command=self.toggle_always_on_top, fg_color="#4CAF50" if self.always_on_top_active else "gray", hover_color="#4CAF50")
        self.btn_pin.pack(side="right", padx=(5, 5))
        
        self.btn_gear = ctk.CTkButton(title_frame, text="⚙️", width=30, height=30, 
                                      command=self.open_settings_window, fg_color="transparent", hover_color="#3366ff")
        self.btn_gear.pack(side="right")
        
        input_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        input_frame.pack(padx=10, pady=10, fill="x")
        
        self.btn_upload = ctk.CTkButton(input_frame, text="📤 Subir Archivo", width=120, command=self.upload_file)
        self.btn_upload.pack(side="left", padx=(0, 5), pady=10)
        
        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text="Escribe un comando o pregunta...", width=280)
        self.input_entry.pack(side="left", padx=(5, 5), pady=10, fill="x", expand=True)
        self.input_entry.bind('<Return>', lambda e: self.procesar_comando_event())
        
        btn_enviar = ctk.CTkButton(input_frame, text="Enviar", command=self.procesar_comando_event, width=100)
        btn_enviar.pack(side="right", padx=(5, 0), pady=10)
        
        self.file_status_label = ctk.CTkLabel(left_panel, text="No hay archivo adjunto.", anchor="w", text_color="gray")
        self.file_status_label.pack(padx=10, fill="x")
        
        pilot_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        pilot_frame.pack(padx=10, pady=(0, 10), fill="x")
        
        ctk.CTkLabel(pilot_frame, text="Modo Piloto (Detección Proactiva)").pack(side="left")
        self.pilot_switch = ctk.CTkSwitch(pilot_frame, text="", command=self.toggle_pilot_mode, width=50)
        self.pilot_switch.pack(side="right")
        
        if self.pilot_mode_active: 
            self.pilot_switch.select()

        ctk.CTkLabel(left_panel, text="Registro de Actividad", anchor="w").pack(padx=10, fill="x")
        self.output_text = ctk.CTkTextbox(left_panel, height=250, width=530)
        self.output_text.pack(padx=10, pady=(5, 10), fill="both", expand=True)
        
        # ---------------- Panel Derecho (VISTA CONTEXTUAL y TERMINAL) ----------------
        ctk.CTkLabel(right_panel, text="VISTA CONTEXTUAL (Análisis)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        self.img_placeholder = ctk.CTkImage(light_image=Image.new('RGB', (200, 150), color='gray'), 
                                            dark_image=Image.new('RGB', (200, 150), color='gray'), size=(250, 180))
        self.screen_preview = ctk.CTkLabel(right_panel, image=self.img_placeholder, text="")
        self.screen_preview.pack(pady=(0, 10))
        self.btn_analizar = ctk.CTkButton(right_panel, text="Analizar Pantalla Ahora (Gemini)", 
                                          command=lambda: self.trigger_context_analysis(), fg_color="#3366ff", 
                                          state="normal" if self.model else "disabled")
        self.btn_analizar.pack(pady=5)
        self.last_capture_label = ctk.CTkLabel(right_panel, text="Sin captura para análisis.")
        self.last_capture_label.pack(pady=5)
        
        ctk.CTkLabel(right_panel, text="TERMINAL DE COMANDOS", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        self.terminal_output = ctk.CTkTextbox(right_panel, height=180, width=250, state="disabled", fg_color="black")
        self.terminal_output.pack(padx=10, pady=(0, 10), fill="both", expand=True)

        self.terminal_output.tag_config("command_tag", foreground="#FFFF00") 
        self.terminal_output.tag_config("output_tag", foreground="#00FF00")  
        self.terminal_output.tag_config("error_tag", foreground="#FF0000")   
        # ---------------- FIN PANEL DERECHO ----------------
        
        self.status_label = ctk.CTkLabel(self, text="Asistente Listo.", anchor="w", fg_color="gray", text_color="white")
        self.status_label.pack(side="bottom", fill="x", padx=0, pady=0)


    # --- FUNCIONES CORE (speak, update_status, write_to_cursor, log_terminal) ---

    def speak(self, text):
        if self.config_response_mode.get() in ["Solo Voz", "Ambos"] and VOZ_DISPONIBLE:
            try:
                self.stop_voice_thread.set()
                self.stop_voice_thread = threading.Event()
                threading.Thread(target=self._run_voice_thread, args=(text, self.stop_voice_thread)).start()
            except Exception as e:
                print(f"Error en pyttsx3: {e}")

    def _run_voice_thread(self, text, stop_event):
        try:
            clean_text = re.sub(r'[\*\`\#]', '', text) 
            engine.say(clean_text)
            engine.runAndWait()
        except Exception:
            pass 

    def update_log_state(self):
        """Ajusta el estado del área de texto (historial) basado en el modo incógnito."""
        if self.incognito_mode_active:
            self.output_text.configure(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("end", "[Modo Incógnito Activo. Sin Registro de Actividad.]")
            self.output_text.configure(state="disabled")
        else:
            self.output_text.configure(state="normal")
            
    # CORRECCIÓN V21: Asegura que el tema sea Dark si Incógnito está activo, para la clave de color
    def set_incognito_visuals(self, is_incognito):
        """Controla la transparencia/visibilidad de la ventana (Anti-Grabación)."""
        
        if is_incognito:
            ctk.set_appearance_mode("Dark") # Forzar Dark
        else:
            ctk.set_appearance_mode(self.config_theme.get())

        if not WIN32_DISPONIBLE: return

        hwnd = self.winfo_id()
        
        try:
            extended_style = win32.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            
            if is_incognito:
                # 1. Asegurar WS_EX_LAYERED
                if not (extended_style & win32con.WS_EX_LAYERED):
                    win32.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style | win32con.WS_EX_LAYERED)
                
                # 2. Aplicar capa de Anti-Grabación: Opacidad baja (254) Y Color Key (0x000000)
                win32.SetLayeredWindowAttributes(
                    hwnd, 
                    COLOR_KEY, 
                    254,       
                    win32con.LWA_ALPHA | win32con.LWA_COLORKEY 
                ) 
                win32.UpdateWindow(hwnd) 

            else:
                # 1. Desactivar capa de Anti-Grabación
                if (extended_style & win32con.WS_EX_LAYERED):
                    win32.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA) 
                    win32.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style & ~win32con.WS_EX_LAYERED)
                    
            win32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)
            
        except Exception as e:
            print(f"ERROR WIN32 en set_incognito_visuals: {e}")
            self.update_status("⚠️ Error en funciones de transparencia (Modo Incógnito Visual falló).")
    
    def update_status(self, mensaje):
        """Actualiza el estado y el log, respeta el modo incógnito."""
        if hasattr(self, 'status_label') and hasattr(self, 'output_text'):
            self.status_label.configure(text=mensaje)
            
            if not self.incognito_mode_active:
                self.output_text.configure(state="normal")
                self.output_text.insert("end", f"\n[PC] {mensaje}")
                self.output_text.see("end")
                self.output_text.configure(state="disabled")
            
            self.update()
            
            if self.config_response_mode.get() != "Solo Mensaje" and not mensaje.startswith("⚠️ ¡PREPÁRATE!") and not mensaje.startswith("🚨 ERROR DETECTADO"):
                self.speak(mensaje) 
                
    def log_terminal(self, command, output=None, error=None):
        self.after(0, lambda: self._log_terminal_ui(command, output, error))

    def _log_terminal_ui(self, command, output, error):
        if not hasattr(self, 'terminal_output'): return
        
        self.terminal_output.configure(state="normal")
        
        if not self.terminal_output.get("1.0", "end-1c").strip():
            self.terminal_output.insert("end", "$ ", "command_tag")
        else:
            self.terminal_output.insert("end", "\n$ ", "command_tag")

        self.terminal_output.insert("end", f"{command}\n", "command_tag")
        
        if output:
            self.terminal_output.insert("end", f"{output}\n", "output_tag")
        if error:
            self.terminal_output.insert("end", f"ERROR: {error}\n", "error_tag")

        self.terminal_output.see("end")
        self.terminal_output.configure(state="disabled")

    def write_to_cursor(self, text_to_write):
        """Inserta texto en el cursor activo según el modo de escritura configurado."""
        self.update_status("⚠️ ¡PREPÁRATE! Fluxi insertará la respuesta en 3 segundos. Coloca el cursor.")
        self.speak("Tienes 3 segundos para colocar el cursor.")
        
        time.sleep(3) 
        
        write_mode = self.config_write_mode.get()

        if write_mode == "Copiar/Pegar":
            self.update_status("🤖 Pegando...")
            pyperclip.copy(text_to_write)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5) 
            self.update_status("✅ Pegado completado.")
        
        elif write_mode == "Escribir Letra por Letra":
            self.update_status("🤖 Escribiendo línea por línea... (Modo Lento)")
            
            lines = text_to_write.split('\n')
            for line in lines:
                pyautogui.write(line.rstrip(), interval=0.1) # Intervalo más lento
                pyautogui.press('enter') 
                time.sleep(0.2) # Pausa más larga entre líneas
                
            self.update_status("✅ Escritura completada.")
        
        self.speak("El contenido ha sido insertado.")
        
    def toggle_always_on_top(self):
        self.always_on_top_active = not self.always_on_top_active
        self.set_always_on_top(self.always_on_top_active)
        
        self.config_data["always_on_top"] = self.always_on_top_active
        save_config(self.config_data)

    def set_always_on_top(self, active):
        self.wm_attributes("-topmost", active)
        if active:
            self.btn_pin.configure(text="📌 Anclado", fg_color="#4CAF50")
            self.update_status("Ventana ANCLADA (Siempre visible).")
        else:
            self.btn_pin.configure(text="📌 Anclar", fg_color="gray")
            self.update_status("Ventana DESANCLADA.")

    # --- FUNCIONES DE COMANDOS Y SUBIDA DE ARCHIVOS ---
    
    def generate_file_with_content(self, filename, content):
        """Genera un archivo local con el contenido proporcionado."""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=filename,
                title="Guardar archivo generado por Fluxi"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.update_status(f"✅ Archivo '{os.path.basename(file_path)}' generado y guardado exitosamente.")
                self.speak("Archivo generado.")
            else:
                self.update_status("❌ Creación de archivo cancelada por el usuario.")

        except Exception as e:
            self.update_status(f"⚠️ Error al generar el archivo: {e}")
            self.log_terminal("Generar Archivo", error=str(e))
    
    # FUNCIÓN CLAVE: EJECUCIÓN REAL DE COMANDOS DE SISTEMA
    def execute_command_in_terminal(self, command_to_execute):
        """Ejecuta un comando de sistema y registra el resultado."""
        self.update_status(f"⚠️ Ejecutando comando de sistema: '{command_to_execute}'...")
        self.log_terminal(command_to_execute)
        
        # Reemplazar %username% por el nombre de usuario real para comandos de CMD/Shell
        command_to_execute = command_to_execute.replace('%username%', os.getlogin())

        try:
            # Usar subprocess.run para ejecución segura y captura de salida real
            result = subprocess.run(
                command_to_execute, 
                shell=True,
                capture_output=True, 
                text=True, 
                timeout=10,
                check=False # No lanzar excepción en caso de error de código de retorno
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if result.returncode == 0:
                self.update_status(f"✅ Comando ejecutado con éxito. Resultado en Terminal.")
                self.log_terminal(command_to_execute, output=output)
            elif error:
                self.update_status(f"❌ Error al ejecutar el comando. Código de salida: {result.returncode}")
                self.log_terminal(command_to_execute, output=output, error=error)
            else:
                # Caso donde el comando falla sin stderr pero con código de error
                self.update_status(f"❌ Comando fallido. Código de salida: {result.returncode}")
                self.log_terminal(command_to_execute, output=output if output else "No se produjo salida.", error=f"Código de salida: {result.returncode}")
                
        except FileNotFoundError:
            self.update_status(f"❌ Error: El comando o programa '{command_to_execute.split()[0]}' no se encontró en el PATH.")
            self.log_terminal(command_to_execute, error="Comando no encontrado (FileNotFoundError).")
        except subprocess.TimeoutExpired:
            self.update_status("❌ Error: La ejecución del comando ha excedido el tiempo límite (10s).")
            self.log_terminal(command_to_execute, error="Tiempo límite de ejecución excedido.")
        except Exception as e:
            self.update_status(f"❌ Error desconocido durante la ejecución: {e}")
            self.log_terminal(command_to_execute, error=str(e))


    def upload_file(self):
        """Abre un diálogo para seleccionar un archivo y almacena su contenido."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo para análisis",
            filetypes=[("Archivos de Texto/Código", "*.txt *.py *.js *.html *.css *.json"), ("Todos los archivos", "*.*")]
        )
        if file_path:
            try:
                # Limitar el tamaño de lectura para evitar sobrecarga de la API
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.uploaded_file_content = f.read(50000) # Límite de 50KB
                self.uploaded_file_name = os.path.basename(file_path)
                self.file_status_label.configure(text=f"✅ Archivo adjunto: {self.uploaded_file_name}", text_color="#4CAF50")
                self.update_status(f"Archivo '{self.uploaded_file_name}' cargado para el próximo comando.")
            except Exception as e:
                self.update_status(f"⚠️ Error al leer el archivo: {e}")
                self.uploaded_file_content = None
                self.uploaded_file_name = None
                self.file_status_label.configure(text="No hay archivo adjunto.", text_color="gray")

    def procesar_comando_event(self, event=None):
        
        user_input = self.input_entry.get().strip()
        source = "[USER]"

        if not user_input: return
        
        self.input_entry.delete(0, tk.END)
        
        if not self.incognito_mode_active:
            self.output_text.configure(state="normal")
            self.output_text.insert("end", f"\n{source} {user_input}")
            self.output_text.configure(state="disabled")
            
        threading.Thread(target=self._procesar_comando_logic, args=(user_input,)).start()

    # --- FUNCIONES PARA AUTO-DESCRIPCIÓN Y COMANDOS INTERNOS ---
    
    def _add_reminder(self, reminder_text):
        """Añade un recordatorio simple a la lista."""
        self.reminders.append(reminder_text)
        save_reminders(self.reminders)
        self.update_status(f"✅ Recordatorio añadido: '{reminder_text[:50]}...'")
        self.speak("Recordatorio guardado.")

    def _list_reminders(self):
        """Lista todos los recordatorios guardados."""
        if not self.reminders:
            self.update_status("🔔 No tienes recordatorios activos.")
            self.speak("No tienes recordatorios activos.")
            return

        reminder_list = "\n".join([f"- {i+1}. {r}" for i, r in enumerate(self.reminders)])
        if not self.incognito_mode_active:
             self.output_text.configure(state="normal")
             self.output_text.insert("end", f"\n[RECORDATORIOS]\n{reminder_list}")
             self.output_text.see("end")
             self.output_text.configure(state="disabled")
             
        self.update_status(f"🔔 Tienes {len(self.reminders)} recordatorios activos.")
        self.speak(f"Tienes {len(self.reminders)} recordatorios activos.")

    def _block_application(self, app_name):
        """Busca y termina todos los procesos que coincidan con el nombre de la aplicación."""
        if not PSUTIL_DISPONIBLE:
             self.update_status("⚠️ psutil no está instalado. No se puede bloquear la aplicación.")
             return
             
        try:
            app_name_lower = app_name.lower()
            terminated_count = 0
            
            for proc in psutil.process_iter(['name']):
                if app_name_lower in proc.info['name'].lower():
                    proc.terminate()
                    terminated_count += 1
            
            if terminated_count > 0:
                self.update_status(f"🚫 Aplicación Bloqueada/Cerrada: Se terminaron {terminated_count} procesos de '{app_name}'.")
                self.log_terminal("Bloqueo App", output=f"{terminated_count} procesos terminados para '{app_name}'.")
                self.speak(f"La aplicación {app_name} ha sido cerrada.")
            else:
                self.update_status(f"✅ La aplicación '{app_name}' no se encontró activa.")

        except Exception as e:
            self.update_status(f"⚠️ Error al intentar bloquear la aplicación: {e}")
            self.log_terminal("Bloqueo App", error=str(e))
    
    def _list_capabilities(self):
        """Genera una lista exhaustiva de las capacidades propias del asistente Fluxi (ACTUALIZADA)."""
        
        cap_list = [
            "🤖 **Capacidades Generales (Gemini 2.5 Flash):**",
            "   - Responder preguntas, resumir textos, generar código y contenido creativo.",
            "   - **Ejecutar comandos de sistema** (CMD/Powershell) con previa autorización (ej. `mkdir`).",
            "   - Analizar capturas de pantalla para dar contexto (análisis contextual y Pilot Mode).",
            "   - Analizar archivos de texto/código adjuntos.",
            "💻 **Control de PC y Automatización (Implementado o Simulado):**",
            "   - **Control de Sistema:** Apagar/Reiniciar (Sim.), Bloqueo de Pantalla, Control de Volumen (si pycaw).",
            "   - **Gestión Multimedia:** Reproducir/Pausar, Siguiente/Anterior canción.",
            "   - **Gestión de Ventanas:** Cerrar, Maximizar, Minimizar.",
            "   - **Comandos de Acceso:** Abrir Explorador, Abrir Configuración, Abrir URLs, Búsqueda Local (Sim.).",
            "   - **Gestión de Tareas:** Recordatorios/Alarmas (Base), Control de Procesos (Sim.).",
            "   - **Seguridad Web:** Bloqueo y Desbloqueo de sitios web (por GUI y comando).",
            "   - **Privacidad:** Modo Incógnito (Anti-Grabación) y Anclaje de ventana (Always On Top).",
            "🌐 **Servicios Simulación:**",
            "   - Búsqueda Web, Clima, Noticias, Traducción, Definiciones, Generación de Contraseñas, Cálculos.",
        ]
        
        return "\n".join(cap_list)

    def _handle_internal_command(self, user_input_lower):
        """Maneja comandos que no necesitan la IA (Auto-descripción)."""
        if any(q in user_input_lower for q in ["que puedes hacer", "que sabes hacer", "cuales son tus comandos", "describe tus funciones", "que haces"]):
            cap_text = self._list_capabilities()
            self.update_status("✅ Fluxi responde sobre sí mismo.")
            self.speak("Mis capacidades principales son:")
            
            if not self.incognito_mode_active:
                self.output_text.configure(state="normal")
                self.output_text.insert("end", f"\n[AUTO-DESCRIPCIÓN]\n{cap_text}")
                self.output_text.see("end")
                self.output_text.configure(state="disabled")
            
            return True
        return False
    
    def _procesar_comando_logic(self, user_input):
        user_input_lower = user_input.lower()
        comando_ejecutado = False
        
        # --- 0. Gestión de Recordatorios y Notas ---
        if any(keyword in user_input_lower for keyword in ["recuerdame", "añade recordatorio", "guarda esta nota"]):
            comando_ejecutado = True
            match = re.search(r'(recuerdame|añade recordatorio|guarda esta nota|crea una nota|nota rapida)\s+(.*)', user_input_lower)
            if match and match.group(2).strip():
                self.after(0, lambda: self._add_reminder(match.group(2).strip()))
            else:
                self.update_status("⚠️ No especificaste el contenido del recordatorio.")
            return

        elif any(keyword in user_input_lower for keyword in ["lista recordatorios", "muestrame mis notas", "que tengo pendiente"]):
            comando_ejecutado = True
            self.after(0, self._list_reminders)
            return
            
        # --- 1. Bloqueo de Aplicaciones (Control de Procesos) ---
        if "bloquea la aplicacion" in user_input_lower or "cierra el programa" in user_input_lower or "termina el proceso" in user_input_lower:
            comando_ejecutado = True
            match = re.search(r'(bloquea la aplicacion|cierra el programa|termina el proceso)\s+(.*)', user_input_lower)
            if match and match.group(2).strip():
                app_name = match.group(2).strip().split()[0]
                self.after(0, lambda: self._block_application(app_name))
            else:
                self.update_status("⚠️ No especificaste el nombre de la aplicación a bloquear/cerrar.")
            return

        # --- 2. Simulación de Servicios ---
        if any(cmd in user_input_lower for cmd in ["dame el clima", "noticias", "traduce", "calendario", "agenda", "enviar email", "dictame", "generar contraseña", "temporizador", "calculadora cientifica", "conversor de divisas"]):
            comando_ejecutado = True
            function_name = user_input_lower.split()[0]
            self.update_status(f"🌐 Simulación: Consultando '{function_name}'. (Requiere integración de APIs/Módulos externos)")
            self.speak("Ejecutando simulación de servicio.")
            return

        # --- 3. Simulación de Gestión de Archivos y Automatización ---
        if any(cmd in user_input_lower for cmd in ["abre archivo", "mueve archivo", "copia archivo", "elimina archivo", "automatiza", "ejecutar script", "historial de comandos"]):
            comando_ejecutado = True
            self.update_status("📂 Simulación: Activando gestión/automatización de tareas. (Requiere módulos avanzados de sistema)")
            self.speak("Ejecutando simulación de tareas de sistema.")
            return
            
        # --- 4. Comandos de Bloqueo y Desbloqueo Web ---
        if user_input_lower.startswith("fluxi quiero bloquear a esta web") or user_input_lower.startswith("fluxi bloquea esta web"):
            comando_ejecutado = True
            url_match = re.search(r'([a-zA-Z0-9-]+\.(com|net|org|io|dev|es|mx|cl|ar|co|biz|info)[^\s]*)', user_input_lower)
            if url_match:
                self.after(0, lambda: self.block_website(url_match.group(0)))
            else:
                self.update_status("⚠️ No se encontró una URL válida para bloquear.")
            return

        elif user_input_lower.startswith("fluxi desbloquea esta web") or "desbloqueame" in user_input_lower:
            comando_ejecutado = True
            url_match = re.search(r'([a-zA-Z0-9-]+\.(com|net|org|io|dev|es|mx|cl|ar|co|biz|info)[^\s]*)', user_input_lower)
            if url_match:
                self.after(0, lambda: self.unblock_website_logic(url_match.group(0)))
            else:
                self.update_status("⚠️ No se encontró una URL válida para desbloquear.")
            return

        # --- 5. Comandos de PC de sistema ---
        for keyword, method_name in self.COMANDOS_PC_SISTEMA.items():
            if keyword in user_input_lower:
                comando_ejecutado = True
                action_function = getattr(self, method_name) 
                self.after(0, lambda: self.handle_pc_action_authorization(
                    user_input_lower, keyword, action_function
                ))
                break
        
        if comando_ejecutado: return

        # --- 6. Comando Interno de Auto-Descripción ---
        if self._handle_internal_command(user_input_lower):
            return
        
        # --- 7. Lógica de IA Generativa ---
        
        # AÑADIDO: Definir is_generative antes de que se use
        is_generative = True
        
        is_explicit_write = user_input_lower.startswith("escribe ")
        is_file_generation_intent = any(keyword in user_input.lower() for keyword in ['genera archivo', 'crea un archivo', 'guarda el script'])
        is_command_execution_intent = any(keyword in user_input.lower() for keyword in ['ejecuta el comando', 'ejecutar', 'run command', 'ejecuta'])
        
        prompt = user_input_lower.split("escribe ", 1)[1] if is_explicit_write else user_input_lower
        
        if self.model is None:
             self.update_status("⚠️ La API de Gemini no está disponible. Solo comandos de PC.")
        else:
            active_title = pyautogui.getActiveWindowTitle()
            
            # --- CORRECCIÓN V22: Extracción del comando literal ---
            original_command_to_execute = None
            if is_command_execution_intent:
                # Regex para buscar la parte del comando después de las palabras clave de ejecución
                match = re.search(r'(ejecuta el comando|ejecutar|run command|ejecuta)\s+(.*)', user_input, re.IGNORECASE)
                if match:
                    original_command_to_execute = match.group(2).strip()
                # Si no se encuentra un match explícito, usa la entrada completa sin la primera palabra
                if not original_command_to_execute:
                    original_command_to_execute = user_input.replace('ejecuta', '').strip() 
            # --- FIN CORRECCIÓN V22 ---
            
            prompt = f"""Eres un asistente de PC para Windows. Sé conciso y directo sin sacrificar información importante.

CAPACIDADES:
- Abrir/cerrar aplicaciones y archivos
- Gestionar archivos y carpetas
- Búsquedas web e información
- Control del sistema (volumen, brillo, etc.)
- Ejecutar comandos y scripts
- Responder preguntas técnicas
- Puedes ejecutar comandos de sistema (CMD/Powershell) si es necesario
- Generar archivos con contenido específico
- Analizar capturas de pantalla y archivos adjuntos
- Insertar texto en el cursor activo (copiar/pegar o escribir letra por letra)
- Automatizar tareas simples
- Gestionar recordatorios y notas
- Bloquear/desbloquear sitios web
- Controlar aplicaciones (abrir, cerrar, minimizar, maximizar)
- Simular servicios como clima, noticias, traducción, etc.
- Gestionar procesos (bloquear aplicaciones)
- Modo Piloto: Detección proactiva de contexto
- Modo Incógnito: Anti-Grabación y privacidad
- Anclaje de ventana (Always On Top)
- Respetar configuraciones de usuario (modo voz, modo escritura, etc.)

REGLAS:
- Respuestas directas, sin rodeos ni preguntas de vuelta
- Si no puedes hacer algo, di "No disponible: [razón]"
- Prioriza soluciones prácticas sobre explicaciones largas
- evita adornos innecesarios
- si el usuario pide ejecutar un comando, pide confirmación antes de ejecutarlo
- si el usuario pide generar un archivo, crea el contenido y espera confirmación antes de guardarlo
- si el usuario pide que escribas algo, prepárate para insertar el texto en el cursor activo

CONTEXTO ACTUAL: {active_title}

PREGUNTA: {user_input}

RESPUESTA:"""
            
            if self.uploaded_file_content:
                prompt_context = f"CONTEXTO: {active_title}. ARCHIVO ADJUNTO ({self.uploaded_file_name}):\n```\n{self.uploaded_file_content}\n```\n\nPregunta del usuario: {user_input}"
                self.uploaded_file_content = None
                self.uploaded_file_name = None
                self.after(0, lambda: self.file_status_label.configure(text="No hay archivo adjunto.", text_color="gray"))

            self.consultar_gemini(user_input, is_generative, is_file_generation_intent, is_command_execution_intent, original_command_to_execute)


    def handle_pc_action_authorization(self, user_input_lower, keyword, action_function):
        confirm = messagebox.askyesno(
            "🚨 Autorización de Comando de PC",
            f"El comando '{keyword.upper()}' requiere acceso al sistema. ¿Autorizas a Fluxi a ejecutarlo?"
        )
        if confirm:
            self.update_status(f"✅ Autorizado: Ejecutando comando '{keyword}'.")
            threading.Thread(target=action_function, args=(user_input_lower,)).start() 
            self.log_terminal(f"Comando de PC: {keyword} autorizado.")
        else:
            self.update_status(f"❌ Comando '{keyword}' cancelado por el usuario.")
            self.log_terminal(f"Comando de PC: {keyword} cancelado.")


    def consultar_gemini(self, user_input, is_generative, is_file_gen, is_command_execution, original_command_to_execute=None):
        """Envía el comando a Gemini y maneja el pegado de código limpio y tareas complejas."""
        try:
            self.update_status("🧠 Consultando a Gemini...")
            
            active_title = pyautogui.getActiveWindowTitle()
            prompt_context = f"Actúa como un copiloto de PC enfocado en el entorno de Windows/PC. Sé extremadamente conciso y directo en tus respuestas, sin usar adornos innecesarios. Evita hacer preguntas de vuelta. CONTEXTO ACTUAL: {active_title}. Pregunta del usuario: {user_input}"
            
            if self.uploaded_file_content:
                prompt_context = f"CONTEXTO: {active_title}. ARCHIVO ADJUNTO ({self.uploaded_file_name}):\n```\n{self.uploaded_file_content}\n```\n\nPregunta del usuario: {user_input}"
                
            response = self.model.generate_content(prompt_context)
            respuesta_texto = response.text.strip()
            self.update_status(f"🤖 Respuesta de Fluxi: {respuesta_texto}")
            
            # 2. Detección de comandos de sistema/shell
            is_code_response = '```' in respuesta_texto
            
            # Si el usuario quiere ejecutar algo O si la respuesta se parece a un comando de shell
            is_potential_command = False
            if not is_code_response and len(respuesta_texto.split()) < 10:
                first_word = respuesta_texto.lower().split()[0] if respuesta_texto.split() else ""
                if first_word in SYSTEM_COMMAND_KEYWORDS:
                    is_potential_command = True
                    
            content_to_paste = respuesta_texto
            match = re.search(r'```[a-zA-Z]*\n(.*?)```', respuesta_texto, re.DOTALL)
            if match: 
                content_to_paste = match.group(1).strip()
            
            is_long_response = len(respuesta_texto.split()) > 40
            
            # 3. Llamada al Handler
            if is_command_execution or is_potential_command:
                 # PASAMOS EL COMANDO ORIGINAL EXTRAÍDO
                 self.after(0, lambda: self._handle_system_task_confirmation(
                     respuesta_texto, clean_content=content_to_paste, is_code_response=is_code_response, 
                     is_file_gen=is_file_gen, is_command_execution=True, 
                     original_command_to_execute=original_command_to_execute
                 ))
                 return

            if is_generative or is_long_response or is_code_response or is_file_gen:
                 # Para escritura normal, NO se pasa original_command_to_execute (se queda en None)
                 self.after(0, lambda: self._handle_system_task_confirmation(
                     respuesta_texto, clean_content=content_to_paste, is_code_response=is_code_response, 
                     is_file_gen=is_file_gen, is_command_execution=False
                 ))
            
            # Limpiar contenido de archivo si fue usado
            if self.uploaded_file_content:
                self.uploaded_file_content = None
                self.uploaded_file_name = None
                self.after(0, lambda: self.file_status_label.configure(text="No hay archivo adjunto.", text_color="gray"))

        except APIError as e:
            self.update_status(f"Hubo un error al conectar con Gemini (API Error): {e}")
            self.speak("Lo siento, no pude contactar a Gemini.")
        except Exception as e:
            self.update_status(f"Hubo un error al conectar con Gemini: {e}")
            self.speak("Lo siento, no pude contactar a Gemini.")

    # FUNCIÓN CLAVE: MANEJO DE AUTORIZACIÓN PARA EJECUTAR, GUARDAR O PEGAR
    def _handle_system_task_confirmation(self, full_response, clean_content, is_code_response, is_file_gen, is_command_execution, original_command_to_execute=None):
        
        # --- Lógica 1: Ejecución de Comando (Prioridad Alta) ---
        if is_command_execution:
            
            command_to_run = original_command_to_execute if original_command_to_execute else clean_content 
            
            # Si el comando extraído del usuario estaba vacío, no hacemos nada
            if not command_to_run:
                 self.update_status("⚠️ No se pudo extraer un comando válido para ejecutar.")
                 return

            confirm = messagebox.askyesno(
                "🚨 Autorización de Ejecución de Comando",
                f"Fluxi ha identificado el siguiente comando:\n\n'{command_to_run}'\n\n¿Quieres ejecutarlo **directamente** en la Terminal de Comandos?"
            )
            if confirm:
                threading.Thread(target=self.execute_command_in_terminal, args=(command_to_run,)).start()
                return

        # --- Lógica 2: Generación de Archivo ---
        if is_file_gen and is_code_response:
            default_filename = "fluxi_script.py"
            confirm = messagebox.askyesno(
                "🚨 Generación de Archivo",
                f"Fluxi ha generado código. ¿Quieres guardar este CÓDIGO limpio en un archivo?\n\n(Selecciona 'No' para solo copiar al cursor o ejecutar el comando si aplica.)"
            )
            if confirm:
                self.after(0, lambda: self.generate_file_with_content(default_filename, clean_content))
                return
        
        # --- Lógica 3: Escritura/Pegado Normal ---
        tipo_contenido = "CÓDIGO" if is_code_response else "TEXTO EXTENSO"
        confirm = messagebox.askyesno(
            "Generación de Contenido",
            f"Fluxi ha generado contenido ({tipo_contenido}). ¿Quieres que lo pegue directamente en tu cursor?"
        )
        if confirm:
            threading.Thread(target=self.write_to_cursor, args=(clean_content,)).start()
        else:
            self.update_status("Escritura de contenido cancelada.")


    # --- FUNCIONES DE CONTROL DE PC (IMPLEMENTADAS O MOCK DETALLADO) ---
    
    def get_volume_interface(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))

    def control_volume(self, comando_input):
        if not VOLUMEN_DISPONIBLE:
            self.update_status("⚠️ pycaw no está disponible. No se puede controlar el volumen.")
            self.log_terminal("Control Volumen", error="pycaw no disponible.")
            return
        
        try:
            comtypes.CoInitialize()
            volume = self.get_volume_interface()
            
            if "silencia" in comando_input or "mudo" in comando_input:
                volume.SetMute(1, None)
                self.update_status("🔇 PC silenciada.")
                self.log_terminal("Control Volumen", output="PC silenciada.")
            else:
                current_scalar = volume.GetMasterVolumeLevelScalar()
                current_vol_perc = int(current_scalar * 100)
                new_vol_perc = current_vol_perc
                
                if "sube" in comando_input or "aumenta" in comando_input:
                    new_vol_perc = min(100, current_vol_perc + 10)
                elif "baja" in comando_input or "reduce" in comando_input:
                    new_vol_perc = max(0, current_vol_perc - 10)
                
                volume.SetMasterVolumeLevelScalar(new_vol_perc / 100.0, None)
                self.update_status(f"🔊 Volumen ajustado a {new_vol_perc}%.")
                self.log_terminal("Control Volumen", output=f"Volumen ajustado a {new_vol_perc}%.")

        except Exception as e:
            self.update_status(f"Error al controlar el volumen: {e}")
            self.log_terminal("Control Volumen", error=str(e))
        finally:
             comtypes.CoUninitialize()

    def control_brightness(self, comando_input): self.update_status("🔆 Simulación: Brillo de pantalla ajustado. (Requiere librerías específicas de sistema)"); self.log_terminal("Control Brillo", output="Brillo ajustado (Simulación).")
    def shutdown_pc(self, comando_input): self.update_status("⚠️ Simulación: PC apagada en 60 segundos. (Comando real: `shutdown /s /t 60`)"); self.log_terminal("Apagar PC", output="Simulación de apagado.")
    def reboot_pc(self, comando_input): self.update_status("⚠️ Simulación: PC reiniciada. (Comando real: `shutdown /r /t 0`)"); self.log_terminal("Reiniciar PC", output="Simulación de reinicio.")
    def lock_pc(self, comando_input): subprocess.Popen(['rundll32.exe', 'user32.dll,LockWorkStation']); self.update_status("🔒 Bloqueando PC."); self.log_terminal("Bloquear PC", output="PC bloqueada.")
    def screenshot(self, comando_input): img = ImageGrab.grab(); img.save("screenshot_fluxi.png"); self.update_status("📸 Captura de pantalla guardada como 'screenshot_fluxi.png'."); self.log_terminal("Captura", output="Captura de pantalla realizada.")
    
    def control_sharing(self, comando_input): self.update_status("Simulación: Compartir controlado."); self.log_terminal("Compartir", output="Simulación ok.")
    def copy_text(self, comando_input): pyautogui.hotkey('ctrl', 'c'); self.update_status("Texto copiado."); self.log_terminal("Copiar", output="Ctrl+C enviado.")
    def paste_text(self, comando_input): pyautogui.hotkey('ctrl', 'v'); self.update_status("Texto pegado."); self.log_terminal("Pegar", output="Ctrl+V enviado.")
    def select_all(self, comando_input): pyautogui.hotkey('ctrl', 'a'); self.update_status("Todo seleccionado."); self.log_terminal("Seleccionar Todo", output="Ctrl+A enviado.")
    def close_window(self, comando_input): pyautogui.hotkey('alt', 'f4'); self.update_status("Ventana cerrada."); self.log_terminal("Cerrar Ventana", output="Alt+F4 enviado.")
    def maximize_window(self, comando_input): pyautogui.hotkey('win', 'up'); self.update_status("Ventana maximizada."); self.log_terminal("Maximizar", output="Win+Up enviado.")
    def minimize_window(self, comando_input): pyautogui.hotkey('win', 'down'); self.update_status("Ventana minimizada."); self.log_terminal("Minimizar", output="Win+Down enviado.")
    def open_explorer(self, comando_input): subprocess.Popen('explorer'); self.update_status("Explorador abierto."); self.log_terminal("Abrir Explorador", output="Comando 'explorer' ejecutado.")
    def open_settings(self, comando_input): subprocess.Popen(['ms-settings:']); self.update_status("Configuración de Windows abierta."); self.log_terminal("Abrir Configuración", output="Comando 'ms-settings:' ejecutado.")
    def play_media(self, comando_input): pyautogui.press('playpause'); self.update_status("Reproducir/Pausar enviado."); self.log_terminal("Media", output="Play/Pause enviado.")
    def pause_media(self, comando_input): pyautogui.press('playpause'); self.update_status("Reproducir/Pausar enviado."); self.log_terminal("Media", output="Play/Pause enviado.")
    def next_media(self, comando_input): pyautogui.press('nexttrack'); self.update_status("Pista siguiente enviado."); self.log_terminal("Media", output="Pista siguiente enviado.")
    def previous_media(self, comando_input): pyautogui.press('prevtrack'); self.update_status("Pista anterior enviado."); self.log_terminal("Media", output="Pista anterior enviado.")

    def search_local(self, comando_input): self.update_status("🔎 Simulación: Iniciando búsqueda de archivos en el PC."); self.log_terminal("Búsqueda Local", output="Simulación ok.")
    def simulate_file_management(self, comando_input): self.update_status("📂 Simulación: Ejecutando gestión de archivos. (Necesita confirmación de ruta)"); self.log_terminal("Gestión Archivos", output="Simulación ok.")
    def simulate_math_conversion(self, comando_input): self.update_status("🧮 Simulación: Realizando cálculo/conversión avanzada."); self.log_terminal("Cálculos", output="Simulación ok.")
    def simulate_translation(self, comando_input): self.update_status("🗣️ Simulación: Realizando traducción de texto."); self.log_terminal("Traducción", output="Simulación ok.")
    def simulate_weather(self, comando_input): self.update_status("🌤️ Simulación: Consultando pronóstico del tiempo."); self.log_terminal("Clima", output="Simulación ok.")
    def simulate_news(self, comando_input): self.update_status("📰 Simulación: Buscando titulares de noticias."); self.log_terminal("Noticias", output="Simulación ok.")
    def simulate_command_history(self, comando_input): self.update_status("📚 Simulación: Mostrando historial de comandos."); self.log_terminal("Historial", output="Simulación ok.")
    def simulate_system_monitor(self, comando_input): self.update_status("📊 Simulación: Mostrando uso de CPU/RAM."); self.log_terminal("Monitor", output="Simulación ok.")
    def simulate_definition(self, comando_input): self.update_status("💡 Simulación: Buscando definición o artículo de Wikipedia."); self.log_terminal("Definición", output="Simulación ok.")
    def simulate_password_gen(self, comando_input): self.update_status("🔑 Simulación: Generando una contraseña segura."); self.log_terminal("Contraseñas", output="Simulación ok.")

    # --- FIN FUNCIONES DE CONTROL DE PC ---

    # --- FUNCIONES DE CAPTURA Y ANÁLISIS ---

    def schedule_capture(self):
        try:
            self._capture_screen_for_analysis()
            
            if self.pilot_mode_active:
                self.check_blocked_websites()
                
            self.after(MIN_CAPTURE_INTERVAL * 1000, self.schedule_capture) 
        except Exception:
            self.after(MIN_CAPTURE_INTERVAL * 1000, self.schedule_capture) 

    def _capture_screen_for_analysis(self):
        try:
            img = ImageGrab.grab()
            self.last_screenshot = img
            
            img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 180))
            self.screen_preview.configure(image=img_ctk)
            self.screen_preview.image = img_ctk  
            
            self.last_capture_label.configure(text=time.strftime("Última captura: %H:%M:%S"))
            
            if self.pilot_mode_active:
                self._run_pilot_mode_check()

        except Exception:
            self.last_capture_label.configure(text="Error al capturar.")

    def trigger_context_analysis(self, user_prompt=None):
        if self.model is None or self.last_screenshot is None:
            self.update_status("⚠️ No hay imagen capturada o la IA no está disponible.")
            return

        prompt = user_prompt if user_prompt else "Analiza el contenido de esta imagen para entender el contexto actual del usuario. Describe brevemente lo que ves y sugiere una acción útil."
        self.update_status("🧠 Enviando imagen a Gemini para análisis contextual...")

        threading.Thread(target=self._run_analysis_thread, args=(prompt, False)).start() 

    def _run_analysis_thread(self, prompt, is_proactive):
        """Lógica de llamada a la API de Gemini para análisis de imágenes."""
        try:
            img_byte_arr = io.BytesIO()
            self.last_screenshot.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            response = self.model.generate_content([
                prompt,
                Image.open(io.BytesIO(img_bytes))
            ])
            
            self.after(0, lambda: self._display_analysis_result(response.text.strip(), is_proactive))

        except APIError as e:
            self.after(0, lambda: self.update_status(f"Error de API al analizar: {e}"))
        except Exception as e:
            self.after(0, lambda: self.update_status(f"Error de análisis: {e}"))

    def _display_analysis_result(self, result_text, is_proactive):
        """Muestra el resultado del análisis de Gemini."""
        if is_proactive:
            if "no se detectó un error obvio" not in result_text.lower() and "no hay un error visible" not in result_text.lower():
                self.update_status(f"🚨 ERROR DETECTADO POR PILOTO: {result_text}")
                self.speak("¡Alerta! Detecté un posible error en tu pantalla.")
            return
            
        self.update_status("✅ Análisis de Contexto Completado.")
        if not self.incognito_mode_active:
            self.output_text.configure(state="normal")
            self.output_text.insert("end", f"\n[GEMINI ANÁLISIS] {result_text}")
            self.output_text.see("end")
            self.output_text.configure(state="disabled")

    # --- FUNCIONES DE MODO PILOTO ---
    
    def toggle_pilot_mode(self):
        self.pilot_mode_active = self.pilot_switch.get()
        if self.pilot_mode_active:
            self.update_status("Modo Piloto ACTIVADO. Fluxi monitorizará la actividad.")
            self.stop_pilot_thread.clear()
        else:
            self.stop_pilot_thread.set()
            self.update_status("Modo Piloto DESACTIVADO.")

    def _run_pilot_mode_check(self):
        """Realiza la comprobación de contexto y actúa (se ejecuta en cada captura)."""
        try:
            active_url_candidate, active_title = self.get_active_url()
            
            if not active_title: return

            # Detección Proactiva de Errores (cada N ciclos)
            if self.model and self.pilot_check_count % CAPTURE_CHECK_DIVISOR == 0:
                error_prompt = "Analiza la imagen. ¿Ves algún mensaje de error (letras rojas, iconos de alerta, popups de fallo, pantallas azules/negras con texto de error)? Si ves un error, transcribe el texto y sugiere una solución concisa. Si no hay error visible, responde solo 'No se detectó un error obvio.'."
                threading.Thread(target=self._run_analysis_thread, args=(error_prompt, True)).start()
            
            self.pilot_check_count += 1
            
            # Chequeo de seguridad de navegación/juegos
            if active_url_candidate:
                is_dangerous = any(keyword in active_url_candidate for keyword in DANGEROUS_KEYWORDS)
                
                if is_dangerous:
                    self.update_status(f"🚨 ALERTA DE SEGURIDAD: '{active_url_candidate}' parece peligroso. Cerrando la pestaña.")
                    webbrowser.open(REDIRECT_URL) 
                    pyautogui.hotkey('ctrl', 'w')
                    self.speak("Alerta. He cerrado una pestaña de riesgo.")
                    return

            is_game = any(keyword in active_title.lower() for keyword in GAME_KEYWORDS)
            is_sensitive = any(keyword in active_title.lower() for keyword in SENSITIVE_APPS)

            if is_game or is_sensitive:
                if time.time() - self._last_pilot_game_ask > 120:
                    action = "Estás jugando un juego" if is_game else "Estás en una aplicación sensible"
                    self.update_status(f"🎮 {action}, ¿necesitas ayuda con la configuración o alguna tarea de fondo?")
                    self.speak(f"{action}, ¿necesitas algo?")
                    self._last_pilot_game_ask = time.time()
                
        except Exception as e:
            self.after(0, lambda: self.update_status(f"⚠️ Error en el chequeo del Modo Piloto: {e}"))


    # --- FUNCIONES DE BLOQUEO WEB Y SEGURIDAD ---

    def block_website(self, url):
        """Bloquea una URL añadiéndola a la lista de bloqueo."""
        url_base = re.sub(r'^https?://(www\.)?', '', url).strip('/').lower()
        blocked_list = load_blocked_websites()
        if url_base not in blocked_list:
            blocked_list.append(url_base)
            save_blocked_websites(blocked_list)
            self.update_status(f"🔒 Sitio BLOQUEADO: '{url_base}'.")
            self.log_terminal("Bloqueo Web", output=f"'{url_base}' bloqueado.")
        else:
            self.update_status(f"⚠️ El sitio '{url_base}' ya estaba bloqueado o no es válido.")
            self.log_terminal("Bloqueo Web", output=f"'{url_base}' ya estaba bloqueado.")

    def unblock_website_logic(self, url):
        """Desbloquea una URL si está en la lista de bloqueo (Usado por comandos y GUI)."""
        url_base = re.sub(r'^https?://(www\.)?', '', url).strip('/').lower()
        blocked_list = load_blocked_websites()
        
        if url_base in blocked_list:
            blocked_list.remove(url_base)
            save_blocked_websites(blocked_list)
            self.update_status(f"🔓 Sitio DESBLOQUEADO: '{url_base}'.")
            self.log_terminal("Bloqueo Web", output=f"'{url_base}' desbloqueado.")
            return True
        else:
            self.update_status(f"⚠️ El sitio '{url_base}' ya se encontraba desbloqueado.")
            self.log_terminal("Bloqueo Web", output=f"'{url_base}' ya estaba desbloqueado.")
            return False

    def check_blocked_websites(self):
        """Comprueba si la URL activa está bloqueada y redirige (Solo llamado si Pilot Mode está activo)."""
        try:
            url_candidate, _ = self.get_active_url()
            if url_candidate:
                url_base = re.sub(r'^https?://(www\.)?', '', url_candidate).strip('/').lower()
                blocked_list = load_blocked_websites()
                
                if any(blocked in url_base for blocked in blocked_list):
                    self.update_status(f"🚨 ACCESO DENEGADO: '{url_candidate}' está bloqueado. Redirigiendo.")
                    webbrowser.open(REDIRECT_URL)
                    pyautogui.hotkey('ctrl', 'w')
                    self.speak("Acceso bloqueado.")
        except Exception:
            pass
    
    # --- FUNCIONES DE VENTANA Y CONFIGURACIÓN ---

    def show_blocked_sites(self):
        blocked_sites_window = ctk.CTkToplevel(self)
        blocked_sites_window.title("🔒 Sitios Web Bloqueados")
        blocked_sites_window.geometry("500x300")
        blocked_sites_window.transient(self)
        blocked_sites_window.resizable(False, False)
        
        blocked_list = load_blocked_websites()
        
        ctk.CTkLabel(blocked_sites_window, text="URLs Bloqueadas (Piloto y Seguridad)", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        scroll_frame = ctk.CTkScrollableFrame(blocked_sites_window, width=450, height=200)
        scroll_frame.pack(padx=20, pady=10, fill="both")
        
        if not blocked_list:
            ctk.CTkLabel(scroll_frame, text="No hay sitios web bloqueados actualmente.").pack(pady=20)
            return

        for i, url in enumerate(blocked_list):
            row_frame = ctk.CTkFrame(scroll_frame)
            row_frame.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(row_frame, text=f"{i+1}. {url}", anchor="w", width=350).pack(side="left", padx=5)
            
            # Función anónima para que cada botón tenga su propia URL en el comando
            def delete_site(u):
                if self.unblock_website_logic(u):
                    messagebox.showinfo("Éxito", f"El sitio '{u}' ha sido desbloqueado.")
                blocked_sites_window.destroy()
                self.show_blocked_sites() # Recargar la ventana para actualizar la lista

            ctk.CTkButton(row_frame, text="🗑️ Eliminar", command=lambda u=url: delete_site(u), fg_color="#FF0000", hover_color="#8B0000").pack(side="right", padx=5)
            
        blocked_sites_window.grab_set()


    def open_settings_window(self):
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("⚙️ Configuración de Fluxi")
        settings_window.geometry("400x650") 
        settings_window.transient(self) 
        settings_window.resizable(False, False)

        ctk.CTkLabel(settings_window, text="🎨 Tema de la Aplicación:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        theme_frame = ctk.CTkFrame(settings_window)
        theme_frame.pack(padx=20, pady=5)
        
        def set_theme(value):
            self.config_theme.set(value)
            self.config_data["theme"] = value
            save_config(self.config_data)
            self.apply_theme_change()

        ctk.CTkRadioButton(theme_frame, text="Dark", variable=self.config_theme, value="Dark", command=lambda: set_theme("Dark")).pack(side="left", padx=5)
        ctk.CTkRadioButton(theme_frame, text="Light", variable=self.config_theme, value="Light", command=lambda: set_theme("Light")).pack(side="left", padx=5)
        ctk.CTkRadioButton(theme_frame, text="System", variable=self.config_theme, value="System", command=lambda: set_theme("System")).pack(side="left", padx=5)

        ctk.CTkLabel(settings_window, text="🕵️ Modo Incógnito / Anti-Grabación:", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        incognito_frame = ctk.CTkFrame(settings_window)
        incognito_frame.pack(padx=20, pady=5)
        
        def toggle_incognito():
            self.incognito_mode_active = not self.incognito_mode_active
            self.config_data["incognito_mode"] = self.incognito_mode_active
            save_config(self.config_data)
            self.update_log_state()
            self.set_incognito_visuals(self.incognito_mode_active) 
            self.update_status(f"Modo Incógnito: {'ACTIVADO' if self.incognito_mode_active else 'DESACTIVADO'}")

        self.incognito_check = ctk.CTkCheckBox(incognito_frame, text="Activar modo de privacidad (Desactiva logs y Anti-Grabación)", command=toggle_incognito)
        if self.incognito_mode_active: self.incognito_check.select()
        self.incognito_check.pack(padx=5, pady=5)
        
        ctk.CTkLabel(settings_window, text="💬 Modo de Respuesta (Mensaje/Voz):", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        response_frame = ctk.CTkFrame(settings_window)
        response_frame.pack(padx=20, pady=5)
        
        def set_response_mode(value):
            self.config_response_mode.set(value)
            self.config_data["response_mode"] = value
            save_config(self.config_data)

        ctk.CTkRadioButton(response_frame, text="Solo Mensaje", variable=self.config_response_mode, value="Solo Mensaje", command=lambda: set_response_mode("Solo Mensaje")).pack(side="left", padx=5)
        ctk.CTkRadioButton(response_frame, text="Solo Voz", variable=self.config_response_mode, value="Solo Voz", state="normal" if VOZ_DISPONIBLE else "disabled", command=lambda: set_response_mode("Solo Voz")).pack(side="left", padx=5)
        ctk.CTkRadioButton(response_frame, text="Ambos", variable=self.config_response_mode, value="Ambos", state="normal" if VOZ_DISPONIBLE else "disabled", command=lambda: set_response_mode("Ambos")).pack(side="left", padx=5)
        
        ctk.CTkLabel(settings_window, text="✍️ Modo de Escritura (Pegado):", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        write_frame = ctk.CTkFrame(settings_window)
        write_frame.pack(padx=20, pady=5)
        
        def set_write_mode(value):
            self.config_write_mode.set(value)
            self.config_data["write_mode"] = value
            save_config(self.config_data)

        ctk.CTkRadioButton(write_frame, text="Copiar/Pegar (Rápido)", variable=self.config_write_mode, value="Copiar/Pegar", command=lambda: set_write_mode("Copiar/Pegar")).pack(side="left", padx=5)
        ctk.CTkRadioButton(write_frame, text="Escribir L.x.L. (Simulación)", variable=self.config_write_mode, value="Escribir Letra por Letra", command=lambda: set_write_mode("Escribir Letra por Letra")).pack(side="left", padx=5)

        ctk.CTkLabel(settings_window, text="🛠️ Personalización Avanzada:", font=ctk.CTkFont(weight="bold")).pack(pady=20)
        ctk.CTkButton(settings_window, text="Ver y Eliminar Sitios Bloqueados", command=self.show_blocked_sites).pack(pady=5)
        
        settings_window.grab_set() 

    def apply_theme_change(self):
        if not self.incognito_mode_active:
            ctk.set_appearance_mode(self.config_theme.get())
            self.update_status(f"Tema cambiado a: {self.config_theme.get()}")
        else:
            self.update_status(f"⚠️ Tema no cambiado: Modo Incógnito ACTIVO (Requiere tema Dark).")


    def get_active_url(self):
        try:
            active_title = pyautogui.getActiveWindowTitle()
            if not active_title: return None, None
            
            url_candidate = None
            if "edge" in active_title.lower() or "chrome" in active_title.lower() or "firefox" in active_title.lower():
                if self.pilot_mode_active:
                    url_candidate = active_title.split(' - ')[0].replace(' ', '').lower() 
            
            return url_candidate, active_title
        except Exception:
            return None, None

    def hide_window(self):
        self.withdraw()

    def restore_window(self, icon, item):
        self.deiconify()
        self.after(0, self.lift)
        self.after(0, self.focus_force)


if __name__ == '__main__':
    app = AsistenteApp()
    app.mainloop()