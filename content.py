# Game data only: constants, narrative text, actions, events, enemies, and skills.

# Required knowledge to enter the final exam battle.
FINAL_EXAM_KNOWLEDGE_THRESHOLD = 55
BOSS_DAY = 5

# Threshold rules for final ending selection.
FINAL_ENDING_THRESHOLDS = {
    "high_distinction":   {"min_knowledge": 80, "max_stress": 60},
    "broke_but_brilliant": {"max_money": 5,      "min_knowledge": 75},
    # fallback: "barely_survived"
}

PERSONAS = {
    "balanced": {
        "label": "Balanced Survivor",
        "description": "A steady student with no extreme strengths or weaknesses.",
        "stats": {"energy": 80, "stress": 20, "money": 60, "knowledge": 10},
    },
    "grinder": {
        "label": "Deadline Grinder",
        "description": "Starts with strong knowledge, but stress is already close behind.",
        "stats": {"energy": 70, "stress": 32, "money": 55, "knowledge": 25},
    },
    "chill": {
        "label": "Chill Optimist",
        "description": "Great energy and low stress, but needs to catch up academically.",
        "stats": {"energy": 92, "stress": 10, "money": 55, "knowledge": 4},
    },
    "worker": {
        "label": "Part-time Hero",
        "description": "Starts with more money, but less energy after many shifts.",
        "stats": {"energy": 65, "stress": 24, "money": 95, "knowledge": 8},
    },
}

DAY_STORIES = {
    1: (
        "Monday morning arrives with a Moodle notification, a cold coffee, "
        "and the brave lie that there is still plenty of time. "
        "The semester is not over yet — technically."
    ),
    2: (
        "Tuesday moves faster than expected. "
        "The library is already half full, the group chat pings every few minutes, "
        "and every browser tab looks equally important."
    ),
    3: (
        "Wednesday is the danger zone: too late to relax, too early to panic properly, "
        "and somehow the perfect conditions for doing both at once."
    ),
    4: (
        "Thursday brings grey skies, creeping deadlines, and the strange feeling "
        "that the semester is folding in on itself faster than your notes."
    ),
    5: (
        "Friday arrives as the final checkpoint. "
        "Campus feels oddly quiet, your notes are covered in highlights, "
        "and the Final Exam Dragon is close enough to hear breathing."
    ),
}

DAY_TRANSITIONS = {
    2: (
        "The night passes quickly. Day 2 begins, "
        "and your to-do list has somehow learned to multiply overnight."
    ),
    3: (
        "Night passes. Day 3 opens with heavier eyes "
        "and a slightly sharper survival instinct."
    ),
    4: (
        "Night passes. Day 4 begins, "
        "and every small decision now feels like it carries strategic weight."
    ),
    5: (
        "Night passes. Day 5 breaks quietly. "
        "The weekend is close, but so is the deadline — and only one of them feels friendly."
    ),
}

# ---------------------------------------------------------------------------
# Persona-specific flavour lines appended after the main action message.
# Keys must match PERSONAS keys exactly.
# ---------------------------------------------------------------------------

PERSONA_ACTION_FLAVOUR = {
    "study_library": {
        "balanced": "You set a timer, find a reasonable seat, and stick to the plan.",
        "grinder":  "You have been here since 8 am. The librarian recognises your order.",
        "chill":    "You tell yourself one hour is enough. It probably is not.",
        "worker":   "You almost nodded off on the train here after the morning shift.",
    },
    "work_shift": {
        "balanced": "You clock in, do the job, and clock out without drama.",
        "grinder":  "Every minute behind the counter feels like a minute stolen from revision.",
        "chill":    "You chat with regulars and somehow enjoy the break from study guilt.",
        "worker":   "This is your third shift this week. Your feet already know the way.",
    },
    "cook_dinner": {
        "balanced": "You follow a simple recipe and feel briefly in control of your life.",
        "grinder":  "You eat standing at the counter — sitting down feels like wasted time.",
        "chill":    "You put on a playlist and turn dinner into the highlight of the day.",
        "worker":   "Cooking beats paying for food you do not have time to enjoy anyway.",
    },
    "buy_coffee": {
        "balanced": "One coffee, responsible choice, back to the desk within fifteen minutes.",
        "grinder":  "This is your third coffee today. You have stopped counting the cost.",
        "chill":    "You sit by the window for a few extra minutes. Nobody can stop you.",
        "worker":   "Staff discount makes this the one luxury you can actually afford right now.",
    },
    "visit_tutor": {
        "balanced": "You come prepared with two specific questions and leave with answers.",
        "grinder":  "You rehearsed this question three times before knocking on the door.",
        "chill":    "You were not sure what to ask, but the conversation sorted itself out.",
        "worker":   "Fitting this in between shifts took real effort. Worth it.",
    },
    "sleep_early": {
        "balanced": "Lights off at eleven. Responsible. Slightly boring. Completely correct.",
        "grinder":  "Closing the laptop early feels physically wrong, but your body wins.",
        "chill":    "You have been looking forward to this since two o'clock.",
        "worker":   "You are asleep before your head hits the pillow. No arguments from anyone.",
    },
}

# ---------------------------------------------------------------------------
# Daily actions
# ---------------------------------------------------------------------------

ACTIONS = {
    "study_library": {
        "label": "Study at Library",
        "scene": "library",
        "effects": {"energy": -15, "stress": 8, "knowledge": 18},
        "message": (
            "You squeeze into the last decent seat beside a tower of water bottles "
            "and colour-coded lecture notes. "
            "An hour passes before the material stops feeling like a foreign language. "
            "By the second hour something clicks — not everything, but enough to keep going."
        ),
        "event_pool": ["past_exam", "library_seat", "surprise_lecture", "quiz_python", "admin_email"],
    },
    "work_shift": {
        "label": "Work Part-time",
        "scene": "work",
        "effects": {"energy": -20, "stress": 6, "money": 45},
        "message": (
            "You clock in while your assignment sits open in another tab at home. "
            "The rush is relentless — orders, spills, a queue that never quite clears. "
            "When your shift ends, payday feels like a small shield against the week ahead, "
            "even if your energy does not survive the transaction."
        ),
        "event_pool": ["customer_complaint", "coles_discount", "opal_empty"],
    },
    "cook_dinner": {
        "label": "Cook at Home",
        "scene": "home",
        "effects": {"energy": 10, "stress": -5, "money": -8},
        "message": (
            "You cook dinner with whatever is left in the fridge — half an onion, "
            "some rice, a sauce that expired last Tuesday but probably fine. "
            "It is not fancy, but it is warm, and warm feels like control "
            "returning quietly to your life."
        ),
        "event_pool": ["groupmate_ping", "flatmate_party", "wifi_disconnect_event"],
    },
    "buy_coffee": {
        "label": "Buy Coffee",
        "scene": "cafe",
        "effects": {"energy": 18, "stress": 5, "money": -6},
        "message": (
            "You join the queue at the campus cafe and emerge four minutes later "
            "with something hot and overpriced. "
            "The first sip is a small, legitimate victory. "
            "The caffeine arrives like a polite favour that will call in its debt around midnight."
        ),
        "event_pool": ["cafe_run_into", "admin_email", "opal_empty", "coles_discount"],
    },
    "visit_tutor": {
        "label": "Visit Tutor",
        "scene": "tutor",
        "effects": {"energy": -8, "stress": -6, "knowledge": 12},
        "message": (
            "You walk into office hours and admit exactly which concept broke your brain. "
            "Three calm sentences from the tutor untangle what two lectures could not. "
            "You leave with a clearer head and the quiet relief of someone "
            "who finally asked instead of guessing."
        ),
        "event_pool": ["quiz_python", "quiz_visa", "past_exam", "surprise_lecture"],
    },
    "sleep_early": {
        "label": "Sleep Early",
        "scene": "sleep",
        "effects": {"energy": 25, "stress": -12, "knowledge": -3},
        "message": (
            "You close the laptop before midnight. "
            "It feels vaguely illegal during finals week, "
            "and some part of your brain files an objection. "
            "Your body overrules it immediately, "
            "and by morning the objection seems much less convincing."
        ),
        "event_pool": ["groupmate_ping", "admin_email", "flatmate_party"],
    },
}

# ---------------------------------------------------------------------------
# Random events
# Each event belongs to one or more day phases via the "phases" list.
# The engine uses this to filter events when building phase-aware pools,
# but individual actions can still reference any event by key regardless
# of phase — the action's event_pool always takes precedence.
# ---------------------------------------------------------------------------

EVENTS = {
    # --- Study / academic events ---
    "past_exam": {
        "title": "Past Exam Discovery",
        "message": (
            "You find a past exam paper tucked inside a borrowed textbook. "
            "One question looks suspiciously relevant to this semester."
        ),
        "animation": "event_exam",
        "phases": ["early", "middle", "late"],
        "choices": {
            "solve": {
                "label": "Work through it properly",
                "result": "The pattern clicks after a few rough attempts. Real progress.",
                "effects": {"knowledge": 14, "energy": -7},
            },
            "skim": {
                "label": "Skim the solution only",
                "result": "You gain confidence, but it might be borrowed confidence.",
                "effects": {"knowledge": 6, "stress": -2},
            },
        },
    },
    "library_seat": {
        "title": "Perfect Seat Opens Up",
        "message": (
            "A spot near a power outlet appears at the prime study table. "
            "A stressed-looking student is hovering nearby."
        ),
        "animation": "event_light",
        "phases": ["early", "middle"],
        "choices": {
            "take_seat": {
                "label": "Take it — you were here first",
                "result": "Two focused hours materialise out of nowhere.",
                "effects": {"knowledge": 12, "stress": -2},
            },
            "offer_seat": {
                "label": "Offer it to them",
                "result": "They look genuinely grateful. You feel surprisingly lighter.",
                "effects": {"stress": -10, "energy": -2},
            },
        },
    },
    "surprise_lecture": {
        "title": "Surprise Extra Lecture",
        "message": (
            "A Moodle notification: 'Additional revision session this Friday — "
            "strongly recommended.' You have a shift that afternoon."
        ),
        "animation": "event_warning",
        "phases": ["early", "middle"],
        "choices": {
            "attend": {
                "label": "Go — swap the shift",
                "result": "Your manager is not thrilled, but your notes are excellent.",
                "effects": {"knowledge": 14, "money": -20, "stress": 5},
            },
            "skip": {
                "label": "Keep the shift, get notes later",
                "result": "Your classmate sends three lines and a meme. Thanks.",
                "effects": {"money": 25, "knowledge": 3, "stress": 8},
            },
        },
    },
    "admin_email": {
        "title": "Ominous Admin Email",
        "message": (
            "A formal email arrives: subject line 'Important Update Regarding Your Enrolment'. "
            "The preview shows nothing useful."
        ),
        "animation": "event_warning",
        "phases": ["early", "middle", "late"],
        "choices": {
            "read_now": {
                "label": "Read it carefully now",
                "result": "It is a timetable correction. Alarming subject, anticlimactic content.",
                "effects": {"knowledge": 4, "stress": 3},
            },
            "ignore": {
                "label": "Deal with it tomorrow",
                "result": "The unknown version of that email is far scarier than the real one.",
                "effects": {"stress": 14},
            },
        },
    },
    # --- Work / commute events ---
    "coles_discount": {
        "title": "Coles Half-price Shelf",
        "message": (
            "You spot the discounted dinner shelf five minutes before closing. "
            "There are three portions of pasta left."
        ),
        "animation": "event_food",
        "phases": ["early", "middle", "late"],
        "choices": {
            "cook": {
                "label": "Grab it and cook properly",
                "result": "You cook enough for tomorrow too. Small win.",
                "effects": {"energy": 12, "money": -6, "stress": -4},
            },
            "skip": {
                "label": "Save the money",
                "result": "Financially sound. Your stomach immediately disagrees.",
                "effects": {"energy": -5, "stress": 4},
            },
        },
    },
    "opal_empty": {
        "title": "Opal Card: Insufficient Funds",
        "message": (
            "The gate flashes red. Your Opal balance ran out. "
            "The next train leaves in four minutes."
        ),
        "animation": "event_train",
        "phases": ["early", "middle", "late"],
        "choices": {
            "top_up": {
                "label": "Top up quickly at the machine",
                "result": "You make it with seconds to spare. Heart rate: elevated.",
                "effects": {"money": -10, "stress": 5},
            },
            "sneak": {
                "label": "Slip through behind someone",
                "result": "You make it, but spend the whole ride convinced an inspector is nearby.",
                "effects": {"stress": 18},
            },
        },
    },
    "customer_complaint": {
        "title": "Customer Complaint",
        "message": (
            "A customer slaps a receipt on the counter: 'I said less ice.' "
            "Eight people are waiting behind them."
        ),
        "animation": "event_message",
        "phases": ["early", "middle"],
        "choices": {
            "apologize": {
                "label": "Apologise and remake it",
                "result": "They leave without saying thank you. The queue moves on.",
                "effects": {"stress": 8, "energy": -5},
            },
            "argue": {
                "label": "Insist you heard correctly",
                "result": "They ask for the manager. The next hour is uncomfortable.",
                "effects": {"stress": 20},
            },
        },
    },
    # --- Social / home events ---
    "groupmate_ping": {
        "title": "Group Chat Emergency",
        "message": (
            "Your groupmate sends: 'sorry just saw this — what are we doing for the report?' "
            "The deadline is in 38 hours."
        ),
        "animation": "event_message",
        "phases": ["early", "middle", "late"],
        "choices": {
            "reply_calmly": {
                "label": "Reply calmly and divide tasks",
                "result": "You split the work evenly. It is going to be fine. Probably.",
                "effects": {"knowledge": 8, "stress": -3},
            },
            "panic_scroll": {
                "label": "Panic-scroll the chat history",
                "result": "The chat gets longer. Your confidence gets shorter.",
                "effects": {"stress": 12},
            },
        },
    },
    "flatmate_party": {
        "title": "Flatmate Party Night",
        "message": (
            "It is 11 pm. Music and laughter are coming through your door. "
            "You have a 9 am class tomorrow."
        ),
        "animation": "event_message",
        "phases": ["early", "middle", "late"],
        "choices": {
            "join": {
                "label": "Join for one hour",
                "result": "One hour becomes three. Future-you will have opinions about this.",
                "effects": {"stress": -15, "energy": -10, "knowledge": -3},
            },
            "earplugs": {
                "label": "Earplugs in, keep studying",
                "result": "You push through, but your focus is at roughly half capacity.",
                "effects": {"stress": 10, "knowledge": 5},
            },
        },
    },
    "cafe_run_into": {
        "title": "Run Into a Classmate",
        "message": (
            "You spot someone from your COMP9001 tutorial at the next table. "
            "They look equally exhausted."
        ),
        "animation": "event_food",
        "phases": ["early", "middle", "late"],
        "choices": {
            "study_together": {
                "label": "Study together for a bit",
                "result": "You compare notes and both fill in gaps you did not know you had.",
                "effects": {"knowledge": 10, "stress": -5, "energy": -4},
            },
            "just_wave": {
                "label": "Just wave and keep your headphones in",
                "result": "Socially efficient. You get another hour of quiet work done.",
                "effects": {"knowledge": 5, "energy": -2},
            },
        },
    },
    "wifi_disconnect_event": {
        "title": "Wi-Fi Drops Mid-Session",
        "message": (
            "The library Wi-Fi disconnects during a lecture recording. "
            "The progress bar sits at 47% indefinitely."
        ),
        "animation": "event_warning",
        "phases": ["early", "middle", "late"],
        "choices": {
            "mobile_data": {
                "label": "Switch to mobile hotspot",
                "result": "It works, barely, and costs you half your daily data.",
                "effects": {"money": -5, "stress": 5, "knowledge": 7},
            },
            "give_up": {
                "label": "Give up and read the textbook instead",
                "result": "The textbook is dense but it does not buffer.",
                "effects": {"knowledge": 8, "energy": -6},
            },
        },
    },
    # --- Quiz events ---
    "quiz_python": {
        "title": "Tutor Pop Question",
        "message": (
            "Your tutor points at the whiteboard mid-explanation: "
            "'Quick one — in Python, is a list mutable or immutable?'"
        ),
        "animation": "event_exam",
        "phases": ["early", "middle", "late"],
        "choices": {
            "mutable": {
                "label": "Mutable",
                "result": "Correct. The tutor nods and moves on. You breathe again.",
                "effects": {"knowledge": 10, "stress": -4},
            },
            "immutable": {
                "label": "Immutable",
                "result": "Wrong. The tutor sighs and reopens the week-two slides.",
                "effects": {"stress": 12},
            },
        },
    },
    "quiz_visa": {
        "title": "Student Services Check-in",
        "message": (
            "A Student Services officer stops you outside the library: "
            "'Just a quick one — what is the fortnightly work-hour limit on a student visa?'"
        ),
        "animation": "event_warning",
        "phases": ["middle", "late"],
        "choices": {
            "correct": {
                "label": "48 hours",
                "result": "Correct. They tick a box and walk away. You exhale slowly.",
                "effects": {"stress": -5, "knowledge": 6},
            },
            "wrong": {
                "label": "40 hours",
                "result": "They hand you a compliance reminder card. Your stress spikes.",
                "effects": {"stress": 15},
            },
        },
    },
}

# ---------------------------------------------------------------------------
# Enemies
# ---------------------------------------------------------------------------

ENEMIES = {
    "seat_hogger": {
        "name": "Seat Hogger",
        "hp": 42,
        "attack": 8,
        "moves": [
            {"name": "Bag Barricade", "description": "blocks three seats at once", "energy": -4, "stress": 8},
            {"name": "Passive-aggressive Sigh", "description": "makes your concentration crack", "energy": -3, "stress": 9},
        ],
        "reward": {"knowledge": 7, "stress": -2},
        "item_drop": ["focus_sticker", "noise_cancel_earbuds"],
    },
    "queue_hydra": {
        "name": "Queue Hydra",
        "hp": 44,
        "attack": 8,
        "moves": [
            {"name": "Double Line Spawn", "description": "new customers appear instantly", "energy": -5, "stress": 8},
            {"name": "Receipt Storm", "description": "everyone asks for a change", "energy": -4, "stress": 9},
        ],
        "reward": {"money": 8, "stress": -2},
        "item_drop": ["discount_voucher", "energy_drink"],
    },
    "fridge_mimic": {
        "name": "Fridge Mimic",
        "hp": 35,
        "attack": 7,
        "moves": [
            {"name": "Missing Ingredients", "description": "the one thing you need is gone", "energy": -4, "stress": 7},
            {"name": "Mystery Leftovers", "description": "confidence in dinner drops fast", "energy": -3, "stress": 8},
        ],
        "reward": {"energy": 4, "stress": -2},
        "item_drop": ["energy_drink", "discount_voucher"],
    },
    "caffeine_crash": {
        "name": "Caffeine Crash",
        "hp": 37,
        "attack": 7,
        "moves": [
            {"name": "Sugar Spike", "description": "energy jumps then drops", "energy": -6, "stress": 5},
            {"name": "Shaky Hands", "description": "typing speed goes weird", "energy": -4, "stress": 7},
        ],
        "reward": {"knowledge": 5},
        "item_drop": ["energy_drink", "cheat_sheet"],
    },
    "concept_wall": {
        "name": "Concept Wall",
        "hp": 41,
        "attack": 8,
        "moves": [
            {"name": "Abstract Trap", "description": "examples stop making sense", "energy": -4, "stress": 9},
            {"name": "Notation Maze", "description": "symbols start to blur", "energy": -4, "stress": 8},
        ],
        "reward": {"knowledge": 9},
        "item_drop": ["cheat_sheet", "focus_sticker"],
    },
    "night_anxiety": {
        "name": "Night Anxiety",
        "hp": 40,
        "attack": 8,
        "moves": [
            {"name": "What-if Spiral", "description": "every scenario ends badly", "energy": -4, "stress": 10},
            {"name": "Clock Watching", "description": "sleep feels impossible", "energy": -5, "stress": 8},
        ],
        "reward": {"stress": -6},
        "item_drop": ["noise_cancel_earbuds", "energy_drink"],
    },
    "final_exam": {
        "name": "Final Exam Dragon",
        "hp": 75,
        "attack": 12,
        "moves": [
            {
                "name": "Multiple-choice Fire",
                "description": "breathes four options that all look correct",
                "energy": -7,
                "stress": 12,
            },
            {
                "name": "Last Ten Marks",
                "description": "guards the hardest question with a smug silence",
                "energy": -6,
                "stress": 14,
            },
        ],
        "reward": {"knowledge": 15, "stress": -15},
    },
}

# ---------------------------------------------------------------------------
# Battle skills
# ---------------------------------------------------------------------------

SKILLS = {
    "review_notes": {
        "label": "Review Notes",
        "description": "Reliable strike. Deal 11 damage, spend 7 energy.",
        "damage": 11,
        "effects": {"energy": -7},
        "message": "You work through your notes methodically and land a clean hit.",
    },
    "cram_study": {
        "label": "Cram Study",
        "description": "High risk. Deal 19 damage, spend 14 energy, gain 9 stress.",
        "damage": 19,
        "effects": {"energy": -14, "stress": 9},
        "message": "You push hard. It lands, but the stress climbs with it.",
    },
    "drink_coffee": {
        "label": "Drink Coffee",
        "description": "Restore 18 energy. Costs $6 and adds 6 stress.",
        "damage": 0,
        "effects": {"energy": 18, "stress": 6, "money": -6},
        "message": "You drink coffee and borrow energy from a later version of yourself.",
    },
    "email_tutor": {
        "label": "Email Tutor",
        "description": "55% chance to deal 24 damage. Costs 5 energy.",
        "damage": 24,
        "effects": {"energy": -5},
        "hit_chance": 0.55,
        "message": "You send the email and wait.",
        "miss_message": "No reply yet. The silence has its own kind of lesson.",
    },
    "deep_breath": {
        "label": "Take Deep Breath",
        "description": "Reduce stress by 15. Gain 2 focus (+8 damage total on your next attack).",
        "damage": 0,
        "effects": {"stress": -15, "focus": 2},
        "message": "You slow down, breathe, and feel something settle.",
    },
}

# ---------------------------------------------------------------------------
# Endings  — full paragraphs, read by the engine via ENDING_MESSAGES[key]
# ---------------------------------------------------------------------------

ENDING_MESSAGES = {
    "high_distinction": (
        "Ending: High Distinction.\n\n"
        "The exam hall empties and you are one of the last to put down your pen — "
        "not because you struggled, but because you checked everything twice. "
        "Walking out into the afternoon sun, the weight of finals week lifts all at once. "
        "Your phone shows three messages from people asking how it went. "
        "You type back the same word to all of them: good. "
        "It is an understatement, but a satisfying one. "
        "The semester is over. You escaped — with style."
    ),
    "broke_but_brilliant": (
        "Ending: Broke but Brilliant.\n\n"
        "Your bank account has four dollars and some change. "
        "Your exam answers, however, are some of the clearest you have ever written. "
        "You sit outside the exam hall eating a Coles meal-deal you had been saving for this moment "
        "and feel something that is almost peace. "
        "The HECS debt is real, the rent is due, and next semester is already looming — "
        "but right now, in this specific patch of sunlight, none of that matters quite yet."
    ),
    "barely_survived": (
        "Ending: Barely Survived.\n\n"
        "You leave the exam hall with the particular walk of someone "
        "who has crossed a finish line by falling over it. "
        "Some questions went well. Others will not be discussed. "
        "Back in the dorm you sleep for eleven hours straight "
        "and wake up unsure what day it is, which is fine, "
        "because for the first time in a week it does not matter. "
        "You made it. Messily, imperfectly, but fully."
    ),
    "burnout": (
        "Ending: Burnout.\n\n"
        "Your energy hits zero on a Thursday afternoon in the library. "
        "You close the laptop, lean back in your chair, and simply cannot continue. "
        "Finals week wins this round. "
        "The notification from the university is polite but firm. "
        "You sit with it for a while, then text someone you trust. "
        "Next semester exists. You will be more careful with yourself."
    ),
    "panic": (
        "Ending: Panic Spiral.\n\n"
        "The stress reaches a point where studying stops being possible. "
        "Every page looks like noise. Every notification lands like an alarm. "
        "You step outside, sit on a bench, and breathe until your hands stop shaking. "
        "The week overwhelms you in the end, but you are still here — "
        "and still here is somewhere worth starting from."
    ),
    "deadline_missed": (
        "Ending: Not Ready.\n\n"
        "When the final exam arrives, the knowledge just is not there. "
        "You sit in the hall and do your best, "
        "but your best today is not enough to beat the dragon. "
        "Walking out early, you feel the gap between where you are "
        "and where you needed to be. "
        "It is not a comfortable feeling, but it is a clear one — "
        "and clarity, at least, is something to work with next time."
    ),
}

ACTION_ENEMY_MAP = {
    "study_library": "seat_hogger",
    "work_shift": "queue_hydra",
    "cook_dinner": "fridge_mimic",
    "buy_coffee": "caffeine_crash",
    "visit_tutor": "concept_wall",
    "sleep_early": "night_anxiety",
}

INTRO_STORY_PAGES = [
    "Finals week has begun. You are an international student in Australia, and every day is a balance between survival and progress.",
    "Each day you choose one action. Your choice changes your stats and triggers one campus challenge.",
    "When a challenge appears, you decide whether to fight or withdraw. Winning gives rewards. Quitting or losing costs you.",
    "Survive all days and defeat the Final Exam Dragon.",
]

MAX_INVENTORY_SIZE = 3
BATTLE_FAILURE_PENALTY = {"energy": -8, "stress": 10}

ITEMS = {
    "energy_drink": {
        "label": "Energy Drink",
        "description": "Recover 15 energy instantly.",
        "effects": {"energy": 15},
    },
    "cheat_sheet": {
        "label": "Cheat Sheet",
        "description": "Gain 2 focus for stronger next attack.",
        "effects": {"focus": 2},
    },
    "noise_cancel_earbuds": {
        "label": "Noise-cancel Earbuds",
        "description": "Reduce stress by 12.",
        "effects": {"stress": -12},
    },
    "discount_voucher": {
        "label": "Discount Voucher",
        "description": "Get $20 from part-time promo bonus.",
        "effects": {"money": 20},
    },
    "focus_sticker": {
        "label": "Focus Sticker",
        "description": "Gain 8 knowledge before next day.",
        "effects": {"knowledge": 8},
    },
}
