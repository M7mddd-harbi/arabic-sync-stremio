const { addonBuilder } = require("stremio-addon-sdk");

const manifest = {
    id: "org.arabic.autosync.final",
    version: "1.1.0",
    name: "Arabic Auto-Sync ✅",
    description: "مزامنة ومعالجة الترجمة العربية تلقائياً",
    resources: ["subtitles"],
    types: ["movie", "series"],
    idPrefixes: ["tt"]
};

const builder = new addonBuilder(manifest);

builder.defineSubtitlesHandler(async (args) => {
    const { id } = args;
    return Promise.resolve({ 
        subtitles: [
            {
                id: `sync-ara-${id}`,
                url: `https://arabic-sync-stremio.onrender.com/subtitles/sync/${id}.srt`,
                lang: "ara",
                label: "Arabic Auto-Sync ✅"
            }
        ] 
    } );
});

module.exports = builder.getInterface();
