# 🌐 Igui-AI

**Igui-AI** es un servicio de inteligencia artificial diseñado para transformar repositorios en documentación **interactiva, accesible y explicativa**.  
Su arquitectura **desacoplada** permite conectarlo fácilmente con diferentes interfaces como **WhatsApp, Telegram o un chat web**.

---

## ✨ Características

- 🔌 **Servicio desacoplado**: el backend AI puede ser consumido desde cualquier cliente.  
- 📄 **Documentación automática**: genera explicaciones de funciones, clases y módulos.  
- 📊 **Diagramas visuales**: crea diagramas (ej. Mermaid) para mostrar arquitectura y flujo.  
- 🔍 **Búsqueda inteligente**: preguntas en lenguaje natural al código/documentación.  
- 🧠 **Deep research**: análisis en múltiples pasos con IA para explicar y mejorar decisiones de diseño.  
- 🤖 **Compatibilidad multi-modelo**: soporte para OpenAI, Gemini, OpenRouter y modelos locales (Ollama).  

---

## 🧰 Tecnologías

| Componente     | Tecnología |
|----------------|------------|
| **Backend**    | FastAPI (Python) |
| **AI**         | OpenAI, Gemini, OpenRouter, Ollama |
| **Frontend**   | Flexible (WhatsApp, Telegram, Webchat, etc.) |
| **Diagramas**  | Mermaid |
| **Persistencia** | Embeddings para búsqueda semántica |

---

## ⚙️ Instalación

### 🔹 Opción 1: Usando Docker (recomendado)

```bash
git clone https://deepwiki.com/JuanjoseAR/Igui-AI.git
cd Igui-AI
cp .env.example .env
# Configura tus claves (OPENAI_API_KEY, GEMINI_API_KEY, etc.)
docker-compose up
Accede al servicio en:
👉 http://localhost:3000 (o conéctalo al cliente que prefieras).

🔹 Opción 2: Instalación manual
Clona el repositorio y crea tu .env.

Instala el backend:

bash
Copiar código
cd api
pip install -r requirements.txt
uvicorn main:app --reload
Integra el cliente de tu elección (ej. WhatsApp, Telegram, Webchat).

🚀 Flujo de funcionamiento
mermaid
Copiar código
flowchart TD
    A[Usuario] -->|URL del repo| B[Backend Igui-AI]
    B --> C[Análisis del repositorio]
    C --> D[Generación de Embeddings]
    D --> E[Documentación y Diagramas]
    E --> F[Interfaz elegida: WhatsApp/Telegram/Web]
📂 Estructura del proyecto
bash
Copiar código
/
├── api/                  # Backend con FastAPI
├── clients/              # Adaptadores (WhatsApp, Telegram, Webchat)
├── .env.example          # Variables de entorno
├── docker-compose.yml    # Configuración Docker
└── README.md             # Este archivo
👥 Colaboradores
👨‍💻 Juan José Arango Rodríguez

👨‍💻 Andrés Felipe Angulo López

👨‍💻 Luis Miguel Toscano Sánchez

👨‍💻 José Luis Romero Gonzales

👨‍💻 Breiner Gonzales Machado

🤝 Contribución
Las contribuciones son bienvenidas 🚀
Puedes:

Agregar nuevos clientes (ej. Slack, Discord).

Mejorar el análisis de código y embeddings.

Optimizar generación de diagramas.

Reportar errores o sugerir mejoras vía issues o pull requests.

🧾 Licencia
📜 Este proyecto está bajo MIT License. Consulta el archivo LICENSE para más información.
