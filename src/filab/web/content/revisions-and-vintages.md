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

The published November 6 example is ten-year **4.86%**, two-year **4.51%**, spread **35 bp**. Against November 5's **38 bp**, the spread change is **−3 bp**.

Toggle **Hypothetical revised ten-year yield** in the experiment. Its second-date ten-year rate is increased by **0.10 percentage point**, to **4.96%** on the default dates. The hypothetical second spread is **45 bp** and the hypothetical spread change is **+7 bp**. The chart, table, and label describe that hypothetical scenario. The source snapshot remains intact.

## Predict, then experiment

In the full viewer, use **Export selected dataset** to save the snapshot and its raw source responses. Use **Import dataset** in another browser to reopen that same evidence. Saved datasets otherwise belong to the browser that downloaded them. Clearing site data removes them from that browser.

Predict whether the first-date spread will change when only the second-date ten-year observation is revised. Toggle the version, reconcile both spreads, and return to the published sample. Compare the provenance identifier before and after: the hypothetical calculation is tied to the same source snapshot and is explicitly labeled as a modification.

Use either calendar to explore another month, then compare your chosen dates. The hypothetical revision always adds 10 bp to the selected second date's published ten-year yield; its description follows that date and its original yield. A missing observation cannot be revised. The exploration notice separates your selected data from the worked example above. **Reset example** restores the pinned November dates, source observations, and published-sample setting.

In the full viewer, save or note a snapshot identifier, refresh a selected year range, and reopen the old version with the saved-dataset radio cards. A completed refresh offers a new dataset without switching your current comparison. Identical normalized observations reuse a version. An unsuccessful refresh cannot activate a partially imported range.

## Misconceptions and limits

Today's retrieval of old dates is not proof that today's values were originally published unchanged. Keeping acquisitions from now onward builds a revision history in this browser; it cannot recover unobserved historical vintages. A checksum identifies bytes, not financial correctness. Source agreement and calculation checks are still required.

The Federal Reserve's fitted nominal curve is a separate potential source for later valuation work. Its revised parameter history must retain its own provenance; it must not be silently merged with Treasury par yields.

## Reflect and transfer

What must accompany a saved research result besides its chart? Explain why an old answer may remain reproducible even when a later dataset gives a different answer.

**Transfer:** A hypothetical revision increases both second-date yields by 10 bp. What happens to their spread and to the spread change from the first date?

::: answer
Both spread measures are unchanged because the two revisions cancel in the difference. Individual yields still differ from the original version. Reproducing only the spread would miss that revision.
:::

Sources: [Treasury feed documentation](https://home.treasury.gov/treasury-daily-interest-rate-xml-feed), [Federal Reserve nominal-curve revision policy](https://www.federalreserve.gov/data/nominal-yield-curve.htm). The revision experiment is hypothetical.
