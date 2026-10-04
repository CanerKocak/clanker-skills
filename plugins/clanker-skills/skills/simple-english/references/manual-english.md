# Clear instructions and faithful rewrites

## Examples

Each rewrite uses only information supplied by the source.

| Source | Rewrite | Detail preserved |
| --- | --- | --- |
| In order to restart the service, you should run `systemctl restart api`. | To restart the service, you should run `systemctl restart api`. | The action remains a recommendation. |
| The connection failed. | The connection failed. | The cause is unknown. Do not add a password or network diagnosis. |
| The deployment might have caused the outage. | The deployment may have caused the outage. | The cause remains uncertain. Keep `might` if `may` could be read as permission. |
| The key must be rotated before the next deployment. | Rotate the key before the next deployment. | This is a requirement with a deadline. |
| The request is validated and its signature is verified by the gateway. | The gateway validates the request and verifies its signature. | Validation and signature verification remain distinct operations. |
| The import failed after 12 records. | The import failed after 12 records. | The record count is known. The cause and the state of those records are unknown. |
| At this point in time, the job is in progress. | The job is running. | The work is ongoing. Do not change it to a completed action. |

Use "You should rotate the key" when the source recommends rotation.
Use "Rotate the key" when the source requires it. Retain the author of a
recommendation when that attribution matters.

Remove redundant phrases only when they add no meaning. `To` can replace
`in order to`; `because` can replace `due to the fact that`. Keep distinctions
such as a historical value versus a projected value, or an exact byte match
versus equivalent behavior.

## Strict ASD-STE100 requests

ASD-STE100 defines writing rules and a controlled dictionary. Its approved
words have specific meanings and grammatical uses. Technical names and verbs
have separate rules. A generic list of simple synonyms cannot replace these
checks.

For a strict request, use the official edition that the user specifies.
If no edition is specified, check the official publication before selecting
one. The [official downloads page](https://www.asd-ste100.org/STE_downloads.html)
provides the standard. [Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)
was published on 15 January 2025.

Check the relevant dictionary entries, permitted meanings, parts of speech,
verb forms, technical terminology, and word-count rules. Issue 9 limits
procedural sentences to 20 words and descriptive sentences to 25. Use the
standard's counting rules rather than a whitespace count.

Check modal verbs in context. For example, Issue 9 permits `could` as a form
of `can` but does not permit that form to express possibility. Do not apply
a blanket ban on `could` in the practical default style.

If the standard or dictionary cannot be checked, state the gap and provide
an STE-style draft. Claim compliance only to the extent supported by the
checks actually performed. Preserve diagnostic quotations and code verbatim;
separate them from the prose being checked.
