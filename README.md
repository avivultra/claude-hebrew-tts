# claude-hebrew-tts

A [Claude Code](https://claude.com/claude-code) plugin that lets Claude **read Hebrew (or any supported language) aloud** to you on demand, using Microsoft's free [edge-tts](https://github.com/rany2/edge-tts) neural voices. No API keys, no subscription.

When you ask Claude *"תקריא לי"* / *"read this aloud"*, the skill activates: Claude writes the text to a temp file and plays it through your OS default audio handler. That's it.

## Voices

| Voice name | Model ID | Gender | Language |
|---|---|---|---|
| `avri` *(default)* | `he-IL-AvriNeural` | Male | Hebrew |
| `hila` | `he-IL-HilaNeural` | Female | Hebrew |

edge-tts supports 400+ other voices too — see [the full list](https://github.com/rany2/edge-tts#list-of-supported-voices). You can extend the `VOICES` dict in `scripts/speak.py` to add them.

## Requirements

- **Claude Code** (any recent version supporting plugins and skills)
- **Python 3.10+** on `PATH`
- **Internet connection** (edge-tts calls Microsoft's public TTS endpoint)
- **Audio player** — Windows and macOS ship with one; Linux users install `mpg123` or `ffplay` or `cvlc`

## Install

### Option A — Install from GitHub (recommended, once published)

```
/plugin marketplace add https://github.com/YOUR-USERNAME/claude-hebrew-tts
/plugin install hebrew-tts@claude-hebrew-tts
```

### Option B — Install from local clone

```
git clone https://github.com/YOUR-USERNAME/claude-hebrew-tts.git
/plugin marketplace add /path/to/claude-hebrew-tts
/plugin install hebrew-tts@claude-hebrew-tts
```

### Option C — Plain local path (dev setup)

Clone or copy the folder anywhere and add it as a local marketplace:

```
/plugin marketplace add E:\tools\claude-hebrew-tts
/plugin install hebrew-tts@claude-hebrew-tts
```

## First-run setup

After installing, run the one-time venv setup inside the plugin folder:

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File "<plugin-dir>\skills\hebrew-tts\scripts\setup.ps1"
```

**macOS / Linux:**
```bash
bash "<plugin-dir>/skills/hebrew-tts/scripts/setup.sh"
```

The setup creates a self-contained venv inside the plugin and installs `edge-tts`. Takes ~30 seconds. Claude will also offer to run this for you automatically on first use.

## Usage

In any Claude Code session, say:

- **"תקריא"** — read Claude's most recent response aloud
- **"תקריא לי בקול: שלום עולם"** — read the given text
- **"תקריא עם הילה"** — use the female voice
- **"תקריא יותר מהר"** — faster speech rate
- **"תשמור כ-MP3"** — save audio file instead of playing

English triggers also work: *"read this aloud"*, *"speak this in Hebrew"*.

## How it works

1. Claude detects one of the trigger phrases and invokes the `hebrew-tts` skill.
2. The skill writes the text to a temp UTF-8 file (`_last.txt` in the scripts folder).
3. `speak.py` calls edge-tts, saves an MP3, and opens it via the OS default handler.
4. Audio plays asynchronously; Claude's turn completes immediately.

**Token cost:** ~80 tokens per read (one Write + one Bash call). The text being read is already in Claude's response — reading it doesn't duplicate it.

## Why edge-tts?

- **Free**, no API key, no quota
- **High quality** — actual Azure neural voices, same ones used in Microsoft Edge's "Read Aloud"
- **Hebrew with correct nikud-free pronunciation** — and vocative pronunciations like names sound natural
- **Offline-friendly Python package** — a single `pip install`

## Caveats

- edge-tts uses an undocumented endpoint Microsoft owns. They could change or throttle it at any time. For production use, swap in Azure Speech Services (paid) or another provider.
- Windows plays MP3s via whatever app is registered for `.mp3` (Windows Media Player, Groove, Edge, VLC…). If yours doesn't auto-play, use `--save` and open manually, or reassociate `.mp3`.
- The temp file `_last.txt` remains after each read — it's overwritten next time.

## Uninstall

```
/plugin uninstall hebrew-tts
/plugin marketplace remove claude-hebrew-tts
```

The plugin's `venv` folder is inside its own directory, so removing the plugin cleans up everything.

## License

MIT — see [LICENSE](LICENSE).

## Credits

- [edge-tts](https://github.com/rany2/edge-tts) by rany2 — the Python wrapper around Microsoft's neural voice endpoint
- Microsoft Azure Neural TTS — the actual voice synthesis
