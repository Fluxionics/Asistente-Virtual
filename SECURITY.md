# 🔒 Seguridad y Privacidad del Asistente Copiloto Fluxi

Este documento describe las medidas de seguridad, la gestión de la privacidad y los protocolos de manejo de datos implementados en el Asistente Copiloto Fluxi (Versión 14).

**AVISO IMPORTANTE:** Fluxi se distribuye como un software de **código cerrado (ejecutable)**. La confianza en la seguridad se basa en los protocolos aquí descritos y la gestión de la clave API por parte del usuario.

---

## 1. Gestión de la Clave de API (GEMINI_API_KEY) 🔑

La **clave de API** es la credencial más sensible requerida por Fluxi.

* **Archivo `.env`:** La clave debe ser almacenada única y exclusivamente en el archivo de configuración `.env` en el directorio raíz de la aplicación, bajo la variable `GEMINI_API_KEY`.
    * **El ejecutable no contiene la clave incrustada**; la lee directamente del `.env`.
* **Responsabilidad del Usuario:** Es responsabilidad total del usuario proteger y asegurar el archivo `.env`. Nunca debe ser compartido.
* **Tráfico Cifrado:** Todas las comunicaciones entre Fluxi y los servidores de Gemini se realizan a través de **HTTPS cifrado**, asegurando que su clave y sus consultas no sean interceptadas en tránsito.

---

## 2. Privacidad y Protocolos de Datos 🛡️

Fluxi está diseñado para minimizar la exposición de datos sensibles.

### A. Modo Incógnito (Anti-Grabación)

El Modo Incógnito es nuestra principal característica de privacidad:

* **No se Registra Actividad:** Al activarse, Fluxi **elimina y desactiva el registro de historial** (`output_text`), asegurando que las conversaciones y comandos no se almacenen.
* **Protección Visual:** Utiliza comandos de sistema (`win32con.WS_EX_LAYERED`) para hacer que la ventana de la aplicación sea **transparente para software de grabación y streaming** (como OBS, Zoom o Teams), previniendo la captura accidental de sus datos dentro de la interfaz de Fluxi.

### B. Datos No Compartidos

* **Comandos de PC:** La información sobre comandos del sistema operativo (`volumen`, `bloquear`, etc.) y sus resultados se procesa **localmente** y no se envía a los servidores de Gemini.
* **Archivos Adjuntos:** El contenido de los archivos que adjunta para el análisis de la IA **solo se envía durante la consulta específica** y no se almacena permanentemente en el sistema de Fluxi.

---

## 3. Seguridad Proactiva y Control de PC 🚨

Fluxi incorpora funciones de seguridad para proteger al usuario de amenazas externas y asegurar el control del sistema.

| Característica | Propósito de Seguridad | Protocolo de Ejecución |
| :--- | :--- | :--- |
| **Lista Negra Web** | Bloqueo de dominios introducidos por el usuario para prevenir el acceso a sitios distractores o maliciosos. | El chequeo se realiza en un bucle cada 5 segundos. **Redirecciona** y **cierra** la pestaña peligrosa. |
| **Detección de Keywords** | Identificación de sitios web con palabras clave peligrosas predefinidas (ej: *phishing*, *malware*). | El chequeo se realiza en un bucle cada 5 segundos y actúa de inmediato. |
| **Autorización de Comandos** | Antes de ejecutar cualquier comando de control de PC (`shutdown`, `lock`, `volume`), Fluxi **siempre solicita una confirmación explícita** al usuario mediante un cuadro de diálogo. | Previene la ejecución accidental o maliciosa de comandos del sistema. |
| **Análisis de Captura (Pilot Mode)** | Envía una captura de pantalla a Gemini solo para un **análisis contextual y de error**, evitando que la IA actúe ciegamente. | La imagen es enviada por HTTPS, analizada por Gemini, y la respuesta regresa al log. |

---

## 4. Reporte de Vulnerabilidades 🐞

Aunque el código fuente es cerrado, valoramos la seguridad.

* Si encuentra una vulnerabilidad o un comportamiento inesperado relacionado con la seguridad o privacidad de los datos en el ejecutable o en el manejo del archivo `.env`, por favor, repórtelo al canal de soporte oficial del desarrollador.

**Contacto de Seguridad:** [Aqui](https://fluxionics.github.io/contacto.html)
