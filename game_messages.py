START_TALE = """
⚡ *BLACKOUT INITIATED* ⚡

The grid has failed. Systems are down.
Someone among you has gone dark.

Find the corrupted before they eliminate everyone.

*Roles have been distributed. Check your private messages.*
"""

ROLE_BRIEFINGS = {
    'Blackout': """
🔴 *BLACKOUT (CORRUPT)*

You are part of the corrupted.
Kill one player per night.

*Teammates:* {teammates}
*Your team must eliminate all survivors.*

Coordinate with your team in secret.
Do NOT reveal yourself in public chat.
""",
    'Razor': """
🔴 *RAZOR (CORRUPT)*

You are part of the corrupted.
Kill one player per night.

*Special:* If someone kills you, they die too.
*Teammates:* {teammates}

Your revenge kill makes you dangerous.
Use it to protect yourself.
""",
    'Phantom': """
🔴 *PHANTOM (CORRUPT)*

You are part of the corrupted.
You cannot kill directly.

*Ability:* Mark one ability player per 2 rounds.
The mark becomes visible to your teammates after 1 day.

*Teammates:* {teammates}

Your marks help your team identify threats.
Choose wisely.
""",
    'Thug': """
🔴 *THUG (CORRUPT)*

You are part of the corrupted.
Kill one player per night.

*Teammates:* {teammates}

You are the muscle. Follow your team's lead.
""",
    'Virus': """
🟡 *VIRUS (NEUTRAL)*

You are a solo threat.
Kill one player per night (2 uses, cooldown between).

*Targets:* {targets}

You must eliminate your assigned targets to win.
You don't know who the other neutrals are.
""",
    'Wraith': """
🟡 *WRAITH (NEUTRAL)*

You are a solo threat.
Kill one player per night (2 uses, cooldown between).

*Win Condition:* Be the last one alive.

You don't know who the other neutrals are.
Trust no one.
""",
    'Glitch': """
🟡 *GLITCH (NEUTRAL)*

You are a solo threat.
You cannot kill directly.

*Ability:* Steal one dead player's role ability (one-time use).

*Win Condition:* Survive to endgame + use stolen ability.

Watch who dies. Choose your steal wisely.
""",
    'Plague': """
🟡 *PLAGUE (NEUTRAL)*

You are a solo threat.
You cannot kill directly.

*Ability:* Infect one player nightly. Infected players lose their next action.

*Win Condition:* Infect 3 players before game ends.

Spread your influence. Disable the survivors.
""",
    'Volt': """
🔵 *VOLT (SURVIVOR)*

You are a survivor. Protect the innocent.

*Ability:* Protect one player nightly.

*Limitations:*
- Can't protect yourself
- Can't protect same player 2x in a row
- You appear SUSPICIOUS on nights you use your ability

Your protection can save lives. Use it wisely.
""",
    'Grid': """
🔵 *GRID (SURVIVOR)*

You are a survivor. Find the corrupted.

*Ability:* Night scan one player. Result: CLEAN or SUSPICIOUS.

*Limitations:*
- Can't scan same player 2x in a row
- You appear SUSPICIOUS on nights you use your ability

Your scans are valuable. Don't waste them.
""",
    'Bunker': """
🔵 *BUNKER (SURVIVOR)*

You are a survivor. Control the threats.

*Ability:* Role-block one player nightly.

*Limitations:*
- Can't block same player 2x in a row

Your blocks can stop kills and abilities.
Use them strategically.
""",
    'Kernel': """
🔵 *KERNEL (SURVIVOR)*

You are a survivor. Uncover the truth.

*Ability:* One-time: reveal one player's exact role.

*Limitations:*
- One-time use only
- Can't use on yourself

Your revelation can expose the corrupted.
Choose your target carefully.
""",
    'Flare': """
🔵 *FLARE (SURVIVOR)*

You are a survivor. Bring back the fallen.

*Ability:* One-time: revive one dead player.

*Limitations:*
- You die in the process
- Revived player returns with no abilities

Your sacrifice can change the game.
Make it count.
""",
    'Sheriff': """
🔵 *SHERIFF (SURVIVOR)*

You are a survivor. Execute the corrupted.

*Ability:* Kill one player nightly.

*Limitations:*
- If target is NOT Corrupt, YOU die instead
- No kill limit

Your justice is deadly. Make sure your target is guilty.
""",
    'Static': """
⚪ *STATIC (VANILLA)*

You are a survivor with no special ability.

*Passive:* First vote against you is public. Everyone sees who started the bandwagon.

Use this to create pressure and find the corrupted.
""",
    'Relay': """
⚪ *RELAY (VANILLA)*

You are a survivor with no special ability.

*Passive:* If 3+ people vote the same target, that target learns who voted for them.

Your presence creates voting information.
""",
    'Ping': """
⚪ *PING (VANILLA)*

You are a survivor with no special ability.

*Passive:* First time you're targeted by any ability, you get a notification: "YOU WERE TARGETED."

You won't know who targeted you, just that it happened.
"""
}

DAWN_MESSAGES = {
    'kill': "💀 *Dawn breaks.* @{username} has been found dead.",
    'no_kill': "🌅 *Dawn breaks.* No casualties last night. The grid held.",
    'shield_save': "🛡️ *Dawn breaks.* @{username} survived an attack. Volt's protection held.",
    'sheriff_kill_corrupt': "⚖️ *Dawn breaks.* @{username} was executed. They were Corrupt.",
    'sheriff_kill_innocent': "💀 *Dawn breaks.* @{username} was executed. Sheriff made a mistake.",
    'exile': "🗳️ @{username} has been exiled. Role: {role}",
    'skip_vote': "🗳️ No exile. The vote was skipped.",
    'tie_vote': "🗳️ No exile. The vote was tied."
}

NIGHT_MESSAGES = {
    'night_start': "🌙 *Night falls.* Abilities activate...",
    'night_end': "☀️ *Night ends.* Preparing dawn report...",
    'choose_target': "Choose your target:",
    'ability_prompt': "Use your ability:",
    'scan_result': "Scan result: {target} is {result}",
    'protect_success': "You protected {target}.",
    'protect_fail': "You failed to protect {target}.",
    'block_success': "You blocked {target}.",
    'role_reveal': "{target} is {role}.",
    'sheriff_result': "Your target {target} was {result}.",
    'virus_targets': "Your targets: {targets}",
    'wraith_win': "You are the last one alive. You win!",
    'glitch_steal': "Choose a dead player to steal their ability:",
    'plague_infect': "Choose a player to infect:"
}

WIN_MESSAGES = {
    'corrupt': "🔴 *CORRUPT WINS.* The grid has fallen.",
    'survivor': "🔵 *SURVIVORS WIN.* The corrupted have been purged.",
    'neutral_wraith': "🟡 *NEUTRAL WINS.* {username} stands alone.",
    'neutral_virus': "🟡 *NEUTRAL WINS.* {username} completed their mission."
}

GAME_REPLAY_HEADER = """
📊 *GAME REPLAY*
Game ID: {game_id}
Winner: {winner}
Duration: {duration} rounds
"""

GAME_REPLAY_ENTRY = """
*Round {round}:*
{events}
"""

LOBBY_MESSAGES = {
    'join': "✅ {username} joined the lobby. ({count}/10)",
    'leave': "❌ {username} left the lobby. ({count}/10)",
    'bot_added': "🤖 {username} added to the game.",
    'game_starting': "⚡ Game starting in {seconds} seconds...",
    'game_started': "⚡ *BLACKOUT INITIATED.* The grid has failed.",
    'not_enough_players': "❌ Need at least 4 players to start.",
    'game_in_progress': "❌ A game is already in progress.",
    'lobby_full': "❌ Lobby is full.",
    'corrupt_count_set': "⚙️ Corrupt count set to {count}."
}

HELP_MESSAGE = """
🎮 *BLACKOUT - How to Play*

*Objective:*
- Survivors: Eliminate all Corrupt + Neutrals
- Corrupt: Kill all Survivors
- Neutrals: Complete individual win conditions

*Commands:*
/join - Join the lobby
/leave - Leave the lobby
/add_bots - Fill to 10 with smart bots
/help - Show this message
/players - Show current players
/vote @username - Vote to exile
/skip - Skip vote
/spectate - View game as dead player
/stats - View your ELO and record
/leaderboard - View top players

*Day Phase:*
- 60 seconds to discuss
- 30 seconds to vote
- Majority vote = exile
- Tie or skip = no exile

*Scan Results:*
- CLEAN: Likely innocent
- SUSPICIOUS: Could be Corrupt, Neutral, or vanilla
- Only Blackout appears CLEAN among Corrupt

*Tips:*
- Volt and Grid appear SUSPICIOUS when using abilities
- Sheriff dies if they kill an innocent
- Phantom marks players for Corrupt team
- Dead players can spectate but not influence
"""

DEAD_SPECTATE_MESSAGE = """
💀 *You are eliminated.*

You can spectate the game but cannot influence it.
Watch the chaos unfold.
"""

VOTE_PUBLIC_MESSAGE = "🗳️ {username} voted for {target}"
VOTE_SKIP_PUBLIC_MESSAGE = "🗳️ {username} skipped the vote"

STATIC_PASSIVE_MESSAGE = "📢 *PUBLIC VOTE:* {username} started the bandwagon against {target}!"
RELAY_PASSIVE_MESSAGE = "📊 *VOTING BLOC DETECTED:* {target} can see who voted for them."
PING_PASSIVE_MESSAGE = "⚡ *YOU WERE TARGETED* by an unknown ability."

BOT_CHAT_TEMPLATES = {
    'Aggressive': {
        'accuse': "🤖 {bot} says: {target} is acting sus. Vote them out!",
        'defend': "🤖 {bot} says: I'm clean. Why would I betray my own team?",
        'agree': "🤖 {bot} says: {accuser} is right about {target}. Let's exile them.",
        'react': "🤖 {bot} says: '{message}'? That's exactly what a Corrupt would say, {target}.",
        'question': "🤖 {bot} says: {target}, you really believe '{message}'? Sus.",
        'quiet': "🤖 {bot} says: I'm watching. Someone's gotta make a move.",
        'accuse_dead': "🤖 {bot} says: {target} accused {player} and now {player}'s dead. Convenient.",
        'vote_bloc': "🤖 {bot} says: {player} and {buddy} keep voting together. Team?",
        'contradict': "🤖 {bot} says: {player} called {target} clean, now calls them sus. Liar.",
    },
    'Cautious': {
        'accuse': "🤖 {bot} says: Can someone scan {target}? Need more info.",
        'defend': "🤖 {bot} says: I haven't done anything suspicious. Check my votes.",
        'agree': "🤖 {bot} says: {accuser} makes a good point about {target}.",
        'react': "🤖 {bot} says: {target}, what do you mean by '{message}'? Explain.",
        'question': "🤖 {bot} says: {target}, can you clarify '{message}'?",
        'quiet': "🤖 {bot} says: Hmm... need to think about this.",
        'accuse_dead': "🤖 {bot} says: {target} accused {player} and now they're gone. Interesting timing.",
        'vote_bloc': "🤖 {bot} says: {player} and {buddy} always vote as a bloc. Collusion?",
        'contradict': "🤖 {bot} says: {player} keeps changing their story about {target}.",
    },
    'Quiet': {
        'accuse': "🤖 {bot} says: {target} maybe?",
        'defend': "🤖 {bot} says: I'm good.",
        'agree': "🤖 {bot} says: Yeah.",
        'react': "🤖 {bot} says: '{message}' ...ok.",
        'question': "🤖 {bot} says: {target} said '{message}'... thoughts?",
        'quiet': "🤖 {bot} says: ...",
        'accuse_dead': "🤖 {bot} says: {target} mentioned {player} before {player} died.",
        'vote_bloc': "🤖 {bot} says: {player} and {buddy} vote same.",
        'contradict': "🤖 {bot} says: {player} switched on {target}.",
    },
    'Strategic': {
        'accuse': "🤖 {bot} says: {target}'s voting pattern matches Corrupt behavior.",
        'defend': "🤖 {bot} says: My voting record is clean. I've been helping.",
        'agree': "🤖 {bot} says: {accuser} is onto something. {target} needs to explain.",
        'react': "🤖 {bot} says: '{message}' doesn't align with {target}'s previous statements.",
        'question': "🤖 {bot} says: {target}, your claim '{message}' needs evidence.",
        'quiet': "🤖 {bot} says: Analyzing the data...",
        'accuse_dead': "🤖 {bot} says: Statistical anomaly: {target} accused {player} pre-mortem.",
        'vote_bloc': "🤖 {bot} says: {player} and {buddy} share {pct}% vote alignment. Correlated.",
        'contradict': "🤖 {bot} says: {player}'s stance on {target} flipped. Deception indicator.",
    }
}

ELO_MESSAGES = {
    'win': "🏆 You won! ELO: {old_elo} → {new_elo} (+{change})",
    'lose': "💀 You lost. ELO: {old_elo} → {new_elo} ({change})",
    'neutral_win': "🏆 Neutral win! ELO: {old_elo} → {new_elo} (+{change})"
}

STATS_MESSAGE = """
📊 *Your Stats*

Username: {username}
ELO: {elo}
Games Played: {games_played}
Wins: {wins}
Win Rate: {win_rate}%
"""

LEADERBOARD_MESSAGE = """
🏆 *Leaderboard*

{entries}
"""

LEADERBOARD_ENTRY = "{position}. {username} - ELO: {elo} ({wins} wins)"
