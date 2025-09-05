# Igui-AI

**Igui-AI** es un servicio de inteligencia artificial diseñado para integrarse fácilmente como backend conversacional. Permite conexiones flexibles con interfaces como WhatsApp, bots de Telegram o chats web.

---

## 📌 Descripción del Proyecto

Igui-AI proporciona un servicio de chat inteligente basado en IA que puede integrarse en diversas plataformas de mensajería o aplicaciones web. El frontend es modular y depende del caso de uso: puede conectarse a librerías de WhatsApp, Telegram o añadirse a un chat en una página web. La arquitectura está pensada para dejar el servicio disponible como microservicio o API REST.

---

## 🚀 Características

- **Interfaz flexible**: compatible con WhatsApp, Telegram y chats web.  
- **Servicio backend independiente**: expone endpoints REST para manejar mensajes.  
- **Lógica impulsada por IA**: procesamiento de lenguaje natural para formular respuestas útiles.  
- **Escalable**: puede desplegarse en servidores o entornos serverless como contenedores o funciones.  
- **Colaborativo y abierto**: ideal para contribuciones externas y extensiones.  

---

## 📁 Estructura de Directorios

```text
/.
├── src/                # Código fuente del backend
│   ├── api/            # Controladores o rutas (ej. webhook, REST endpoints)
│   ├── services/       # Lógica de IA y procesamiento de mensajes
│   └── utils/          # Utilidades y helpers
├── config/             # Archivos de configuración (API keys, tokens)
├── tests/              # Pruebas unitarias e integraciones
├── Dockerfile          # Para contenerización
├── docker-compose.yml  # Orquestación si hay múltiples servicios
├── package.json        # Dependencias y scripts (si es Node.js)
└── README.md           # Este archivo
