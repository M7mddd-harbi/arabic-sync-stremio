const express = require("express");
const { serveHTTP } = require("stremio-addon-sdk");
const addonInterface = require("./addon");
const path = require("path");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 10000;

// تشغيل إضافة Stremio
serveHTTP(addonInterface, { port: PORT, path: "/manifest.json" });

// نقطة معالجة الترجمة
app.get("/subtitles/sync/:mediaId", (req, res) => {
    const { mediaId } = req.params;
    
    // رسالة بسيطة تخبر المستخدم أن الإضافة تعمل
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.send(`1
00:00:01,000 --> 00:00:10,000
تم تشغيل إضافة المزامنة العربية بنجاح!
(Arabic Auto-Sync is Active)
`);
});

// إنشاء مجلد التخزين المؤقت
const cacheDir = path.join(__dirname, "cache");
if (!fs.existsSync(cacheDir)) {
    fs.mkdirSync(cacheDir);
}

console.log(`Addon is running on port ${PORT}`);
