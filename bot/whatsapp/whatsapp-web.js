// whatsapp_bot.js
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

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
    if (!msg.body) return;

    try {
        const response = await axios.post('http://localhost:8000/webhook', {
            id_usuario: msg.from,  // Número con @c.us
            texto: msg.body
        });

        const respuesta = response.data.respuesta;
        if (respuesta) {
            await client.sendMessage(msg.from, respuesta);
        }
    } catch (error) {
        console.error("❌ Error al procesar mensaje:", error);
        await client.sendMessage(msg.from, "⚠️ Ocurrió un error al procesar tu mensaje.");
    }
});

client.initialize();
