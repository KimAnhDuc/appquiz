package com.piflab.partygame

import android.content.Context
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL

/**
 * Downloads the online question set and keeps a copy on the TV so the game also works offline.
 *
 * Online layout (any static host, e.g. GitHub Pages) – see quiz-content/ in the project:
 *   <base>/manifest.json   {"version": "...", "questions": "questions.json"}   (tiny, checked on every launch)
 *   <base>/questions.json  {"version": "...", "questions": [...]}              (downloaded only when the version changes)
 *   <base>/img/...         question pictures, loaded straight from the host by the TV's WebView
 *
 * To publish new questions: upload the new files to the host. TVs pick them up on next launch
 * (or within [UPDATE_INTERVAL_MIN] minutes while the app stays open). No APK reinstall needed.
 */
class ContentStore(context: Context, baseUrl: String) {

    private val base = baseUrl.trim().let { if (it.isNotEmpty() && !it.endsWith("/")) "$it/" else it }
    private val dir = File(context.filesDir, "content")
    private val dataFile = File(dir, "questions.json")
    private val versionFile = File(dir, "version.txt")

    val enabled: Boolean get() = base.isNotEmpty()

    /** The last downloaded set, or null if nothing is cached. */
    fun loadCached(): QuestionSet? {
        if (!enabled || !dataFile.exists()) return null
        return try {
            val questions = QuestionBank.parse(dataFile.readText(Charsets.UTF_8), base)
            if (questions.isEmpty()) null
            else QuestionSet(questions, versionFile.takeIf { it.exists() }?.readText()?.trim() ?: "?", "online (đã lưu)")
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Checks the manifest and downloads questions.json when the version changed.
     * Returns the new set, or null when already up to date or the network/host is unavailable.
     * Never throws: a failed update must not break the game.
     */
    fun update(): QuestionSet? {
        if (!enabled) return null
        return try {
            // Query string defeats CDN/browser caches so a freshly published version is seen immediately.
            val manifest = JSONObject(fetch("manifest.json?t=${System.currentTimeMillis()}", 8_000))
            val remoteVersion = manifest.getString("version")
            val cachedVersion = versionFile.takeIf { it.exists() }?.readText()?.trim()
            if (remoteVersion == cachedVersion && dataFile.exists()) return null

            val file = manifest.optString("questions", "questions.json")
            val body = fetch("$file?v=$remoteVersion", 60_000)
            val questions = QuestionBank.parse(body, base)
            if (questions.size < MIN_QUESTIONS) return null // refuse a broken/empty upload

            dir.mkdirs()
            val tmp = File(dir, "questions.json.tmp")
            tmp.writeText(body, Charsets.UTF_8)
            if (!tmp.renameTo(dataFile)) {
                dataFile.writeText(body, Charsets.UTF_8)
                tmp.delete()
            }
            versionFile.writeText(remoteVersion, Charsets.UTF_8)
            QuestionSet(questions, remoteVersion, "online")
        } catch (e: Exception) {
            null
        }
    }

    private fun fetch(path: String, timeoutMs: Int): String {
        val conn = URL(base + path).openConnection() as HttpURLConnection
        try {
            conn.connectTimeout = timeoutMs
            conn.readTimeout = timeoutMs
            conn.setRequestProperty("User-Agent", "DoVui-TV/1.0")
            conn.setRequestProperty("Cache-Control", "no-cache")
            if (conn.responseCode != HttpURLConnection.HTTP_OK) throw java.io.IOException("HTTP ${conn.responseCode}")
            return conn.inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() }
        } finally {
            conn.disconnect()
        }
    }

    companion object {
        const val UPDATE_INTERVAL_MIN = 30L
        private const val MIN_QUESTIONS = 20
    }
}
