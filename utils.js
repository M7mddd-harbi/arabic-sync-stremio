function normalizeArabic(text) {
    return text
        .replace(/[\u064B-\u0652]/g, "")
        .replace(/ـ/g, "")
}

module.exports = { normalizeArabic }
