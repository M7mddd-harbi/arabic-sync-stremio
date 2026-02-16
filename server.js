require("dotenv").config();
const express = require("express");
const { serveHTTP } = require("stremio-addon-sdk");
const addonInterface = require("./addon");
const path = require("path");
const fs = require("fs");
const multer = require("multer");

const app = express();
const PORT = process.env.PORT || 7000;

const upload = multer({ dest: "uploads/" });

// Serve the Stremio Addon
serveHTTP(addonInterface, { port: PORT, path: "/manifest.json" });

const { spawn } = require("child_process");

// Subtitle Proxy & Processing Endpoint
app.get("/subtitles/sync/:mediaId", async (req, res) => {
    const { mediaId } = req.params;
    const videoUrl = req.query.videoUrl; // In real usage, we'd resolve this via Stremio stream
    const originalSrtUrl = req.query.srtUrl; // Original unsynced Arabic SRT
    
    const cacheDir = path.join(__dirname, "cache");
    const syncedPath = path.join(cacheDir, `${mediaId}.srt`);
    const processingFlag = path.join(cacheDir, `${mediaId}.processing`);

    if (fs.existsSync(syncedPath)) {
        res.setHeader("Content-Type", "text/plain; charset=utf-8");
        return res.sendFile(syncedPath);
    }

    // If already processing, return placeholder
    if (fs.existsSync(processingFlag)) {
        res.setHeader("Content-Type", "text/plain; charset=utf-8");
        return res.send(`1\n00:00:01,000 --> 00:00:10,000\nجاري المزامنة... يرجى المحاولة لاحقاً.\n(Still syncing, try again in a moment...)`);
    }

    // Start background sync if we have the necessary URLs
    if (videoUrl && originalSrtUrl) {
        fs.writeFileSync(processingFlag, "true");
        
        const inputSrt = path.join(cacheDir, `${mediaId}_input.srt`);
        
        // Download original SRT first
        try {
            const axios = require("axios");
            const response = await axios.get(originalSrtUrl);
            fs.writeFileSync(inputSrt, response.data);

            const pythonProcess = spawn("python3", [
                path.join(__dirname, "sync_engine.py"),
                videoUrl,
                inputSrt,
                syncedPath
            ]);

            pythonProcess.on("close", (code) => {
                fs.unlinkSync(processingFlag);
                if (fs.existsSync(inputSrt)) fs.unlinkSync(inputSrt);
                console.log(`Sync for ${mediaId} finished with code ${code}`);
            });
        } catch (err) {
            console.error("Failed to start sync:", err);
            if (fs.existsSync(processingFlag)) fs.unlinkSync(processingFlag);
        }
    }

    // Anti-Timeout Strategy: Return placeholder if not ready
    res.setHeader("Content-Type", "text/plain; charset=utf-8");
    res.send(`1
00:00:01,000 --> 00:00:10,000
جاري مزامنة الترجمة العربية... يرجى الانتظار قليلاً.
(Arabic Auto-Sync is processing...)
`);
});

// Create necessary directories
["cache", "uploads"].forEach(dir => {
    const dirPath = path.join(__dirname, dir);
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath);
    }
});

// Local File Upload Endpoint
app.post("/upload-local-srt", upload.single("subtitle"), (req, res) => {
    if (!req.file) return res.status(400).send("No file uploaded.");
    
    const mediaId = req.body.mediaId || "local";
    const videoUrl = req.body.videoUrl;
    
    const targetPath = path.join(__dirname, "cache", `${mediaId}_local_input.srt`);
    fs.renameSync(req.file.path, targetPath);
    
    // Trigger sync if videoUrl is provided
    if (videoUrl) {
        const syncedPath = path.join(__dirname, "cache", `${mediaId}_local_synced.srt`);
        const pythonProcess = spawn("python3", [
            path.join(__dirname, "sync_engine.py"),
            videoUrl,
            targetPath,
            syncedPath
        ]);
        
        pythonProcess.on("close", (code) => {
            console.log(`Local sync for ${mediaId} finished with code ${code}`);
        });
    }

    res.json({ 
        message: "File uploaded and sync started", 
        url: `http://localhost:${PORT}/subtitles/sync/${mediaId}_local` 
    });
});

console.log(`Addon is running at http://localhost:${PORT}/manifest.json`);
