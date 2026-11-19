# Seals: priority without disclosure

A seal is the SHA-256 hash of a private document, published with a timestamp. The document stays private; the hash
proves that this exact text existed at the time of the commit that published it. If its content is later claimed by
anyone, the author can open the document and anyone can check it against the hash below.

| Sealed (UTC) | What | SHA-256 |
|---|---|---|
| 2026-11-19 19:29 | The White Dragon discovery loop (from question to pre-registered, beacon-drawn, confirmed prediction), the ordering law of the operation table, and RSOS lineage forensics. Author: R. A. Elu | `60c65ef3fd4452898e5a596c2b7acfca5c852ace22ffdf3cea1fbcad16e1e09f` |

Check: `sha256sum <document>` must print the hash above. The document contains a random nonce, so the hash cannot be
reproduced by guessing its text.
