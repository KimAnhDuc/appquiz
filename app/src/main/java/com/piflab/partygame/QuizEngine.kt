package com.piflab.partygame

import org.json.JSONArray
import org.json.JSONObject
import java.util.UUID
import kotlin.math.roundToInt

/**
 * "Đố Vui" – a Kahoot-style multiple-choice quiz.
 *
 * LOBBY    -> players join from their phones; the VIP (first player) or the TV remote starts.
 * QUESTION -> TV shows question (+ image), phones show 4 boxes A/B/C/D.
 *             Ends early when every active player has answered.
 * REVEAL   -> correct answer, how many picked each option, points gained, leaderboard.
 * FINAL    -> after [questionsPerGame] questions: total scores and the champion.
 *
 * Scoring: correct answer = 500 + up to 500 speed bonus (faster = more). Wrong/no answer = 0.
 *
 * All public methods are synchronized: they are called from NanoHTTPD worker threads
 * and from the 1-second ticker.
 */
class QuizEngine(
    initial: QuestionSet,
    private val questionsPerGame: Int = 10
) {
    enum class Phase { LOBBY, QUESTION, REVEAL, FINAL }

    class Player(val id: String, val name: String, val color: String) {
        var score = 0
        var correct = 0
        var lastGain = 0
        /** true/false = answered right/wrong last question, null = didn't answer. */
        var lastCorrect: Boolean? = null
        var lastSeen = System.currentTimeMillis()
    }

    private class Answer(val choice: Int, val at: Long)

    private var phase = Phase.LOBBY
    private val players = LinkedHashMap<String, Player>()
    private var game = listOf<Question>()
    private var index = -1
    private val answers = LinkedHashMap<String, Answer>()
    private var deadline = 0L
    private val deck = ArrayDeque<Question>()
    private var bank = initial.questions
    private var bankVersion = initial.version
    private var bankSource = initial.source

    @Volatile
    var joinUrl: String = ""

    private val current: Question? get() = game.getOrNull(index)

    /** Swap in a freshly downloaded question set. A game in progress keeps its already-drawn questions. */
    @Synchronized
    fun setBank(set: QuestionSet) {
        if (set.questions.isEmpty()) return
        bank = set.questions
        bankVersion = set.version
        bankSource = set.source
        deck.clear()
    }

    // ---------- Player actions ----------

    sealed class JoinResult {
        data class Ok(val player: Player) : JoinResult()
        data class Error(val message: String) : JoinResult()
    }

    /** Joining is allowed at any time; late joiners simply start from 0 points. */
    @Synchronized
    fun join(rawName: String): JoinResult {
        if (players.size >= MAX_PLAYERS) return JoinResult.Error("Phòng đã đủ $MAX_PLAYERS người")
        val base = rawName.trim().replace(Regex("\\s+"), " ").take(MAX_NAME_LEN)
        if (base.isEmpty()) return JoinResult.Error("Vui lòng nhập tên")

        var name = base
        var n = 2
        while (players.values.any { it.name.equals(name, ignoreCase = true) }) {
            name = "$base $n"
            n++
        }
        val usedColors = players.values.map { it.color }.toSet()
        val color = COLORS.firstOrNull { it !in usedColors } ?: COLORS[players.size % COLORS.size]
        val player = Player(UUID.randomUUID().toString().take(8), name, color)
        players[player.id] = player
        return JoinResult.Ok(player)
    }

    /** Start from a phone: only the VIP may do it. */
    @Synchronized
    fun start(pid: String): Boolean = pid == vipId() && startOrRestart()

    /** OK button on the TV remote: start in the lobby, back to lobby from the final screen. */
    @Synchronized
    fun startOrRestart(): Boolean = when (phase) {
        Phase.LOBBY -> if (players.size >= MIN_PLAYERS && bank.isNotEmpty()) { startGame(); true } else false
        Phase.FINAL -> { phase = Phase.LOBBY; true }
        else -> false
    }

    @Synchronized
    fun isInLobby(): Boolean = phase == Phase.LOBBY

    @Synchronized
    fun playAgain(pid: String): Boolean {
        if (pid != vipId() || phase != Phase.FINAL) return false
        phase = Phase.LOBBY
        return true
    }

    @Synchronized
    fun answer(pid: String, choice: Int): Boolean {
        if (phase != Phase.QUESTION || pid !in players || pid in answers || choice !in 0..3) return false
        answers[pid] = Answer(choice, System.currentTimeMillis())
        if (activePlayers().all { it.id in answers }) reveal()
        return true
    }

    // ---------- Clock ----------

    @Synchronized
    fun tick() {
        val now = System.currentTimeMillis()
        when (phase) {
            Phase.LOBBY -> players.values.removeAll { now - it.lastSeen > LOBBY_TIMEOUT_MS }
            Phase.QUESTION -> if (now >= deadline) reveal()
            Phase.REVEAL -> if (now >= deadline) {
                if (index + 1 >= game.size) phase = Phase.FINAL else nextQuestion()
            }
            Phase.FINAL -> Unit
        }
    }

    // ---------- Transitions ----------

    private fun startGame() {
        players.values.forEach {
            it.score = 0
            it.correct = 0
            it.lastGain = 0
            it.lastCorrect = null
        }
        game = drawQuestions()
        index = -1
        nextQuestion()
    }

    /** Draw from a shuffled deck so questions don't repeat until the whole bank is used. */
    private fun drawQuestions(): List<Question> {
        val count = minOf(questionsPerGame, bank.size)
        return List(count) {
            if (deck.isEmpty()) deck.addAll(bank.shuffled())
            deck.removeFirst().shuffled()
        }
    }

    private fun nextQuestion() {
        index++
        answers.clear()
        phase = Phase.QUESTION
        deadline = System.currentTimeMillis() + QUESTION_SEC * 1000L
    }

    private fun reveal() {
        val q = current ?: return
        val duration = QUESTION_SEC * 1000.0
        for (p in players.values) {
            val a = answers[p.id]
            p.lastCorrect = a?.let { it.choice == q.answer }
            p.lastGain = if (a != null && a.choice == q.answer) {
                val speed = ((deadline - a.at) / duration).coerceIn(0.0, 1.0)
                BASE_POINTS + (SPEED_BONUS * speed).roundToInt()
            } else 0
            p.score += p.lastGain
            if (p.lastCorrect == true) p.correct++
        }
        phase = Phase.REVEAL
        deadline = System.currentTimeMillis() + REVEAL_SEC * 1000L
    }

    // ---------- Helpers ----------

    private fun vipId(): String? = players.keys.firstOrNull()

    /** Players whose phone polled recently; disconnected phones don't block the question. */
    private fun activePlayers(): List<Player> {
        val now = System.currentTimeMillis()
        return players.values.filter { now - it.lastSeen <= ACTIVE_TIMEOUT_MS }
    }

    private fun ranking(): List<Player> =
        players.values.sortedWith(compareByDescending<Player> { it.score }.thenByDescending { it.correct })

    // ---------- State for clients ----------

    /** Snapshot for the TV (pid == null) or for one phone. Also marks that phone as alive. */
    @Synchronized
    fun state(pid: String?): JSONObject {
        val now = System.currentTimeMillis()
        val me = pid?.let { players[it] }
        me?.lastSeen = now

        val timed = phase == Phase.QUESTION || phase == Phase.REVEAL
        val json = JSONObject()
            .put("phase", phase.name)
            .put("index", index + 1)
            .put("total", game.size.takeIf { it > 0 } ?: minOf(questionsPerGame, bank.size))
            .put("remaining", if (timed) ((deadline - now + 999) / 1000).coerceAtLeast(0) else 0)
            .put("duration", QUESTION_SEC)
            .put("joinUrl", joinUrl)
            .put("minPlayers", MIN_PLAYERS)
            .put("bank", JSONObject().put("count", bank.size).put("version", bankVersion).put("source", bankSource))

        val vip = vipId()
        val ranked = ranking()
        val playersJson = JSONArray()
        players.values.forEach { p ->
            playersJson.put(
                JSONObject()
                    .put("id", p.id)
                    .put("name", p.name)
                    .put("color", p.color)
                    .put("score", p.score)
                    .put("correct", p.correct)
                    .put("vip", p.id == vip)
                    .put("active", now - p.lastSeen <= ACTIVE_TIMEOUT_MS)
                    .put("done", phase == Phase.QUESTION && p.id in answers)
                    .put("lastGain", p.lastGain)
                    .put("lastCorrect", p.lastCorrect ?: JSONObject.NULL)
            )
        }
        json.put("players", playersJson)

        if (me != null) {
            json.put(
                "me", JSONObject()
                    .put("id", me.id)
                    .put("name", me.name)
                    .put("color", me.color)
                    .put("score", me.score)
                    .put("correct", me.correct)
                    .put("vip", me.id == vip)
                    .put("choice", answers[me.id]?.choice ?: JSONObject.NULL)
                    .put("lastGain", me.lastGain)
                    .put("lastCorrect", me.lastCorrect ?: JSONObject.NULL)
                    .put("rank", ranked.indexOf(me) + 1)
            )
        }

        val q = current
        if (q != null && timed) {
            val qj = JSONObject()
                .put("category", q.category)
                .put("text", q.text)
                .put("image", q.image ?: JSONObject.NULL)
                .put("emoji", q.emoji ?: JSONObject.NULL)
                .put("options", JSONArray(q.options))
            if (phase == Phase.REVEAL) {
                val counts = IntArray(4)
                answers.values.forEach { counts[it.choice]++ }
                qj.put("answer", q.answer).put("counts", JSONArray(counts.toList()))
            }
            json.put("question", qj)
            // Let the TV start downloading the next picture while players are still answering.
            json.put("preload", game.getOrNull(index + 1)?.image ?: JSONObject.NULL)
        }
        return json
    }

    companion object {
        const val MIN_PLAYERS = 1
        const val MAX_PLAYERS = 12
        const val MAX_NAME_LEN = 12
        const val QUESTION_SEC = 20
        const val REVEAL_SEC = 8
        const val BASE_POINTS = 500
        const val SPEED_BONUS = 500
        private const val ACTIVE_TIMEOUT_MS = 15_000L
        private const val LOBBY_TIMEOUT_MS = 30_000L
        private val COLORS = listOf(
            "#FF4F8B", "#42A5F5", "#66BB6A", "#FFCA28", "#AB47BC", "#FF7043",
            "#26C6DA", "#D4E157", "#8D6E63", "#EC407A", "#7E57C2", "#9CCC65"
        )
    }
}
