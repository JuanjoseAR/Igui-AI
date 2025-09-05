Igui-AI

Igui-AI es un servicio de inteligencia artificial diseñado para integrarse fácilmente como backend conversacional. Permite conexiones flexibles con interfaces como WhatsApp, bots de Telegram o chats web.

📌 Descripción del Proyecto

Igui-AI proporciona un servicio de chat inteligente basado en IA que puede integrarse en diversas plataformas de mensajería o aplicaciones web. El frontend es modular y depende del caso de uso: puede conectarse a librerías de WhatsApp, Telegram o añadirse a un chat en una página web. La arquitectura está pensada para dejar el servicio disponible como microservicio o API REST.

🚀 Características

Interfaz flexible: compatible con WhatsApp, Telegram y chats web.

Servicio backend independiente: expone endpoints REST para manejar mensajes.

Lógica impulsada por IA: procesamiento de lenguaje natural para formular respuestas útiles.

Escalable: puede desplegarse en servidores o entornos serverless como contenedores o funciones.

Colaborativo y abierto: ideal para contribuciones externas y extensiones.

📁 Estructura de Directorios
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

🛠️ Instalación & Uso
Dependencias de instalación (ej. Node.js):
npm install


Configura tus credenciales (WhatsApp, Telegram, claves API) en config/.

Ejecuta en desarrollo:
npm run dev

(Opcional) Ejecución vía Docker:
docker build -t igui-ai .
docker run -p 3000:3000 igui-ai

Pruebas:
npm test

🧠 ¿Cómo conectar un Frontend?

Puedes adaptar el frontend según tu escenario:

WhatsApp: usa una librería tipo whatsapp-web.js o APIs oficiales para recibir y enviar mensajes desde tu número de WhatsApp conectado al backend.

Telegram: usa node-telegram-bot-api, telegraf, u otras librerías para Telegram para manejar actualizaciones webhook.

Chat Web: crea un frontend en React/Vue/HTML que envíe mensajes vía fetch/AJAX a tu endpoint REST y renderice respuestas en tiempo real.

👥 Colaboradores

Este proyecto es mantenido por:

Juan José Arango Rodríguez

Andrés Felipe Angulo López

Luis Miguel Toscano Sánchez

José Luis Romero Gonzales

Breiner Gonzales Machado

📝 Contribuciones

Las contribuciones son bienvenidas. Para colaborar:

Haz un fork del repositorio.

Crea una rama (feature/tu-nueva-funcionalidad).

Haz cambios y asegúrate de pasar las pruebas.

Envía un Pull Request describiendo tus cambios.

Por favor, revisa el archivo CONTRIBUTING.md (si existe) para detalles adicionales sobre estilo de código, pruebas, etc.

📚 Documentación y Recursos

Documentación del API: documentos en docs/ o auto generada con herramientas como Swagger, Postman, etc.

Guías de integración: ejemplos de conectores (WhatsApp, Telegram, chat web).

Referencias internas: descripción de endpoints, formatos de mensajes, estructura de datos, etc.

✅ Licencia

Este proyecto está bajo la licencia MIT License (o especifica la correspondiente).
