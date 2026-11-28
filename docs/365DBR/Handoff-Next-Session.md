# START HERE — 2026-11-26

Read this section only. The paragraphs below it are history. Their counts are stale. Do not rebuild `db/review/speaker-names.tsv`. The name generator is not on disk. `temp/task.py` is a read-only scanner and does not write the review file. Rebuilding the file would erase `reply`, `heading`, `named`, and `not-quotation`.

The review file is not loaded. Do not load it. Do not start the vault or 365DBR. Demo speaker rows in the vault stay as they are and are not this corpus.

## Counts

4,118 explicit. 7,326 carried. 11 reply. 11 heading. 37 named. 3 not-quotation. 0 unresolved. 11,506 rows. Rowley checked the hard verses on 2026-11-26. Those corrections are in the file. Do not put them back.

## What each basis means

- `explicit`: the name is written as the subject of this speech word.
- `carried`: the program kept an earlier name. This is the open set. Many of these names are the wrong person. Not vault-ready.
- `reply`: the next "said" or "answered" after a named speaker, one named person spoken to, and a Hebrew question word. The name stops on that word. The English question mark is not the test.
- `heading`: a psalm opens "of David," and this word is his "I," or Psalm 16:2. His name is not the subject written on the verb. The name stops on that word.
- `named`: this word has no subject noun. The person is named in this verse or the clause just before. The name stops on that word.
- `not-quotation`: the word does not introduce a quotation. The speaker cell is empty on purpose.
- `inferred-from-text` stays unused. Do not add a general inferred flag. `named` and `heading` are the only approved narrow classes.

## Locked rules

The Word is true in every book. Poetry is not fiction. Chapters and verses are an index, not the boundary of a speech. A name that was given is not the speaker. A noun inside "I said" or "you said" is not the speaker. Hebrew and Greek dictionary numbers are not mixed. `called` and `commanded` stay. יהוה is YHWH. אֱלֹהִים is God. Ἰησοῦς is Jesus. The file spells Cain as Kain. Greek Strong numbers are not used to identify a Greek word. Do not ask Rowley to read Hebrew or Greek. His check is the English name. If a name is the wrong person, he sends the verse id. Do not call the Word a story. Do not store a reading that the written words do not support in order to agree with anyone.

Psalm 16:2 is settled. The pointed word in the vault is אָמַרְתְּ, "you (feminine) said." The word soul is not in Psalm 16:1 or 16:2. "O my soul" is the King James supply. The old Greek reads "I said," and some Hebrew copies spell אמרתי. No other person is named. Speaker David, basis `heading`, not `explicit`.

## The 53 to verify in English

Explicit, the subject is written on the word:

- Exodus 1:19, the midwives.
- Judges 5:29, her princesses.
- 1 Samuel 4:20, the women standing by her.
- 1 Kings 1:2, his servants.
- 1 Kings 1:39, all the people.
- Esther 2:2, servants of the king.
- Esther 3:3, servants of the king.
- Nehemiah 2:19, Sanballat, Tobiah, and Geshem.
- Micah 3:5, the prophets. Peace is what they cried.
- Zephaniah 1:2, Zephaniah 1:3, Zephaniah 2:9, YHWH. The phrase is "a declaration of YHWH."
- Haggai 1:2, this people.
- Zechariah 1:4, "called," the former prophets. "Saying" is also the former prophets. "Thus said" is YHWH. "Declares" is YHWH. God is quoting the prophets, and their message is God.

Named, the person is in this verse or the clause just before:

- Exodus 2:19, the daughters, from Exodus 2:16.
- Exodus 2:20, the word "Call," Reuel. His speech to his daughters.
- Leviticus 1:1, "called," YHWH. YHWH is named on "spoke" in the same verse.
- Numbers 25:2, the daughters of Moab, from Numbers 25:1.
- Deuteronomy 1:14, both words, Israel. Deuteronomy 1:22, Israel. Moses is speaking to Israel, and the verb is "you said."
- Joshua 1:11, "command," Joshua. It is inside his charge from Joshua 1:10.
- Joshua 1:16, "they answered," the Reubenite, the Gadite, and the half of the tribe of Manasseh, from Joshua 1:12.
- Judges 1:1, "saying," the sons of Israel.
- Judges 1:15, Achsah, from Judges 1:13.
- Ruth 1:10, Orpah and Ruth.
- 1 Kings 1:25, the sons of the king, the heads of the host, and Abiathar.
- 1 Kings 1:28 and 1 Kings 1:32, "Call," David.
- 1 Kings 1:34, "you shall say," David. He is giving the charge. The people say it at 1 Kings 1:39.
- Nehemiah 1:3, Hanani and the men of Judah, from Nehemiah 1:2. "Those left" is what they said about Jerusalem.
- Nehemiah 2:18, the Jews, the priests, the nobles, the prefects, and the rest, from Nehemiah 2:16.
- Psalm 3:4, "He answers me," YHWH. David is the one who calls.
- Proverbs 1:21, both words, Wisdom, from Proverbs 1:20.
- Hosea 2:1, "Say," YHWH, from Hosea 1:2. Ammi is the name to be spoken.
- Zechariah 1:6, the fathers.
- Zechariah 1:11, both words, those YHWH sent, from Zechariah 1:10.
- Malachi 1:2 and Malachi 1:5, Israel, from Malachi 1:1.
- Malachi 1:6, Malachi 1:7, and Malachi 1:13, the priests.
- Acts 1:6, the apostles, from Acts 1:2.
- 2 Timothy 2:18, Hymenaeus and Philetus. "Among them" in 2:16 means they are some of the godless chatter, not the only two. The word "saying" is written of these two. The rest of that set is not named, so no further names are stored.
- 1 Samuel 2:3, Hannah. Her prayer begins at 1 Samuel 2:1. She tells the proud not to speak haughtily. They are addressed, not quoted.
- Proverbs 24:2, evil men, from Proverbs 24:1. Their lips speak. Lips are not stored.
- Micah 6:12, its inhabitants. They have spoken falsehood.
- Ephesians 2:11, "called Uncircumcision," the circumcision. That is the Jews in this verse. Uncircumcision is the label. The next word, "called Circumcision," is a label, not God.
- 1 Timothy 5:13, the younger widows, from 1 Timothy 5:11. The verse calls them idle, gossips, and busybodies.

Still no speaker stored:

- Ecclesiastes 7:21, "they speak." No person is named. The servant is the one you might hear, in the next clause. The Preacher is giving the instruction. God is not the subject of "they speak."
- Malachi 1:4, "they shall call them a border of wickedness." No person is named. Edom is already explicit on "Edom says." YHWH is already explicit on "thus said YHWH."
- Malachi 1:2 stays as it was checked: "says YHWH" is YHWH, and "you say" is Israel.

## Already done. Do not redo

Reply, the name stops on that word: Genesis 21:30 Abraham. Genesis 4:9 Kain. Genesis 37:13 Joseph. Exodus 8:10 word 1 Pharaoh, and word 3 stays Moses. Numbers 23:12 Balaam on "answered" and "said." The "spoke" in that verse stays YHWH. 1 Samuel 16:11 Jesse. 1 Kings 21:20 Elijah. 2 Kings 6:22 Elisha. 2 Chronicles 18:3 Jehoshaphat. Jonah 4:9 Jonah. Twenty other question-shaped hits were left because the same speaker continues, the word is inside the quotation, or the next speech is a later scene.

Heading, speaker David, not explicit: Psalm 16:2, 17:6, 27:7, 28:1, 32:5, 86:3, 86:7, 122:8, 138:3, 139:11, 141:1. "Answer me" in those verses was left.

Checked earlier and still standing: Genesis 1:28 God. Genesis 1:5 Night is not the speaker. Genesis 1:10 Seas is not the speaker. Genesis 4:25 Seth is not the speaker. Genesis 4:1 the woman. Genesis 23 Abraham. Numbers 17:1 YHWH. Jonah 3:4 Jonah. Matthew 5:2 Jesus. John 14:6 Jesus.

## Carried rows already known to be wrong

Do not rediscover these. They were left because they are `carried`, not part of the 53.

- Exodus 2:18 "he says" is stored as Moses. The man is Reuel.
- Exodus 2:20 word 1 "he says" is stored as Egyptian. The man is Reuel. Word 10 is already Reuel.
- Joshua 1:16 "saying" is still Joshua. Word 1 of that verse is already the Reubenite, the Gadite, and the half of the tribe of Manasseh.
- Psalm 3:4 "I call" is stored as way. That "I" is David. "He answers" on the next word is already YHWH.
- Hosea 1:9 "said" and "called" are stored as Israel. YHWH is speaking to Hosea.
- "Answer me" still carries the old name in Psalm 17:6, 27:7, 86:7, 138:3, and 141:1. The "you" there is YHWH being asked. Psalm 141:1 "when I call" is still the old carried name.
- Genesis 32:27 "dawn." Genesis 32:28 carries Jacob on the speech that renames him.
- 1 Samuel 20:4 carries Merab. 1 Kings 1:13 carries virgin. 2 Kings 18:36 carries Ivvah.

## Next session

Wait for Rowley's notes on the 53. Change only the verses he marks. Then the work is the 7,328 carried rows, by class, starting from the list above. A carried name that is the person spoken to, or a noun inside the quotation, is the class to find. Do not flip every unnamed "and he said." The person who asked often speaks again after the answer. Do not load the vault. Genre, validation queries, the API, Pass 4, and tiers 2–4 stay unbuilt. Before ending that session, replace this START HERE section. Do not leave the next session to rebuild this from the chat.

## History below this line. Counts in it are stale.

Speaker names, 2026-11-26, the 53 blanks. All 53 unresolved rows are now filled or marked. 14 are explicit, the subject written on the word (the midwives, her princesses, the women standing by her, his servants, all the people, servants of the king, Sanballat and Tobiah and Geshem, declaration of YHWH, this people, the former prophets, the prophets). 32 are basis named: the person is named in the verse or the clause just before, and the name stops on that word. 7 are not-quotation, with no speaker stored. Unresolved is now 0. Counts: 4,117 explicit, 7,328 carried, 11 reply, 11 heading, 32 named, 7 not-quotation. Carried names are not ready for the vault. The file is still not loaded. Neighbor carried rows were left, including Exodus 2:20 word 1 still Egyptian, Joshua 1:16 "saying" still Joshua, and Psalm 3:4 "I call" still way.

Speaker names, 2026-11-26, heading pass. Eleven speech words in psalms that open "of David" are basis heading, speaker David. The name is not marked explicit, and it stops on that word. Psalm 16:2, 17:6, 27:7, 28:1, 32:5, 86:3, 86:7, 122:8, 138:3, 139:11, 141:1. "Answer me" in those verses stays unchanged. Counts: 4,103 explicit, 7,328 carried, 11 reply, 11 heading, 53 unresolved. The 53 unresolved were read and not fixed. Carried names are not ready for the vault. The file is still not loaded.

Speaker names, 2026-11-26. `db/review/speaker-names.tsv` is a review file, not loaded. 4,103 explicit, 7,349 carried, 54 unresolved. Programming errors fixed in this pass: Hebrew and Greek dictionary numbers are no longer merged; a verb for "I" or "you" stops the search so a noun inside the quotation is not the speaker; the name after "his name" is not the speaker; two verse numbers that share one order are no longer woven together word by word. Checked: Genesis 1:28 God; Genesis 1:5 Night is not the speaker; Genesis 1:10 Seas is not the speaker; Genesis 4:25 Seth is not the speaker; Genesis 23 Abraham, not a dictionary mix-up; Numbers 17:1 YHWH; Matthew 5:2 Jesus; John 14:6 Jesus. Reply pass, same day: a named speaker, one named person spoken to, and a Hebrew question word located 31 next "said" or "answered" words. Eleven of those words are the other person's reply and are marked basis reply. The name stops at that word. Genesis 21:30 is Abraham. Also Cain (file spelling Kain) at Genesis 4:9, Joseph at Genesis 37:13, Pharaoh at Exodus 8:10 (the next word in that verse stays Moses), Balaam at Numbers 23:12, Jesse at 1 Samuel 16:11, Elijah at 1 Kings 21:20, Elisha at 2 Kings 6:22, Jehoshaphat at 2 Chronicles 18:3, Jonah at Jonah 4:9. The other twenty stay unchanged: the same speaker continues, the word "said" is inside the quotation, or the next speech is a later scene. Counts: 4,103 explicit, 7,338 carried, 11 reply, 54 unresolved. Carried names are not ready for the vault. The file is still not loaded.

Speaker quotation review, 2026-11-25. `db/review/speaker-quotation-markers.tsv` lists speech words from the Hebrew and Greek tokens. 11,506 rows, 8,394 verses, all 66 books. It is not loaded. It does not name the speaker. The 8 demo speaker rows were not used. Two tokens were held out: 2SA.19.13 תמרו tagged H559, and JER.3.19 לי tagged H7121.

Speaker rule and bleed gate, 2026-11-25. The old sentence stays: "The result still means the word is written, not that God said it." The reading and the reason are in `docs/SI/SI-Architecture-and-Tier1-Spec.md`, section "Locked contract," under "Speaker rule (2026-11-25)." Unknown means the speaker row is missing. `db/query/bleed.py` is read-only. `ask_tier1` calls it before a hit counts and again before the result returns. "Freedom of religion" and "freedom from Christianity" are refused. A hit counts only when that Hebrew or Greek word is written in the verse. The five cases in the next paragraph are unchanged. The API, Pass 4, tiers 2–4, and a genre load stay unbuilt.

Tier 1 loop, 2026-11-16. `db/query/tier1.py` `ask_tier1` is read-only. Pass the Hebrew or Greek word. It returns the places, the verses around the first place, and one result: speaks, contradicts, or silent. Silent stops. Contradicts is only the explicit claim "absent" when the word is written. LSV, KJV, and YLT are shown. LSB and WEB are not. No summary is added. Tiers 2–4 stay closed. Each shown verse prints speaker and genre from stored annotations only. No row prints unknown. A speaker is not copied outside its range. Theme is not used as genre. The result still means the word is written, not that God said it. Checked: Μάρκος speaks at ACT.12.12 with speaker unknown; an unwritten Greek word is silent; claim absent on Μάρκος contradicts; G3138 is refused; μακάριος speaks at MAT.5.3 with speaker Jesus on MAT.5.3 through MAT.5.6, and unknown on MAT.4.25, MAT.5.1, and MAT.5.2. No genre rows are stored, so genre is unknown. Print with `python db/scripts/tier1_ask.py`. This is not the S.I. API.

S.I. API, 2026-11-16. The API is not built. `serve_query_api.py` on `127.0.0.1:8765` is the local API, for querying the vault during the build. The real API will read a locked snapshot only, accept a question, and return the passages plus one result: Scripture speaks, Scripture contradicts this claim, or this search is silent. It does not write, and it does not open the vault. 365DBR keeps reading the static files directly. Full text: the locked contract, section "The API."

S.I. contract, 2026-11-16. Read `docs/SI/SI-Architecture-and-Tier1-Spec.md`, section "Locked contract," before any S.I. work. S.I. is the library. The Word of God is its language. 365DBR is the first application of that library, not the engine. Two logic layers run before the tiers answer and again before an answer leaves: Engler's 7 checks, and bleed. Bleed means a near neighbor is not the thing itself. It was unwritten until this date. Do not merge it into check 6. Do not build retrieval Pass 4 (weighted OR) as a grey match. The next engine session is one read-only loop: a question, the written word and the surrounding verses, the verses on screen, and one result — Scripture speaks, Scripture contradicts this claim, or this search is silent. On silence, stop. Do not start the vault or 365DBR over. Do not rename a locked term unless the old term, the new term, and the reason are written into that contract.

365DBR number rule, local only, 2026-11-16. `db/query/verify.py` stamps `number_match` on the local verse packs. An extended tag matches only the same written tag. `G2424G` matches `G2424G` and does not match `G2424`. A compound matches only that same compound. The owner checked Philemon 1:25, Philemon 1:24, Acts 21:6, and Song of Solomon 8:14 and saw nothing incorrect. `ws/strong/` and `ws/word/` were not rebuilt. Nothing was uploaded. Uploading that label is 365DBR work, and only when asked. It is not an S.I. session.

Word-file names, 2026-11-09. `ws/word/` files are UTF-8 hex (`cebaceb1ceb9.json` for και), because GoDaddy FTP turns Greek and Hebrew names into `?` and those URLs 404. `strongs_optional.js?v=20261109` builds that name. Upload `index.html`, `bible.html`, `strongs_optional.js`, and a fresh `ws/word/`. Delete the remote `word/` folder first. Do not re-upload the old Greek names.

Check-in and production, 2026-11-08. Local `ws/` was exported again the same day. Upload together: `index.html`, `bible.html`, `strongs_optional.js`, and the whole `ws/` folder, including the new `ws/word/`. A commit does not contain `ws/` (`manifest.json`, `verse/`, `strong/`, and `word/` are gitignored). Do not upload `RAW/`, Python, `db/`, or Docker. Day packs in `data/` were not changed.

Production is GoDaddy `/public_html/365DBR/`. The public site never has a database. The cache is written on this machine, then moved. Put `ws/` beside the HTML files (`https://mt-sin.ai/365DBR/ws/manifest.json`).

Word study, tested in a browser on 2026-11-08:
- The word, STEPBible English, lemma, lexicon gloss, and Strong's notes are one line. The place count is its own line and ends with a colon. A list with no places is not shown.
- Place lists follow the written word (Greek lemma letters, Hebrew lemma consonants), not a Strong's number. Philemon 1:25 Ἰησοῦ: 921 places, notes still `dStrong G2424G · sStrong G2424 · stored G2424G`. χάρις: 146 places. November 9, Philemon 1:24 Μάρκος: 8 places. Each hit shows the Greek or Hebrew that is written in that verse.
- Export: `python db/scripts/export_word_study_static.py`. 66 books, 31,100 verses, 444,791 tokens, 408,910 with `step_english`, 13,942 strong files, 45,297 word files.

Acts 21:6. Our Greek reads ἀσπασάμενοι ἀλλήλους ἐπέβημεν. ἀλλήλους is linked: one another, G0240. ἐπέβημεν is stored as G1910 / ἐπιβαίνω, the TR form "we embarked" on TAGNT Act.21.6#04. That token is not linked, so its panel has no STEPBible English.

ἀσπασάμενοι is confirmed. TAGNT Act-Rev, row Act.21.6#01, meaning-variant column, same letters: ἀσπασάμενοι, English "greeting", G0782, grammar V-ADP-NPM, editions TR+Byz. That is our token. The same row's main text is a different form: ἀπησπασάμεθα, English "we greeted", G0782=V-AMI-1P, editions NA28+NA27+Tyn+SBL+WH+Treg. Do not copy "we greeted" onto the participle, and do not link this token to that main row.

The dictionary column on that row says ἀποσπάω, "to draw away". That head is not this word. TBESG eStrong G0782 is ἀσπάζομαι, short gloss "to pay respects to", body "to welcome, greet, salute." The row's Alt Strongs cell is G2009. TBESG G2009 is ἐπιτιμία, "punishment", a different word. Do not store G2009. TBESG G20093 is ἀπασπάζομαι, "to take leave of", and it cites Act.21.6. That number is not the dStrong or sStrong printed on Act.21.6#01.

On 2026-11-08 the stored lemma, number, and morph on ἀσπασάμενοι were the neighbor's (ἀλλήλων / G0240). That copy was cleared, with 77 other unlinked Greek tokens of the same kind. On 2026-11-08 the variant note was then stored on this token only: G0782, lemma ἀσπάζομαι (TBESG original_word), morph V-ADP-NPM. It is still not linked, so the panel must not say "we greeted". After export it shows the lemma, the TBESG gloss "to pay respects to", and "Stored G0782 · no STEPBible row is linked". That last clause means the main row is not attached. The variant English "greeting" stays in the TAGNT variant column. Do not put G0240 back. Do not link Act.21.6#01. The owner runs `python db/scripts/export_word_study_static.py` so `ws/` matches this store.

Status as of 2026-11-05. The block above is newer. Below that, 2026-10-28 is older still.

Data already in the local database and in local `ws/`: a whole verse of letters links in order even when the verse numbers differ. One cross-number link, STEPBible PSA.18.50 onto the tokens at 2SA.22.51. A samekh or pe after the sof pasuq is a section mark and is ignored. 1 Chronicles 12:8–10 carry their STEPBible English. No original word was moved.

Status as of 2026-10-28. Do not re-research this. The block above is the newer status.

Verse text
- KJV (translation_id 2) and LSV (translation_id 1) are local eBible. All 31,102 verses each. SHA-256 on every row. No KJV or LSV source_note cites api.bible. The 30-day api.bible duty does not apply to these rows.
- KJV zip: apps/365DBR/RAW/KJV/eBible/eng-kjv2006_usfm.zip sha256 BF907642B9A37530EBD9CEDF08273F62A7C2140E414205FD4B8208BE952B4B14. License: public domain outside the UK. UK print or import needs the Queen's Printers (Cambridge, Oxford, Collins). source_bible_id ebible:eng-kjv2006.
- LSV zip: apps/365DBR/RAW/LSV/eBible/englsv_usfm.zip sha256 8EA9837F3FD6B4281CC9F0D0FF27DA51A44FDF8379FCA88733D7A7BCE4BC15AD. License: CC BY-SA 4.0, Covenant Press / Covenant Christian Coalition, 2020. source_bible_id ebible:englsv. Every LSV strong attribute was dropped. The numbers do not sit on the matching words. Dash-only lines 3JN.1.15 and REV.12.18 were not merged.
- LSB, WEB, and YLT were not rewritten. original_tokens was not rewritten.
- Loader: apps/365DBR/load_ebible_kjv_lsv.py. Provenance: apps/365DBR/RAW/KJV/eBible/PROVENANCE.txt and the LSV PROVENANCE.txt beside it.

Thirteen KJV compounds
- A space between two \w tags was removed only where this same file spells the compound as one word: cannot, wherein, whereunto, whatsoever.
- Verses: ACT.4.16, ACT.4.20, ACT.5.39, COL.3.17, COL.3.23, 1TI.2.7, 1TI.5.25, 1TI.6.12, 2TI.1.11, 2TI.2.9, 2TI.2.13, HEB.6.17, HEB.9.5.
- Hebrews 9:5 "can" is G2076. The other "cannot" rows are G1410 + G3756.
- Acts 5:39 reads "cannot" and still has two tag rows: can/G1410 and not/G3756.
- 2 Timothy 2:9 reads "Wherein" and "evil doer". "evil" is untagged. "doer" is G2557. Leave those as two words.

KJV English Strong's tags
- Migration 008_kjv_english_strong_tags is applied. schema_migrations has that version.
- Table kjv_english_strong_tags: 348,884 rows, edition eng-kjv2006.
- word_order counts \w and \+w spans, not every English word.
- These are KJV English-word tags from that file. They are not a WLC or TR alignment and they are not certified. They must not be copied onto original_tokens.
- 2 Thessalonians 3:18: grace G5485, our G2257, Lord G2962, Jesus G2424, Christ G5547, with G3326, you G5216, all G3956, Amen G0281. "be" is \add and has no row.
- apply_migrations.py failed: DATABASE_URL does not parse (host was read as eRSs@localhost). 008 was applied with docker exec psql. The loader connects through db/.env and works.

Not done
- Public day packs were not re-exported. https://mt-sin.ai/365DBR/ still serves the previous JSON.
- stage1_ingest_lsb_web_ylt.py, stage1_part2_execute.py, and stage3_export_and_ui.py were deleted on 2026-11-04 at the owner's request. Do not restore them. fetch_readings.py and fetch_omissions_cache.py are in apps/365DBR/reference/retired-api-bible/ and must not be run. They call api.bible and can overwrite day JSON.
- Do not run publish_365dbr.ps1 -Init unless asked, and only after the new HTML/JS are known to be on the server.

Recorded 2026-11-05. Current only where the 2026-11-08 block above does not replace it. Greek strong_number is still not certified. A finished display fix is not an open bug.
- Greek original_tokens.strong_number is not certified. The deleted stage1_part2_execute.py had filled gaps with a match window, a prefix test, most_common, and TR_EXACT_OVERRIDES. There is no strong_norm column. Proof: 2TH.3.18 ἡμῶν is stored as G3165; the lexicon entry for G3165 is μέ ("me"). The KJV English tag for "our" is G2257. The STEPBible English on that token is "of us". Those are different facts. TBESG prints eStrong G2424 and dStrong G2424G on Ἰησοῦς, gloss Jesus. G2424G is not its own eStrong, so an exact extended_strong lookup does not return that gloss. The place list is the word file (921 verses), already in the 2026-11-08 block. The old "absent from strongs_lexicon" sentence was misleading. A count of 977 stored G2424G tokens is stale: MRK.10.29 εἶπεν had that number copied from a neighbor and was cleared on 2026-11-08. v_interlinear_tokens uses left(strong_number, 5). 533 Greek rows are compounds such as G0846+G2532. Hebrew strong_number was not overwritten by that script. The suffix restore did not write any Strong's number.
- Do not start a fuzzy or majority Strong's rebuild. A number printed on that word in a named file is a source tag. A matcher, a vote, or a shifted overlay is a guess and must not be stored as Strong's.
- Stage 4 Path A is loaded (2026-11-04). Table stepbible_token_rows: 305,648 TAHOT + 141,746 TAGNT = 447,394 word rows. Migration 009. Loader apps/365DBR/load_stepbible_tokens.py. Audit apps/365DBR/audit_token_sources.py.
- Referees on disk: Hebrew is apps/365DBR/RAW/OSHB/wlc (WLC 4.20, the file TAHOT names as its base). Greek is apps/365DBR/RAW/GRCTR USX running text. Footnotes stay out of the verse body. Style d is a colophon. HEB_WLC is the same Leningrad text in another file, not a second manuscript. There is no Aleppo file here. Do not treat a different edition's disagreement as corruption.
- Link order, 2026-11-05. The old 1,182 figure was from before `--link-only`. After that pass, 1,012 linked rows sit earlier in the token verse than the previous linked row. 1,006 of those are one word on each side. 1 Corinthians 1:1 is the pattern: STEPBible has Χριστοῦ then Ἰησοῦ, and the token verse has Ἰησοῦ then Χριστοῦ. Each of those stays linked: the letters name that word. 309 links had more STEPBible copies than tokens, so the single-word pass had glued one copy onto the only token. 2 Corinthians 8:14 περίσσευμα is the first clause; the token verse only has the second. Song of Solomon 2:13 לך was one. Those 309 were unlinked. A single-word link is now refused when the letter counts differ. Full-verse matches stay, including PSA.18.50 onto 2SA.22.51 (10 rows). Linked rows are now 408,910. No token carries two STEPBible rows. No original word was moved.
- OSHB vs original_tokens on the same verse id: 16,923 of 23,012 verses are consonant-exact. 6,072 OSHB words are absent from that token verse. 5,162 of those are still in stepbible_token_rows, unlinked. Song of Solomon 8:14 is the pattern: OSHB and TAHOT both have לְ/ךָ, and original_tokens does not. The unlinked row was kept. 1 Chronicles 12 shows a verse-number offset (OSHB 12:10 is the token text of 12:9), so a raw "replaced word" count is not letter corruption. 1,833 TAHOT L rows differ from OSHB by a trailing section-mark samekh.
- GRCTR verse body vs Greek tokens: 7,474 of 7,856 verses exact. 2 Thessalonians 3:18 colophon is Πρὸς Θεσσαλονικεῖς δευτέρα ἐγράφη ἀπὸ Ἀθηνῶν, and the six unlinked TAGNT K rows are that colophon. TAGNT also preserves real edition variants (for example ἑλλησι / ἔθνεσιν) and movable nu. Keep both labeled.
- Suffix restore 2026-11-04 (`restore_oshb_suffixes.py`, reader `oshb_wlc.py`). 5,260 OSHB suffix pronouns inserted into 4,236 verses. New rows have strong_number NULL, lemma NULL, morph from the OSHB `<w>`, and extra.source `oshb-wlc-4.20`. Hebrew tokens 299,420 to 304,680. Greek stayed 140,111. Song 8:14 consonants match OSHB, including לְ/ךָ with no Strong's number. 1 Chronicles 12 was not changed. The 1,144 neighbor-verse offsets (1,004 at verse-1, 140 at verse+1) were not touched. Letter link after the insert: 352,337 linked, 9,321 no letter match, 57,970 ambiguous. Shared-token English agrees on 139 and disagrees on 169. Disagreeing tokens were left unlabeled.
- Local `ws/` export 2026-11-04 (`db/scripts/export_word_study_static.py`). 66 books, 444,791 tokens, 351,824 with `step_english`. The key is omitted unless every linked STEPBible row on that token has the same English. Label: STEPBible contextual English. highlightGloss was not written. "Not uploaded" described this 2026-11-04 pack only. The owner later uploaded a ws/ pack. Current upload state is the 2026-11-08 block at the top. `get_connection()` reads `db/.env` first because the container env password is rejected. Do not FTP unless asked.
- Text match 2026-11-04 (`load_stepbible_tokens.py --link-only`). Verse numbers are an index. A whole verse whose letters match in order is linked even when `heb_ref` is set and even when the token verse number differs. One such cross-number link: STEPBible PSA.18.50 (מגדיל, "making great") to tokens at 2SA.22.51. Tokens at PSA.18.50 read מגדל and stayed unlinked to that gloss. ס or פ after sof pasuq is a section mark and is ignored. 1CH.12.8–10 now carry their STEPBible English, including Ezer, the/ chief, Obadiah, the/ second, Eliab, the/ third. Single-word rows that still have `heb_ref` and do not sit in a full-verse match stay unlinked. No original_tokens row was moved. Greek colophon words at 2TH.3.18 stay unlinked. Do not treat a cross-number full-verse link as corruption. Local `ws/` was exported again on 2026-11-05 after the 309 unlinks: 408,910 tokens with `step_english`. That "Not uploaded" note is stale. See the 2026-11-08 block at the top.
- highlightGloss is gone and must stay gone. Gloss is not the English of a WLC/TR occurrence. Word Study hit text follows the Focal slot only. Compare text is slot 2 only.
- Aa is on for Hebrew and Greek in the UI. Greek numbers are still not certified.
- Test verses are never Genesis 1:1 or Matthew 1:1.
- finish_all.py and patch_export.py are deleted.
- Verse table has 31,305 rows. Protestant English is the 31,102 translation rows. REV.12.18 still exists with 0 translations and 0 tokens. LUK.17.37, ACT.15.41, and ACT.24.27 have English and zero Greek tokens.
- translations ids: 1 LSV, 2 KJV, 5 LSB, 6 WEB, 7 YLT. No ids 3 or 4.
- bible_common.py PARALLEL_IDS and db/etl/parse_passage.py still name the old api.bible ids. Do not rewrite applied migration 001.
- verify_schema.py is read-only (2026-11-05). It checks the eBible ids for KJV and LSV, reads SNG.8.14 and 2TH.3.18, and checks kjv_english_strong_tags for 2TH.3.18. It does not insert or delete. It passed. Greek original_tokens.strong_number stays uncertified.
- verify_bookmark_word_study.py expects Aa on Hebrew and Greek (2026-11-05). Bible samples are 2KI.1.1 and 2TH.3.18. Day 0913 samples are JOB.41.12 and 1CO.15.22. It passed on localhost. Matthew 1:1 is not used.
- 365dbr_dev is a superuser. Roles were not split.
- "Immutable" means a loaded file hash plus verse hash stays frozen. A correction is a new snapshot. KJV and LSV cells are allowed to change when the local file proves the change.
# 365DBR & S.I. (Scriptural Intelligence) — Master Agent & Grok Build Briefing
**Last Updated:** 2026-10-28 (Stages 1–3 Complete & Live in Production)

## 1. CRITICAL ARCHITECTURAL REALITY (READ FIRST)
- **GoDaddy Hosting is NOT a Blocker:** Do NOT assume we must migrate off GoDaddy to proceed with the database or Scriptural Intelligence (S.I.).
- **Local Master DB + Pre-Computed Static Export ($0 Runtime):**
  - Our authoritative Tier-1 S.I. relational database (`mt_sinai_365dbr` in local Docker PostgreSQL) is 100% operational on the developer workstation.
  - Production `365DBR` on GoDaddy runs entirely from deterministic, pre-computed static JSON packs (`apps/365DBR/data/<MMDD>/canonical_map.json` and `apps/365DBR/ws/{verse,strong}/*.json`) compiled directly from the local Postgres database and USX ASTs.
  - Meanwhile, the S.I. Tier-1 Database, Tier-2 API (`db/query/`), and Tier-3 Immutable Logic Engine are developed and verified locally against Docker Postgres with zero cloud hosting dependency.

## 2. NON-NEGOTIABLE SOLA SCRIPTURA & INTEGRITY RULES
1. **Textual Authority:** Original Hebrew WLC (`OSHB`) and Greek Textus Receptus (`TR` / `GRCTR`), alongside `LSB`, `LSV`, `KJV`, `WEB`, and `YLT`.
2. **Zero Guessing / Zero Heuristic Alignment:** Never use regex stem-matching (e.g., `highlightGloss`) or approximate word guessing to highlight or map English words to Hebrew/Greek tokens. Every mapping must be 100% deterministic, traceable to a primary source column/tag, and transparently labeled.
3. **Zero Artificial Verse Padding:** Exactly `31,102` canonical verses. Never insert placeholder text for versification differences.

## 3. COMPLETED STATE THROUGH STAGE 3 (LIVE IN PROD)
- **Stage 1 (Canonical Spine, 5 Translations, Original Tokens):**
  - `verses`: `31,102` canonical rows (`LUK.17.37`, `ACT.15.41`, `ACT.24.27` restored; bogus `REV.12.18` removed).
  - `verse_translations`: `155,510` rows (`LSB`, `LSV`, `KJV`, `WEB`, `YLT` x `31,102`) with enforced `text_sha256`.
  - `original_tokens`: `439,531` rows (`299,420` Hebrew WLC + `140,111` Greek TR) with 100% normalized Strong's (`strong_norm`).
  - `verse_alignments` (`31,102` rows) & `data_sources` (`7` authoritative provenance records).
- **Stage 2 (Strong's Lexicon & Production SQL Views):**
  - `strongs_lexicon`: `22,716` entries (`11,681` Hebrew `TBESH` + `11,035` Greek `TBESG`), 100% token join coverage.
  - Views: `v_interlinear_tokens` and `v_daily_reading_verses` tracked through migration `007_stage2_interlinear_and_reading_views.sql`.
- **Stage 3 (Static Export Pipeline & 3-Slot UI in `index.html` and `bible.html`):**
  - All 365 `apps/365DBR/data/<MMDD>/canonical_map.json` files contain `HEB` (original WLC/TR), `LSB`, `KJV`, `LSV`, `WEB`, and `YLT`.
  - Static Word Study packs (`apps/365DBR/ws/verse/*.json` for all 66 books and `apps/365DBR/ws/strong/*.json` for OT + NT Strong's numbers) are exported and deployed.
  - Both `index.html` and `bible.html` feature 3-slot parallel reading (Slot 1 Original Hebrew/Greek, Slot 2 Compare dropdown, Slot 3 Focal dropdown) working across both mobile (narrow) and desktop (wide) views, plus OT & NT Strong's Word Study.

## 4. CURRENT WORKFLOW 
- **DB-Backed Compilation:** Never overwrite `canonical_map.json` using the legacy 2-translation `compile_site.py` pipeline alone. The database exporter is `apps/365DBR/stage3_export_and_ui.py`. `finish_all.py` and `patch_export.py` were one-shot scripts and have been deleted. They reinserted `highlightGloss`.
-  KJV and LSV verse text are local eBible as of 2026-10-28. No row cites api.bible. WEB, YLT, LSB, and WLC were already local. Do not refresh those verses on a 30-day cycle.

## 5. NEXT UP: STAGE 4 & S.I. TRANSITION ROADMAP
1. **Deterministic Token-to-English Alignment (Stage 4 Path A):** Loaded 2026-11-04 into `stepbible_token_rows` from `apps/365DBR/RAW/STEPBible/Translators Amalgamated OT+NT/`. See the status block at the top of this file. Do not write those values onto `original_tokens`. KJV English `<w>` tags already sit in `kjv_english_strong_tags` and are not a WLC/TR alignment.
2. **Monthly `api.bible` DB Sync Script:** Automate checking `api.bible` monthly into `verse_translations` + regenerating static daypacks only when SHA-256 hashes change.
3. **S.I. Tier-2 & Tier-3 Logic Engine:** Build deterministic cross-reference, lexical concordances, and Sola Scriptura verification queries on top of `mt_sinai_365dbr`.
