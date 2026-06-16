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

*Ability:* Steal one dead player's role (one-time use). You take their ability and become them.

*Win Condition:* Survive to endgame + use stolen ability.

Watch who dies. Anyone can be stolen - corrupt, survivor, or neutral. Choose wisely.
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

HELP_MESSAGE = """🎮 *BLACKOUT - How to Play*

*Objective:*
• Survivors: Eliminate all Corrupt + Neutrals
• Corrupt: Kill all Survivors
• Neutrals: Complete individual win conditions

*Commands:*
• /join - Join the lobby
• /leave - Leave the lobby
• /add_bots - Fill to 10 with smart bots
• /help - Show this message
• /players - Show current players
• /skip - Skip vote
• /spectate - View game as dead player
• /stats - View your ELO and record
• /leaderboard - View top players

*Day Phase:*
• 60 seconds to discuss
• 30 seconds to vote
• Majority vote = exile
• Tie or skip = no exile

*Scan Results:*
• CLEAN: Likely innocent
• SUSPICIOUS: Could be Corrupt, Neutral, or vanilla
• Only Blackout appears CLEAN among Corrupt

*Tips:*
• Volt and Grid appear SUSPICIOUS when using abilities
• Sheriff dies if they kill an innocent
• Phantom marks players for Corrupt team
• Dead players can spectate but not influence
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

ABILITY_ANNOUNCEMENTS = {
    'Grid': {
        'scan_clean': [
            "🔍 {bot} says: I scanned {target} last night. They came back CLEAN.",
            "🔍 {bot} says: {target} is clean. My scan was clear.",
            "🤖 {bot} says: Heads up, I scanned {target} and got CLEAN. So they're good.",
            "🔍 {bot} says: {target} checked out clean. Moving on.",
        ],
        'scan_suspicious': [
            "🚨 {bot} says: I scanned {target} last night. They're SUSPICIOUS.",
            "🚨 {bot} says: {target} is SUS. My scan lit up red.",
            "🤖 {bot} says: {target} came back SUSPICIOUS. We need to talk about this.",
            "🚨 {bot} says: I have a scan on {target} — SUSPICIOUS. That's not good.",
        ],
    },
    'Volt': {
        'protected': [
            "🛡️ {bot} says: I protected someone last night. Can't say who.",
            "🛡️ {bot} says: My shield went up last night. Someone's alive because of me.",
            "🤖 {bot} says: I did my job last night. Someone's protected.",
        ],
    },
    'Bunker': {
        'blocked': [
            "🔒 {bot} says: I blocked someone last night. Their ability was stopped.",
            "🔒 {bot} says: Someone got bunkered last night. Couldn't use their ability.",
            "🤖 {bot} says: My block went through last night. Someone's ability is on cooldown.",
        ],
    },
    'Kernel': {
        'revealed': [
            "📋 {bot} says: I revealed someone's role last night. It's real.",
            "📋 {bot} says: I used my one-time ability. I know someone's exact role now.",
            "🤖 {bot} says: The truth is out. I revealed a role last night.",
        ],
    },
    'Sheriff': {
        'executed_corrupt': [
            "⚖️ {bot} says: I executed someone last night. They were Corrupt. Justice served.",
            "⚖️ {bot} says: My target was guilty. One less Corrupt to worry about.",
            "🤖 {bot} says: Sheriff here. My execution last night hit a Corrupt. Good riddance.",
        ],
    },
}

BOT_CHAT_TEMPLATES = {
    'Aggressive': {
        'accuse': [
            "🤖 {bot} says: {target} is acting sus. Vote them out!",
            "🤖 {bot} says: {target} is 100% corrupt. I can feel it.",
            "🤖 {bot} says: {target} has been dodging all game. Guilty.",
            "🤖 {bot} says: {target}'s votes make no sense for a survivor. Out them.",
            "🤖 {bot} says: {target} is playing too quiet. Corrupt confirmed.",
            "🤖 {bot} says: {target} deflects every accusation. Classic corrupt move.",
        ],
        'defend': [
            "🤖 {bot} says: I'm clean. Why would I betray my own team?",
            "🤖 {bot} says: I've been helping all game. Back off.",
            "🤖 {bot} says: My voting record speaks for itself. I'm good.",
            "🤖 {bot} says: Accuse me and you're wasting a vote. I'm survivor.",
            "🤖 {bot} says: I've been pushing for the right targets. I'm not corrupt.",
        ],
        'agree': [
            "🤖 {bot} says: {accuser} is right about {target}. Let's exile them.",
            "🤖 {bot} says: Finally! {target} needs to go. {accuser} nailed it.",
            "🤖 {bot} says: Agreed. {target} is suspicious as hell.",
            "🤖 {bot} says: {accuser} sees it too. {target} is done.",
        ],
        'react': [
            "🤖 {bot} says: '{message}'? That's exactly what a Corrupt would say, {target}.",
            "🤖 {bot} says: {target}, that excuse is trash. Try harder.",
            "🤖 {bot} says: '{message}'? That's literally corrupt talk.",
            "🤖 {bot} says: {target}, you just proved you're corrupt with that.",
        ],
        'question': [
            "🤖 {bot} says: {target}, you really believe '{message}'? Sus.",
            "🤖 {bot} says: {target}, explain yourself. That doesn't add up.",
            "🤖 {bot} says: {target}, your logic is broken. Corrupt confirmed.",
            "🤖 {bot} says: {target}, that makes zero sense for a survivor.",
        ],
        'quiet': [
            "🤖 {bot} says: I'm watching. Someone's gotta make a move.",
            "🤖 {bot} says: Patience. The corrupt will slip up.",
            "🤖 {bot} says: Everyone calm down. We need to vote smart.",
            "🤖 {bot} says: I'm reading the room. Something's off.",
        ],
        'accuse_dead': [
            "🤖 {bot} says: {target} accused {player} and now {player}'s dead. Convenient.",
            "🤖 {bot} says: {target} got {player} killed with that accusation. Corrupt move.",
            "🤖 {bot} says: {player} is dead after {target} targeted them. Suspicious.",
        ],
        'vote_bloc': [
            "🤖 {bot} says: {player} and {buddy} keep voting together. Team?",
            "🤖 {bot} says: {player} and {buddy} are always in sync. Colluding?",
            "🤖 {bot} says: {player} and {buddy} vote the same every time. Suspicious pair.",
        ],
        'contradict': [
            "🤖 {bot} says: {player} called {target} clean, now calls them sus. Liar.",
            "🤖 {bot} says: {player} flipped on {target}. Which is it? Corrupt confirmed.",
            "🤖 {bot} says: {player} contradicted themselves about {target}. Caught.",
        ],
        'deduction': [
            "🤖 {bot} says: {target} hasn't been scanned yet. Time to check them.",
            "🤖 {bot} says: The corrupt always protect their own. Look at voting patterns.",
            "🤖 {bot} says: {target}'s behavior changed after {player} died. Guilty conscience?",
            "🤖 {bot} says: Statistically, one of {target} or {accuser} is corrupt.",
        ],
        'vote_pressure': [
            "🤖 {bot} says: We NEED to exile someone tonight. {target} is the best lead.",
            "🤖 {bot} says: Skipping vote helps the corrupt. Vote {target}.",
            "🤖 {bot} says: If {target} is clean, we lose time. But if they're corrupt, we win.",
        ],
        'suspicion_level': [
            "🤖 {bot} says: {target} is on my high suspicion list. Watch them.",
            "🤖 {bot} says: My reads say {target} is corrupt. Trust me.",
            "🤖 {bot} says: {target} has too many red flags. Vote them out.",
        ],
    },
    'Cautious': {
        'accuse': [
            "🤖 {bot} says: Can someone scan {target}? Need more info.",
            "🤖 {bot} says: {target} is suspicious but I need confirmation before voting.",
            "🤖 {bot} says: {target}'s behavior is odd. We should investigate.",
            "🤖 {bot} says: I'm not 100% on {target} yet. Need a scan.",
            "🤖 {bot} says: {target} might be corrupt. Can we get a Grid scan?",
        ],
        'defend': [
            "🤖 {bot} says: I haven't done anything suspicious. Check my votes.",
            "🤖 {bot} says: My record is clean. I've been voting correctly.",
            "🤖 {bot} says: I'm not corrupt. My actions speak for themselves.",
            "🤖 {bot} says: I've been helping the team. Don't waste votes on me.",
        ],
        'agree': [
            "🤖 {bot} says: {accuser} makes a good point about {target}.",
            "🤖 {bot} says: I'm leaning towards {accuser}'s read on {target}.",
            "🤖 {bot} says: {accuser} has been right before. {target} is worth investigating.",
            "🤖 {bot} says: {target}'s story doesn't add up. {accuser} is onto something.",
        ],
        'react': [
            "🤖 {bot} says: {target}, what do you mean by '{message}'? Explain.",
            "🤖 {bot} says: '{message}' is an odd thing to say. {target}, clarify.",
            "🤖 {bot} says: {target}, that statement is suspicious. Can you explain?",
            "🤖 {bot} says: '{message}' doesn't track with what we know, {target}.",
        ],
        'question': [
            "🤖 {bot} says: {target}, can you clarify '{message}'?",
            "🤖 {bot} says: {target}, where's the evidence for that claim?",
            "🤖 {bot} says: {target}, that doesn't match the facts. Explain.",
            "🤖 {bot} says: {target}, your logic is flawed. Walk us through it.",
        ],
        'quiet': [
            "🤖 {bot} says: Hmm... need to think about this.",
            "🤖 {bot} says: Waiting for more information before I commit.",
            "🤖 {bot} says: This is tricky. Need to analyze the data.",
            "🤖 {bot} says: I'm processing. Don't rush me.",
        ],
        'accuse_dead': [
            "🤖 {bot} says: {target} accused {player} and now they're gone. Interesting timing.",
            "🤖 {bot} says: {player} died after {target} called them out. Coincidence?",
            "🤖 {bot} says: {target} targeted {player} before {player} died. Could be corrupt.",
        ],
        'vote_bloc': [
            "🤖 {bot} says: {player} and {buddy} always vote as a bloc. Collusion?",
            "🤖 {bot} says: {player} and {buddy} vote together suspiciously often.",
            "🤖 {bot} says: {player} and {buddy} are aligned. Could be corrupt partners.",
        ],
        'contradict': [
            "🤖 {bot} says: {player} keeps changing their story about {target}.",
            "🤖 {bot} says: {player} contradicted themselves. That's a red flag.",
            "🤖 {bot} says: {player} flipped on {target}. Which story is real?",
        ],
        'deduction': [
            "🤖 {bot} says: {target} hasn't been scanned yet. Someone should check them.",
            "🤖 {bot} says: The corrupt usually vote together. Look at the bloc patterns.",
            "🤖 {bot} says: {target}'s defense was weak. That's concerning.",
            "🤖 {bot} says: We need to cross-reference votes with scan results.",
        ],
        'vote_pressure': [
            "🤖 {bot} says: We should vote {target} based on current evidence.",
            "🤖 {bot} says: Not voting helps the corrupt. {target} is our best option.",
            "🤖 {bot} says: {target} has the most evidence against them. Let's vote.",
        ],
        'suspicion_level': [
            "🤖 {bot} says: {target} is suspicious but I need more data.",
            "🤖 {bot} says: My read on {target} is uncertain. Need a scan.",
            "🤖 {bot} says: {target} could be corrupt. We should investigate.",
        ],
    },
    'Quiet': {
        'accuse': [
            "🤖 {bot} says: {target} maybe?",
            "🤖 {bot} says: {target}... I'm watching.",
            "🤖 {bot} says: Something about {target} feels off.",
            "🤖 {bot} says: {target} is on my radar.",
        ],
        'defend': [
            "🤖 {bot} says: I'm good.",
            "🤖 {bot} says: Not me.",
            "🤖 {bot} says: I'm clean.",
            "🤖 {bot} says: Check someone else.",
        ],
        'agree': [
            "🤖 {bot} says: Yeah.",
            "🤖 {bot} says: Mm-hmm.",
            "🤖 {bot} says: Agreed.",
            "🤖 {bot} says: Makes sense.",
        ],
        'react': [
            "🤖 {bot} says: '{message}' ...ok.",
            "🤖 {bot} says: Hmm.",
            "🤖 {bot} says: Sure, {target}.",
            "🤖 {bot} says: Right.",
        ],
        'question': [
            "🤖 {bot} says: {target} said '{message}'... thoughts?",
            "🤖 {bot} says: {target}... why?",
            "🤖 {bot} says: {target}, really?",
            "🤖 {bot} says: {target}, that's odd.",
        ],
        'quiet': [
            "🤖 {bot} says: ...",
            "🤖 {bot} says: *watches silently*",
            "🤖 {bot} says: Observing.",
            "🤖 {bot} says: *thinking*",
        ],
        'accuse_dead': [
            "🤖 {bot} says: {target} mentioned {player} before {player} died.",
            "🤖 {bot} says: {player} is dead. {target} talked to them.",
            "🤖 {bot} says: {target} and {player}... interesting.",
        ],
        'vote_bloc': [
            "🤖 {bot} says: {player} and {buddy} vote same.",
            "🤖 {bot} says: {player}... {buddy}... same votes.",
            "🤖 {bot} says: {player} and {buddy} are paired.",
        ],
        'contradict': [
            "🤖 {bot} says: {player} switched on {target}.",
            "🤖 {bot} says: {player} changed their mind.",
            "🤖 {bot} says: {player} contradicted.",
        ],
        'deduction': [
            "🤖 {bot} says: {target} hasn't been scanned.",
            "🤖 {bot} says: Patterns. {target} is off.",
            "🤖 {bot} says: The votes tell a story.",
        ],
        'vote_pressure': [
            "🤖 {bot} says: {target}. Vote.",
            "🤖 {bot} says: Vote {target} or we lose ground.",
            "🤖 {bot} says: {target} is the play.",
        ],
        'suspicion_level': [
            "🤖 {bot} says: {target}. Sus.",
            "🤖 {bot} says: {target} is sus.",
            "🤖 {bot} says: {target}... don't trust.",
        ],
    },
    'Strategic': {
        'accuse': [
            "🤖 {bot} says: {target}'s voting pattern matches Corrupt behavior.",
            "🤖 {bot} says: {target} has avoided being scanned all game. Suspicious.",
            "🤖 {bot} says: {target}'s defense timing is statistically anomalous.",
            "🤖 {bot} says: {target} aligns with Corrupt meta-strategy. High probability.",
            "🤖 {bot} says: {target}'s speech patterns indicate deception.",
        ],
        'defend': [
            "🤖 {bot} says: My voting record is clean. I've been helping.",
            "🤖 {bot} says: I've consistently voted against Corrupt. My data proves it.",
            "🤖 {bot} says: My actions demonstrate survivor alignment. Check my history.",
            "🤖 {bot} says: I've been transparent all game. No reason to suspect me.",
        ],
        'agree': [
            "🤖 {bot} says: {accuser} is onto something. {target} needs to explain.",
            "🤖 {bot} says: {accuser}'s analysis is sound. {target} is statistically likely corrupt.",
            "🤖 {bot} says: The evidence supports {accuser}'s claim about {target}.",
            "🤖 {bot} says: {accuser} has a track record of correct reads. {target} is suspicious.",
        ],
        'react': [
            "🤖 {bot} says: '{message}' doesn't align with {target}'s previous statements.",
            "🤖 {bot} says: {target}, that claim contradicts your round 1 behavior.",
            "🤖 {bot} says: '{message}' is statistically inconsistent with survivor play.",
            "🤖 {bot} says: {target}, your statement has a 73% deception indicator.",
        ],
        'question': [
            "🤖 {bot} says: {target}, your claim '{message}' needs evidence.",
            "🤖 {bot} says: {target}, that logic is flawed. Re-examine.",
            "🤖 {bot} says: {target}, the data doesn't support your claim.",
            "🤖 {bot} says: {target}, your reasoning has gaps. Fill them.",
        ],
        'quiet': [
            "🤖 {bot} says: Analyzing the data...",
            "🤖 {bot} says: Cross-referencing voting patterns.",
            "🤖 {bot} says: Running probability analysis...",
            "🤖 {bot} says: Processing game state...",
        ],
        'accuse_dead': [
            "🤖 {bot} says: Statistical anomaly: {target} accused {player} pre-mortem.",
            "🤖 {bot} says: {target}'s accusation of {player} preceded their death. Correlation: high.",
            "🤖 {bot} says: {player} died after {target}'s accusation. Probability of coincidence: low.",
        ],
        'vote_bloc': [
            "🤖 {bot} says: {player} and {buddy} share {pct}% vote alignment. Correlated.",
            "🤖 {bot} says: {player} and {buddy} vote sync rate is anomalous. Possible collusion.",
            "🤖 {bot} says: {player} and {buddy} have identical voting patterns. Statistically suspicious.",
        ],
        'contradict': [
            "🤖 {bot} says: {player}'s stance on {target} flipped. Deception indicator.",
            "🤖 {bot} says: {player} contradicted themselves about {target}. High deception signal.",
            "🤖 {bot} says: {player} changed position on {target} without new evidence. Suspicious.",
        ],
        'deduction': [
            "🤖 {bot} says: {target} hasn't been scanned. Probability of Corrupt: {pct}%",
            "🤖 {bot} says: Cross-referencing: {target}'s votes align with known Corrupt patterns.",
            "🤖 {bot} says: {target}'s behavior matches Corrupt meta. Recommend scan.",
            "🤖 {bot} says: Data analysis suggests {target} is Corrupt with {pct}% confidence.",
        ],
        'vote_pressure': [
            "🤖 {bot} says: Statistical analysis favors exiling {target}. Vote accordingly.",
            "🤖 {bot} says: Not voting has a -{pct}% win probability. Vote {target}.",
            "🤖 {bot} says: {target} is the highest-probability Corrupt. Exile them.",
        ],
        'suspicion_level': [
            "🤖 {bot} says: {target} is on my high suspicion list. Confidence: {pct}%.",
            "🤖 {bot} says: My algorithm flags {target} as Corrupt. Probability: {pct}%.",
            "🤖 {bot} says: {target}'s suspicion index is {score}/10. Recommend investigation.",
        ],
    },
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
