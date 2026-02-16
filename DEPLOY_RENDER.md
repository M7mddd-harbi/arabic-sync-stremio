const { addonBuilder } = require("stremio-addon-sdk");

const manifest = {
    id: "org.arabic-sync-addon",
    version: "1.0.0",
    name: "Arabic Auto-Sync Subtitles",
    description: "Automatic Arabic subtitle synchronization using audio fingerprinting and reference-based alignment.",
    resources: ["subtitles"],
    types: ["movie", "series"],
    idPrefixes: ["tt"], // Supports IMDb IDs
    catalogs: [],
    contactEmail: "support@example.com",
    logo: "https://example.com/logo.png"
};

const builder = new addonBuilder(manifest);

builder.defineSubtitlesHandler(async (args) => {
    const { type, id } = args;
    console.log(`Subtitle request for ${type} ${id}`);

    // This is where we will implement the logic to:
    // 1. Check cache for existing synced subtitles
    // 2. Fetch original Arabic subtitles from providers (e.g., OpenSubtitles)
    // 3. Trigger background sync if not already done
    // 4. Return the list of available (and placeholder) subtitles

    const subtitles = [
        {
            id: `sync-ara-${id}`,
            url: `http://localhost:7000/subtitles/sync/${id}`,
            lang: "ara"
        }
    ];

    return Promise.resolve({ subtitles });
});

module.exports = builder.getInterface();
