🧠 THE COMPLETE POKER BOT KNOWLEDGE STACK



I’ll organize this exactly how real systems are built.



🧱 LAYER 1 — GAME MECHANICS (Physics of Poker)



This is the “laws of the universe” for the bot.



Without this, nothing else works.



1️⃣ Cards \& Hand Strength



Rank system



Hand categories (pair, two pair, etc.)



Kickers



Showdown strength



Relative hand strength vs board



Bot uses this for:



showdown evaluation



hand comparison



draw detection



nutted hand detection



2️⃣ Streets



Preflop



Flop



Turn



River



Each street changes:



available info



bet sizes



bluff frequency



equity realization



Bot uses this for:



strategy switching



decision trees



bet sizing rules



3️⃣ Positions



Button



Cutoff



Middle



UTG



Blinds



Why crucial



Position affects:



playable hands



bluff frequency



value betting range



pot control



This is one of the strongest EV factors in poker.



4️⃣ Stack Size \& Depth



Measured in BB.



Important thresholds:



100BB → deep play



40BB → normal



20BB → pressure zone



10BB → push/fold



<6BB → jam almost everything playable



Bot uses this for:



risk tolerance



shove ranges



bluff frequency



postflop complexity



5️⃣ Pot Odds

call / (pot + call)



Bot uses this for:



calling decisions



draw profitability



river bluff catching



6️⃣ Equity



Chance of winning at showdown.



Types:



raw equity



realized equity



range vs range equity



future street equity



Monte Carlo only gives raw equity.



Strong bots reason about realized equity.



7️⃣ Fold Equity



Probability opponent folds.



This is the engine of aggression.



Bluffs are profitable because of fold equity.



Bot must estimate:



EV = fold% \* pot + call% \* equity \* pot



🧱 LAYER 2 — PRE-FLOP STRATEGY (Biggest EV source)



Most profit in poker comes from preflop decisions.



This is where beginner bots fail.



1️⃣ Opening Ranges



Hands you play first-in.



Depend on:



position



stack depth



tournament phase



table aggression



2️⃣ Calling Ranges



Hands you call raises with.



Depend on:



raiser position



stack depth



pot odds



reverse implied odds



3️⃣ 3-Bet Ranges



Hands you re-raise with.



Two types:



value 3bets



bluff 3bets



Bot must balance both.



4️⃣ Push/Fold Ranges



Short stack strategy.



Very mathematical.

Used in tournaments constantly.



5️⃣ Blind Defense



Special logic for SB/BB.



Why special?

Because:



already invested chips



closing action



different pot odds



🧱 LAYER 3 — POST-FLOP STRATEGY



This is where most human intuition exists.



Bots must model board + ranges.



1️⃣ Hand Categories



Instead of “I have QJ” we think:



nuts



strong made hand



medium strength



weak made hand



draw



air



Bots reason in categories.



2️⃣ Board Texture



Critical concept.



Boards can be:



dry (A72 rainbow)



wet (JT9 two-tone)



paired



monotone



connected



high-card heavy



Texture determines:



bluff frequency



cbet frequency



value range strength



3️⃣ Draw Detection



Bot must detect:



flush draws



straight draws



backdoor draws



combo draws



These drive semi-bluff logic.



4️⃣ Continuation Betting (C-Bet)



If you raised preflop, you often bet flop.



But frequency depends on:



board texture



range advantage



opponent type



5️⃣ Pot Control



Sometimes strong hand should not bet.



Bot must know when to:



check medium strength



slow play nuts



avoid bloating pot



🧱 LAYER 4 — OPPONENT MODELING



This is where bots become competitive.



1️⃣ Player Type Detection



Basic types:



Nit (very tight)



TAG (tight aggressive)



LAG (loose aggressive)



Calling station



Maniac



Each requires different strategy.



2️⃣ Stats Tracking



Bots track:



VPIP (hands played)



PFR (raises preflop)



aggression factor



fold-to-cbet



showdown frequency



These stats drive exploitative play.



3️⃣ Range Narrowing



Each action reduces opponent range.



Example:



UTG raise → strong range

Flop call → removes junk

Turn raise → strong hands only





Good bots update opponent range continuously.



🧱 LAYER 5 — EV \& DECISION THEORY



This is math layer.



1️⃣ Expected Value



Every action should maximize EV.



Bots compute:



EV of fold



EV of call



EV of raise



2️⃣ Risk Adjusted EV



Tournament bots must consider:



stack survival



variance control



edge preservation



3️⃣ Bet Sizing Logic



Bots choose bet size based on:



board texture



range advantage



stack depth



bluff/value ratio



🧱 LAYER 6 — SOLVER-LIKE THINKING



Top-level poker AI concepts.



1️⃣ Mixed Strategies



Strong bots don’t always:



bet



fold



raise



They randomize:



bet 70%

check 30%





This prevents exploitation.



2️⃣ Range vs Range Logic



Not:



My hand vs opponent hand





But:



My range vs opponent range on this board





This is solver-style thinking.



3️⃣ Exploitative Adjustments



If opponent:



folds too much → bluff more



calls too much → value bet more



bluffs too much → call lighter



🏁 THIS IS THE COMPLETE MAP



Everything we build will come from this list.



We won’t add random features.



We’ll add them in dependency order.



🎯 Next Step (Your Choice)



We now pick the FIRST BUILDING BLOCK.



Three valid starts:



A️⃣ Hand Representation + Notation System



(required for ranges, board logic, draw detection)



B️⃣ Preflop Range System



(start building real strategy immediately)



C️⃣ Board + Hand Category Detector



(start postflop brain early)



Tell me:



A, B, or C



1. # We build it carefully, one file at a time.
