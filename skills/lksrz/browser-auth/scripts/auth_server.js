const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { chromium } = require('playwright-core');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

async function startServer({ 
    port = 19191, 
    host = '127.0.0.1',
    chromiumPath = '/usr/bin/chromium-browser', 
    sessionFile = 'session.json',
    token = crypto.randomBytes(16).toString('hex'),
    proxy = process.env.BROWSER_PROXY || null
}) {
    const app = express();
    const server = http.createServer(app);
    const io = new Server(server);

    app.get('/', (req, res) => {
        if (req.query.token !== token) {
            return res.status(403).send('Forbidden: Invalid or missing token');
        }
        // Use path.resolve to ensure we have an absolute path
        const indexPath = path.resolve(__dirname, '../assets/index.html');
        
        if (!fs.existsSync(indexPath)) {
            console.error(`Asset not found at: ${indexPath}`);
            return res.status(404).send(`NotFoundError: Asset not found at ${indexPath}`);
        }
        
        res.sendFile(indexPath);
    });

    io.use((socket, next) => {
        const socketToken = socket.handshake.query.token;
        if (socketToken === token) {
            return next();
        }
        return next(new Error('Authentication error'));
    });

    io.on('connection', async (socket) => {
        console.log('User authenticated and connected');
        
        const launchArgs = [
            '--disable-dev-shm-usage',
            '--no-first-run',
            '--no-zygote'
        ];

        if (process.env.BROWSER_NO_SANDBOX === 'true') {
            console.warn('WARNING: Running browser without sandbox (RCE risk)');
            launchArgs.push('--no-sandbox');
            launchArgs.push('--disable-setuid-sandbox');
        }

        const browser = await chromium.launch({
            executablePath: chromiumPath,
            headless: true,
            proxy: proxy ? { server: proxy } : undefined,
            args: launchArgs
        });
        
        const context = await browser.newContext({
            viewport: { width: 1280, height: 720 },
            userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        });
        
        const page = await context.newPage();
        await page.goto('https://google.com');

        const sendScreenshot = async () => {
            try {
                if (page.isClosed()) return;
                const buffer = await page.screenshot({ type: 'jpeg', quality: 50 });
                socket.emit('screenshot', buffer.toString('base64'));
            } catch (e) {}
        };

        const interval = setInterval(sendScreenshot, 400);

        socket.on('mouseClick', async ({ x, y }) => {
            try { await page.mouse.click(x, y); await sendScreenshot(); } catch (e) {}
        });

        socket.on('type', async ({ text }) => {
            try { await page.keyboard.type(text); await sendScreenshot(); } catch (e) {}
        });

        socket.on('key', async ({ key }) => {
            try { await page.keyboard.press(key); await sendScreenshot(); } catch (e) {}
        });

        socket.on('goto', async ({ url }) => {
            try { await page.goto(url.startsWith('http') ? url : `https://${url}`); await sendScreenshot(); } catch (e) {}
        });

        socket.on('done', async () => {
            const cookies = await context.cookies();
            const storage = await page.evaluate(() => JSON.stringify(localStorage));
            fs.writeFileSync(sessionFile, JSON.stringify({ cookies, storage }, null, 2));
            socket.emit('captured', { success: true });
        });

        socket.on('disconnect', async () => {
            clearInterval(interval);
            await browser.close();
        });
    });

    server.listen(port, host, () => {
        console.log(`\n🚀 BROWSER AUTH SERVER READY`);
        console.log(`URL: http://${host === '0.0.0.0' ? 'YOUR_IP' : host}:${port}/?token=${token}\n`);
    });

    return server;
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const port = parseInt(args[0]) || 19191;
    const sessionFile = args[1] || 'session.json';
    const host = process.env.AUTH_HOST || '127.0.0.1';
    const token = process.env.AUTH_TOKEN || crypto.randomBytes(16).toString('hex');
    startServer({ port, host, sessionFile, token });
}

module.exports = { startServer };
