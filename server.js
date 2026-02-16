const express = require("express");
const { serveHTTP } = require("stremio-addon-sdk");
const addonInterface = require("./addon");

const app = express();
const PORT = process.env.PORT || 10000;

// تشغيل إضافة Stremio
serveHTTP(addonInterface, { port: PORT, path: "/manifest.json" });

// رابط تقديم الترجمة
app.get("/subtitles/sync/:mediaId.srt", (req, res) => {
    const srtContent = `1\n00:00:01,000 --> 00:00:10,000\nتم تفعيل المزامنة العربية الذكية ✅\n(Arabic Auto-Sync is Active)`;
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.send(srtContent);
});

console.log(`Server is ready on port ${PORT}`);
