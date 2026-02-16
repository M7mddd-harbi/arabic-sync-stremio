const { addonBuilder } = require("stremio-addon-sdk");

const manifest = {
    id: "org.arabic-sync-addon",
    version: "1.0.0",
    name: "Arabic Auto-Sync Subtitles",
    description: "Automatic Arabic subtitle normalization and sync.",
    resources: ["subtitles"],
    types: ["movie", "series"],
    idPrefixes: ["tt"],
    catalogs: []
};

const builder = new addonBuilder(manifest);

builder.defineSubtitlesHandler(async (args) => {
    const { type, id } = args;
    const subtitles = [
        {
            id: `sync-ara-${id}`,
            url: `https://arabic-sync-stremio.onrender.com/subtitles/sync/${id}`,
            lang: "ara"
        }
    ];
    return Promise.resolve({ subtitles } );
});

module.exports = builder.getInterface();
