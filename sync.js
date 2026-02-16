const { exec } = require("child_process")
const fs = require("fs")
const { normalizeArabic } = require("./utils")

const DOWNLOAD_DIR = "/tmp/downloads"
const SYNC_DIR = "/tmp/synced"

function downloadFile(url, output) {
    return new Promise((resolve, reject) => {
        exec(`curl -L "${url}" -o "${output}"`, (err) => {
            if (err) reject(err)
            else resolve()
        })
    })
}

async function syncSubtitles(videoUrl, subtitleUrl, id) {

    const subtitlePath = `${DOWNLOAD_DIR}/${id}.srt`
    const outputPath = `${SYNC_DIR}/${id}_synced.srt`

    await downloadFile(subtitleUrl, subtitlePath)

    return new Promise((resolve, reject) => {
        exec(`ffsubsync "${videoUrl}" -i "${subtitlePath}" -o "${outputPath}"`, (err) => {
            if (err) return reject(err)

            let content = fs.readFileSync(outputPath, "utf8")
            content = normalizeArabic(content)
            fs.writeFileSync(outputPath, content)

            resolve({
                id: id + "_synced",
                lang: "ara",
                url: `/file/${id}`
            })
        })
    })
}

module.exports = { syncSubtitles }
