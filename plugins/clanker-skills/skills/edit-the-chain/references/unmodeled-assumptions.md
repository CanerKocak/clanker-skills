# Unmodeled assumptions

Facts the environment always applies. Our spec, quote, or mental model never
named them.

This is not a fee list. A fee is one shape. The class is **an implicit fact
we treated as free, cosmetic, already priced, or identical to a proxy.**

## How to hunt

For each thing the change **always** does, or each number it treats as
"the cost" / "the slot" / "the lock":

1. What does the runtime, chain, DB, library, or wallet **always** do then?
2. Did we read that from a primary source (docs, chain param, schema,
   trigger, library code) or from a comment / wallet label / analogy?
3. Is it in the quote, the lock, the send, or the UI?
4. If not: unmodeled. Name it. Price it, gate on it, or stop doing the
   "always".

## Shapes (general)

| Shape | Question |
|-------|----------|
| **Always-on side effect** | We always set / attach / tag / log / persist X. What does the environment charge, lock, or mutate when X is present? |
| **Wrong oracle** | We classify on a convenient proxy (balance, flag, label). What signal does the environment actually use? |
| **Cap shown as cost** | A limit, `fee_limit`, buffer, or wallet "fee" line. Is that a ceiling, a burn, or a display? |
| **Same number, two jobs** | Two mechanisms share a magnitude (both "1"). Are they the same sink? |
| **Leftover treated as discount** | Inventory, cache, or prior state exists. Does the product still charge as-if-empty, or did we silently give that away? |
| **Model vs receipt** | Quote uses formula F. Receipts include G. Is G in F? |
| **Already handled elsewhere** | A trigger, unique index, or library already enforces it. Would a second writer parkour? |
| **Sibling rail / surface** | This rail or screen models it. Does the twin? |

## What the reviewer must do

- Read the brief's "we always…" and "we assume… is free" lines first.
- For each, find the environment rule (param, opcode, trigger, wallet
  estimate) from a primary source, not from the brief.
- Report only **live** misses: a producer in this diff or this path today.
- Do not invent a second check on a path that cannot produce the state.

## What the reviewer must not do

- Demand the billed number and the admission gate be the same sum without
  showing that they measure the same thing.
- Restore a path the brief rejected unless this tree still has a producer.
- Treat a wallet estimate as the protocol bill without checking which
  number the wallet printed (cap vs burn vs side effect).
- Ask for a sibling guard ("refund has X so dismiss must") without a live
  producer and a non-zero inventory count.

After the review returns, the parent still runs the receiving gate. Priority
labels and reviewer agreement are search signals, not orders.
