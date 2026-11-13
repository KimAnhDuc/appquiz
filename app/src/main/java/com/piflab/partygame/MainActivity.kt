package com.piflab.partygame

import android.annotation.SuppressLint
import android.os.Bundle
import android.view.KeyEvent
import android.view.WindowManager
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.net.Inet4Address
import java.net.NetworkInterface
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit

/**
 * The TV is the game host: it runs the HTTP server + game engine and shows
 * the big screen (tv.html) in a fullscreen WebView. Phones join via QR code.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var engine: QuizEngine
    private var updater: ScheduledExecutorService? = null
    private var server: GameServer? = null
    private var ticker: ScheduledExecutorService? = null
    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        webView = WebView(this).apply {
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.mediaPlaybackRequiresUserGesture = false
            webViewClient = WebViewClient()
            isFocusable = false
            setBackgroundColor(0xFF14101F.toInt())
        }
        setContentView(webView)

        // Questions: last downloaded set if any, otherwise the small bundled set. Then refresh from the web.
        val store = ContentStore(this, getString(R.string.content_base_url))
        engine = QuizEngine(store.loadCached() ?: QuestionBank.loadBundled(this))
        engine.joinUrl = localIpAddress()?.let { "http://$it:$PORT" }.orEmpty()

        try {
            server = GameServer(applicationContext, engine, PORT).also { it.start(SOCKET_TIMEOUT_MS, false) }
        } catch (e: Exception) {
            Toast.makeText(this, R.string.server_failed, Toast.LENGTH_LONG).show()
            finish()
            return
        }

        ticker = Executors.newSingleThreadScheduledExecutor().also {
            it.scheduleAtFixedRate({ engine.tick() }, 1, 1, TimeUnit.SECONDS)
        }

        if (store.enabled) {
            updater = Executors.newSingleThreadScheduledExecutor().also {
                it.scheduleWithFixedDelay(
                    { store.update()?.let(engine::setBank) },
                    0, ContentStore.UPDATE_INTERVAL_MIN, TimeUnit.MINUTES
                )
            }
        }

        webView.loadUrl("http://127.0.0.1:$PORT/tv")
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent): Boolean {
        return when (keyCode) {
            KeyEvent.KEYCODE_DPAD_CENTER, KeyEvent.KEYCODE_ENTER, KeyEvent.KEYCODE_NUMPAD_ENTER,
            KeyEvent.KEYCODE_BUTTON_A, KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE -> {
                if (!engine.startOrRestart() && engine.isInLobby()) {
                    Toast.makeText(this, "Chưa có ai vào phòng – quét mã QR để tham gia", Toast.LENGTH_SHORT).show()
                }
                true
            }
            else -> super.onKeyDown(keyCode, event)
        }
    }

    /** Prefer Wi-Fi/Ethernet private addresses (192.168.x, 10.x, 172.16-31.x). */
    private fun localIpAddress(): String? {
        val addresses = NetworkInterface.getNetworkInterfaces().asSequence()
            .filter { it.isUp && !it.isLoopback }
            .flatMap { it.inetAddresses.asSequence() }
            .filterIsInstance<Inet4Address>()
            .toList()
        return (addresses.firstOrNull { it.isSiteLocalAddress } ?: addresses.firstOrNull())?.hostAddress
    }

    override fun onDestroy() {
        ticker?.shutdownNow()
        updater?.shutdownNow()
        server?.stop()
        webView.destroy()
        super.onDestroy()
    }

    companion object {
        private const val PORT = 8080
        private const val SOCKET_TIMEOUT_MS = 10_000
    }
}
