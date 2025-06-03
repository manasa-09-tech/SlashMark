'use strict';

require('dotenv').config();
console.log("Encryption key:", process.env.ENCRYPTION_KEY);
const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');

const app = express();
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || '12345678901234567890123456789012';
const IV_LENGTH = 16;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

function encrypt(text) {
    let iv = Buffer.alloc(16, 0); // static IV of 16 bytes of zero
    let cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv);
    let encrypted = cipher.update(text, 'utf8');
    encrypted = Buffer.concat([encrypted, cipher.final()]);
    return iv.toString('hex') + ':' + encrypted.toString('hex');
}

function decrypt(text) {
    let textParts = text.split(':');
    let iv = Buffer.from(textParts.shift(), 'hex');
    let encryptedText = Buffer.from(textParts.join(':'), 'hex');
    let decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv);
    let decrypted = decipher.update(encryptedText);
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    return decrypted.toString();
}

const html = `
<!DOCTYPE html>
<html>
<head><title>Encryption App</title></head>
<body>
  <h2>Encrypt Text</h2>
  <form method="POST" action="/encrypt">
    <input type="text" name="text" placeholder="Enter text" required />
    <button type="submit">Encrypt</button>
  </form>
  
  <h2>Decrypt Text</h2>
  <form method="POST" action="/decrypt">
    <input type="text" name="text" placeholder="Enter encrypted text" required />
    <button type="submit">Decrypt</button>
  </form>
</body>
</html>
`;

app.get('/', (req, res) => res.send(html));

app.post('/encrypt', (req, res) => {
    const encrypted = encrypt(req.body.text);
    res.send(`<p>Encrypted: ${encrypted}</p><a href="/">Back</a>`);
});

app.post('/decrypt', (req, res) => {
    try {
        const decrypted = decrypt(req.body.text);
        res.send(`<p>Decrypted: ${decrypted}</p><a href="/">Back</a>`);
    } catch (err) {
        res.send(`<p>Decryption failed. Invalid input or key.</p><a href="/">Back</a>`);
    }
});

app.listen(3000, () => {
    console.log('Server running at http://localhost:3000');
});