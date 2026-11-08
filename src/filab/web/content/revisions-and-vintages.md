## Preserve the evidence behind an answer

A **retrieval** is an acquisition of source bytes. A **revision** changes an observation. A **snapshot** is the immutable normalized dataset used by a comparison. Repeating a retrieval can produce different feed metadata while leaving every yield unchanged.

**Goal:** Reproduce an old answer after new data arrives. Prerequisite: [observation and publication](/lessons/observation-and-publication).

The application keeps raw-response hashes, acquisition timestamps, and versioned normalized observations. A raw SHA-256 hash identifies exact response bytes. A snapshot identifier reflects normalized values and cached coverage under a normalizer version. Different feed-generation timestamps can change the raw hash without changing the snapshot. A newly loaded coverage period changes the dataset even if its overlapping yields agree.

## Derive the effect of a hypothetical revision

Let $s$ be the ten-year minus two-year spread in basis points. Suppose a hypothetical revision changes only the ten-year rate by $\delta$ in annual decimal units. Then

$$
s'=10{,}000[(y_{10}+\delta)-y_2]=s+10{,}000\delta.
$$

If $\delta=0.0010$, the ten-year yield is revised upward by 10 bp and the spread rises 10 bp. This arithmetic does not assert that Treasury actually revised the observation.

## Reproduce two versions

The published February 18 example is ten-year **4.55%**, two-year **4.29%**, spread **26 bp**. Against February 14's **21 bp**, the spread change is **+5 bp**.

Toggle **Hypothetical revised ten-year yield** in the experiment. Its second-date ten-year rate is increased by **0.10 percentage point**, to **4.65%** on the default dates. The hypothetical second spread is **36 bp** and the hypothetical spread change is **+15 bp**. The chart, table, and label describe that hypothetical scenario. The source snapshot remains intact.

## Predict, then experiment

Predict whether the first-date spread will change when only the second-date ten-year observation is revised. Toggle the version, reconcile both spreads, and return to the published sample. Compare the provenance identifier before and after: the hypothetical calculation is tied to the same source snapshot and is explicitly labeled as a modification.

In the full viewer, save or note a snapshot identifier, refresh a selected year range, and reopen the old version with the saved-dataset radio cards. A completed refresh offers a new dataset without switching your current comparison. Identical normalized observations reuse a version. An unsuccessful refresh cannot activate a partially imported range.

## Misconceptions and limits

Today's retrieval of old dates is not proof that today's values were originally published unchanged. Keeping acquisitions from now onward builds a local revision history; it cannot recover unobserved historical vintages. A checksum identifies bytes, not financial correctness. Source agreement and calculation checks are still required.

The Federal Reserve's fitted nominal curve is a separate potential source for later valuation work. Its revised parameter history must retain its own provenance; it must not be silently merged with Treasury par yields.

## Reflect and transfer

What must accompany a saved research result besides its chart? Explain why an old answer may remain reproducible even when a later dataset gives a different answer.

**Transfer:** A hypothetical revision increases both second-date yields by 10 bp. What happens to their spread and to the spread change from the first date?

::: answer
Both spread measures are unchanged because the two revisions cancel in the difference. Individual yields still differ from the original version. Reproducing only the spread would miss that revision.
:::

Sources: [Treasury feed documentation](https://home.treasury.gov/treasury-daily-interest-rate-xml-feed), [Federal Reserve nominal-curve revision policy](https://www.federalreserve.gov/data/nominal-yield-curve.htm). The revision experiment is hypothetical.
