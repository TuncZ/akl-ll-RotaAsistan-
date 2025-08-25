const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const csv = require('csv-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Frontend dosyalarını sunmak için middleware
app.use(express.static(path.join(__dirname, 'public')));

// API Endpoint: /api/getUcret
// Örnek istek: /api/getUcret?yer=AvrasyaTüneli&yil=2026&aracSinifi=1
app.get('/api/getUcret', (req, res) => {
    const { yer, yil, aracSinifi } = req.query;
    const currentYear = new Date().getFullYear();

    if (parseInt(yil, 10) <= currentYear) {
        // Geçmiş veya mevcut yıl: CSV'den veri oku
        const results = [];
        fs.createReadStream(path.join(__dirname, 'data', 'gecis_ucretleri.csv'))
            .pipe(csv())
            .on('data', (data) => {
                if (data.yer === yer && data.yil === yil && data.arac_sinifi === aracSinifi) {
                    results.push(data);
                }
            })
            .on('end', () => {
                if (results.length > 0) {
                    res.json({ ucret: parseFloat(results[0].ucret) });
                } else {
                    res.status(404).json({ error: 'Geçmiş veri bulunamadı.' });
                }
            });
    } else {
        // Gelecek yıl: Python AI modelini çağır
        const pythonProcess = spawn('python', [
            path.join(__dirname, 'ai_model', 'predict_toll.py'),
            JSON.stringify({ yer, yil, aracSinifi }) // Ekonomik verileri de ekleyebilirsin
        ]);

        pythonProcess.stdout.on('data', (data) => {
            try {
                const result = JSON.parse(data.toString());
                res.json({ ucret: result.tahmini_ucret });
            } catch (e) {
                res.status(500).json({ error: 'AI modelinden geçersiz yanıt.' });
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
            res.status(500).json({ error: 'AI modelinde bir hata oluştu.' });
        });
    }
});

app.listen(PORT, () => {
    console.log(`Sunucu http://localhost:${PORT} adresinde çalışıyor.`);
});