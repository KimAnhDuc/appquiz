package com.piflab.partygame

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Color
import com.google.zxing.BarcodeFormat
import com.google.zxing.EncodeHintType
import com.google.zxing.qrcode.QRCodeWriter
import fi.iki.elonen.NanoHTTPD
import org.json.JSONObject
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream

/**
 * HTTP server running on the TV.
 *   GET  /            -> phone controller page
 *   GET  /tv          -> TV screen page (loaded by the TV's own WebView)
 *   GET  /img/<file>  -> question images from assets/img
 *   GET  /qr.png      -> QR code of the join URL
 *   GET  /api/state   -> game state (?pid=... for a phone)
 *   POST /api/join | /api/start | /api/again | /api/answer
 */
class GameServer(
    private val context: Context,
    private val engine: QuizEngine,
    port: Int
) : NanoHTTPD(port) {

    private val pageCache = HashMap<String, String>()
    private var qrCache: Pair<String, ByteArray>? = null

    override fun serve(session: IHTTPSession): Response {
        return try {
            route(session)
        } catch (e: Exception) {
            json(Response.Status.INTERNAL_ERROR, JSONObject().put("error", e.message ?: "error"))
        }
    }

    private fun route(session: IHTTPSession): Response {
        val uri = session.uri
        if (session.method == Method.GET) {
            if (uri.startsWith("/img/")) return image(uri.removePrefix("/img/"))
            return when (uri) {
                "/" -> html("phone.html")
                "/tv" -> html("tv.html")
                "/qr.png" -> qrPng()
                "/api/state" -> json(Response.Status.OK, engine.state(param(session, "pid").ifEmpty { null }))
                else -> notFound()
            }
        }
        if (session.method != Method.POST) return notFound()

        session.parseBody(HashMap())
        val pid = param(session, "pid")
        return when (uri) {
            "/api/join" -> when (val r = engine.join(param(session, "name"))) {
                is QuizEngine.JoinResult.Ok -> ok(JSONObject().put("pid", r.player.id))
                is QuizEngine.JoinResult.Error -> fail(r.message)
            }
            "/api/start" -> result(engine.start(pid), "Chỉ VIP mới bắt đầu được")
            "/api/again" -> result(engine.playAgain(pid), "Không thể chơi lại lúc này")
            "/api/answer" -> result(
                engine.answer(pid, param(session, "choice").toIntOrNull() ?: -1),
                "Hết giờ hoặc bạn đã trả lời rồi"
            )
            else -> notFound()
        }
    }

    private fun param(session: IHTTPSession, name: String): String =
        session.parameters[name]?.firstOrNull()?.trim().orEmpty()

    private fun html(asset: String): Response {
        val body = synchronized(pageCache) {
            pageCache.getOrPut(asset) {
                context.assets.open(asset).bufferedReader(Charsets.UTF_8).use { it.readText() }
            }
        }
        return newFixedLengthResponse(Response.Status.OK, "text/html; charset=utf-8", body).noStore()
    }

    private fun image(name: String): Response {
        if (name.isEmpty() || name.contains("..") || name.contains('/') || name.contains('\\')) return notFound()
        val mime = when (name.substringAfterLast('.').lowercase()) {
            "svg" -> "image/svg+xml"
            "png" -> "image/png"
            "jpg", "jpeg" -> "image/jpeg"
            "webp" -> "image/webp"
            "gif" -> "image/gif"
            else -> return notFound()
        }
        val bytes = try {
            context.assets.open("img/$name").use { it.readBytes() }
        } catch (e: java.io.IOException) {
            return notFound()
        }
        return newFixedLengthResponse(Response.Status.OK, mime, ByteArrayInputStream(bytes), bytes.size.toLong())
    }

    private fun qrPng(): Response {
        val url = engine.joinUrl
        if (url.isEmpty()) return notFound()
        val bytes = synchronized(this) {
            qrCache?.takeIf { it.first == url }?.second ?: renderQr(url).also { qrCache = url to it }
        }
        return newFixedLengthResponse(Response.Status.OK, "image/png", ByteArrayInputStream(bytes), bytes.size.toLong())
    }

    private fun renderQr(text: String): ByteArray {
        val size = 480
        val matrix = QRCodeWriter().encode(
            text, BarcodeFormat.QR_CODE, size, size, mapOf(EncodeHintType.MARGIN to 2)
        )
        val pixels = IntArray(size * size) { i ->
            if (matrix.get(i % size, i / size)) Color.BLACK else Color.WHITE
        }
        val bitmap = Bitmap.createBitmap(pixels, size, size, Bitmap.Config.ARGB_8888)
        return ByteArrayOutputStream().use { out ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
            bitmap.recycle()
            out.toByteArray()
        }
    }

    private fun result(success: Boolean, error: String) =
        if (success) ok(JSONObject()) else fail(error)

    private fun ok(body: JSONObject) = json(Response.Status.OK, body.put("ok", true))

    private fun fail(message: String) =
        json(Response.Status.OK, JSONObject().put("ok", false).put("error", message))

    private fun json(status: Response.Status, body: JSONObject): Response =
        newFixedLengthResponse(status, "application/json; charset=utf-8", body.toString()).noStore()

    private fun notFound() = newFixedLengthResponse(Response.Status.NOT_FOUND, "text/plain", "Not found")

    private fun Response.noStore() = apply { addHeader("Cache-Control", "no-store") }
}
