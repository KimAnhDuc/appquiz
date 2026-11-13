package com.piflab.partygame

import android.content.Context
import org.json.JSONObject

/**
 * One multiple-choice question. [answer] is the index (0-3) of the correct option.
 * [image] is ready to put in an <img src>: either a server-relative path ("/img/x.svg", bundled in the APK)
 * or an absolute https URL (online content).
 */
data class Question(
    val category: String,
    val text: String,
    val options: List<String>,
    val answer: Int,
    val image: String?,
    val emoji: String?
) {
    /** Same question with options in random order (so the correct answer isn't always A). */
    fun shuffled(): Question {
        val order = options.indices.shuffled()
        return copy(options = order.map { options[it] }, answer = order.indexOf(answer))
    }
}

/** A parsed question set plus where it came from (shown on the TV lobby). */
data class QuestionSet(val questions: List<Question>, val version: String, val source: String)

object QuestionBank {
    /** Offline fallback shipped inside the APK (assets/questions.json). */
    fun loadBundled(context: Context): QuestionSet {
        val text = context.assets.open("questions.json").bufferedReader(Charsets.UTF_8).use { it.readText() }
        return QuestionSet(parse(text, imageBase = null), "bundled", "offline")
    }

    /**
     * Parses a questions.json. Entries without exactly 4 options are skipped.
     * Relative image paths are resolved against [imageBase] (online content) or served from the APK (null).
     */
    fun parse(json: String, imageBase: String?): List<Question> {
        val arr = JSONObject(json).getJSONArray("questions")
        val result = ArrayList<Question>(arr.length())
        for (i in 0 until arr.length()) {
            val o = arr.getJSONObject(i)
            val opts = o.optJSONArray("options") ?: continue
            if (opts.length() != 4) continue
            val answer = o.optInt("answer", 0)
            if (answer !in 0..3) continue
            val text = o.optString("q")
            if (text.isBlank()) continue
            result += Question(
                category = o.optString("category", "Tổng hợp"),
                text = text,
                options = (0 until 4).map { opts.getString(it) },
                answer = answer,
                image = resolveImage(o.optString("image"), imageBase),
                emoji = o.optString("emoji").takeIf { it.isNotBlank() }
            )
        }
        return result
    }

    private fun resolveImage(raw: String, imageBase: String?): String? {
        val path = raw.trim()
        return when {
            path.isEmpty() -> null
            path.startsWith("http://") || path.startsWith("https://") -> path
            imageBase != null -> imageBase + path.trimStart('/')
            else -> "/" + path.trimStart('/')
        }
    }
}
