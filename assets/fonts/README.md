# Fonts

Bundled so the game looks the same on every machine and every language renders with full diacritics.

| File | Used for |
|---|---|
| `AlegreyaSC-ExtraBold.ttf` | Titles |
| `AlegreyaSC-Bold.ttf` | Buttons and labels |
| `AlegreyaSans-Bold.ttf` | Scores and emphasis |
| `AlegreyaSans-Medium.ttf` | Body text and tables |

Both families are by Huerta Tipográfica and released under the SIL Open Font License, included as `OFL-AlegreyaSC.txt` and `OFL-AlegreyaSans.txt`.

The two Alegreya Sans files are modified: the digits 0-9 point at the font's own lining tabular figures. The default old-style figures make `000450` read like `ooo45o`, and SDL_ttf cannot switch OpenType features.
