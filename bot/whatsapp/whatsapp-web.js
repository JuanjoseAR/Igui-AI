const fs = require('fs');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('✅ Bot WhatsApp listo');
});

client.on('message', async msg => {
    try {
        if (msg.hasMedia) {
            const media = await msg.downloadMedia();
            if (!media || !media.mimetype.startsWith('text')) {
                await client.sendMessage(msg.from, "❌ Solo se aceptan archivos de texto (.txt o .docx).");
                return;
            }

            if (media && media.mimetype.includes('text')) {
                const buffer = Buffer.from(media.data, 'base64');
                const fileName = media.filename || `archivo_${Date.now()}.txt`;
                const filePath = path.join(__dirname, 'temp', fileName);

                // Crear carpeta si no existe
                fs.mkdirSync(path.join(__dirname, 'temp'), { recursive: true });

                // Guardar archivo temporalmente
                fs.writeFileSync(filePath, buffer);

                // Preparar el form-data
                const formData = new FormData();
                formData.append('archivo', fs.createReadStream(filePath));
                formData.append('id_usuario', msg.from);

                const response = await axios.post('http://localhost:8000/cargar-preguntas', formData, {
                    headers: formData.getHeaders()
                });

                const respuesta = response.data.respuesta;
                if (respuesta) await client.sendMessage(msg.from, respuesta);

                // Eliminar el archivo temporal después de enviarlo (opcional)
                fs.unlinkSync(filePath);
            }

            return;
        }

        if (!msg.body || typeof msg.body !== 'string' || msg.body.trim() === '') {
            await client.sendMessage(msg.from, "❌ Solo se aceptan mensajes de texto legibles.");
            return;
        }

        const response = await axios.post('http://localhost:8000/webhook', {
            id_usuario: msg.from,
            texto: msg.body
        });

        const respuesta = response.data.respuesta;
        if (respuesta) await client.sendMessage(msg.from, respuesta);

    } catch (error) {
        console.error("❌ Error al procesar mensaje:", error);
        await client.sendMessage(msg.from, "⚠️ Ocurrió un error al procesar tu mensaje.");
    }
});

client.initialize();
