const { addonBuilder } = require("stremio-addon-sdk")
const express = require("express")
const NodeCache = require("node-cache")
const fs = require("fs")
const { syncSubtitles } = require("./sync")

const app = express()
const cache = new NodeCache({ stdTTL: 86400 }) // 1 يوم

const DOWNLOAD_DIR = "/tmp/downloads"
const SYNC_DIR = "/tmp/synced"

if (!fs.existsSync(DOWNLOAD_DIR)) fs.mkdirSync(DOWNLOAD_DIR, { recursive: true })
if (!fs.existsSync(SYNC_DIR)) fs.mkdirSync(SYNC_DIR, { recursive: true })

const builder = new addonBuilder({
    id: "org.arabic.autosync",
    version: "1.0.0",
    name: "Arabic Auto-Sync Subtitles",
    description: "Auto sync Arabic subtitles using FFsubsync",
    resources: ["subtitles"],
    types: ["movie", "series"],
    idPrefixes: ["tt"]
})

// تعريف handler للنصوص المترجمة
builder.defineSubtitlesHandler(async ({ id }) => {
    const cached = cache.get(id)
    if (cached) return { subtitles: cached }
    return { subtitles: [] }
})

// نقطة الوصول لملف manifest.json
app.get("/manifest.json", (req, res) => {
    res.json(builder.getManifest())
})

// نقطة الوصول لمزامنة الترجمة
app.get("/sync", async (req, res) => {
    const { videoUrl, subtitleUrl, id } = req.query
    if (!videoUrl || !subtitleUrl || !id)
        return res.status(400).send("Missing parameters")

    try {
        const result = await syncSubtitles(videoUrl, subtitleUrl, id)
        cache.set(id, [result])
        res.json([result])
    } catch (err) {
        console.error(err)
        res.status(500).send("Sync failed")
    }
})

// تنزيل الملف بعد المزامنة
app.get("/file/:id", (req, res) => {
    const filePath = `${SYNC_DIR}/${req.params.id}_synced.srt`
    if (fs.existsSync(filePath)) {
        res.download(filePath)
    } else {
        res.status(404).send("File not found")
    }
})

// استخدام واجهة stremio-addon-sdk الصحيحة مع Express
app.use("/", builder.getInterface().getRouter()) // <= هذا التعديل المهم

const PORT = process.env.PORT || 10000
app.listen(PORT, () => console.log("Addon running on port " + PORT))


