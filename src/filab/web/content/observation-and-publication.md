## A date on a row is not an availability timestamp

The observation date tells you which day's curve a row describes. Publication tells you when the source made information available. Retrieval tells you when your application obtained a particular response. These answer different questions.

**Goal:** Identify which timing claims the evidence supports. Prerequisite: [par yields and comparable observations](/lessons/par-yields-and-quotes).

Treasury uses indicative quotations obtained at or near **3:30 p.m.** each trading day and says rates are usually available by **6 p.m. Eastern**, subject to delays. Neither statement establishes the exact publication time of each historical row. This application records that time as **unknown**. Midnight in an XML observation-date field is a date encoding, not a market-opening release time.

## An information timeline

Define $O$ as the observation date, $P$ as a publication instant if known, $R$ as the retrieval instant, and $T$ as a proposed decision instant. A historical decision can only use the release if the release was available by then:

$$
P\le T.
$$

Here $O$ is a date and the other symbols are timestamps with time zones. Substituting $O$ for $P$ erases time-of-day information and does not prove the inequality. Retrieval proves possession by $R$; it does not prove possession at some earlier proposed decision time.

## Reproduce the source evidence

In the source panel, identify the observation date and UTC retrieval timestamp. The bundled example records when its maintainer acquired the file. Additional downloads record when this browser obtained the response. What separate evidence would establish when Treasury first published that observation?

Select November 6, 2026. Its published ten-year value is 4.86%. In the provenance panel, read the observation date, the actual UTC retrieval timestamp of the bundled response, and the unknown publication-time statement. The pinned response was acquired after these observation dates. It cannot establish the exact original release time or prove what someone could access on the morning of November 6.

The XML feed's **updated** timestamp can describe the generated feed. It is preserved in the raw response, but it is not promoted to the publication time of every old observation. Its presence does not create a point-in-time vintage archive.

## Predict, then experiment

Before changing the dates, predict which evidence will change. Compare November 5 and 6, then switch the first date to November 4. Observation dates and values change. The bundled response's retrieval time and hash remain the same because those rows came from the same acquisition.

Change a calendar to October, choose an October date, and compare it with November. Inspect the separate retrieval times and hashes for the contributing responses; an observation date does not become its retrieval date. The exploration notice marks the change from the worked example, and **Reset example** restores the pinned November data. Your browser downloads uncached months directly from Treasury. A failed download shows **No data**. Previously downloaded months remain saved in this browser.

Open the full viewer and explicitly refresh a year if online. Inspect the newly saved dataset's retrieval time. A new retrieval does not necessarily mean the underlying observations changed. Opening a lesson, resetting its example, and using its pinned month make no request to Treasury. Exploring other months can acquire new observations.

## Misconceptions and limits

A daily observation series need not be a same-day live feed. A usual release schedule is not a guarantee, and UTC retrieval time should not be confused with Eastern market time. The viewer compares historical observations; it does not certify a historically executable trading signal.

## Reflect and transfer

Explain what additional release or vintage evidence you would require for a strategy that makes decisions before the close. Why is a retrospective study still useful when point-in-time availability is unknown?

**Transfer:** A hypothetical source observes at 3:30 p.m., releases at 6:20 p.m., and your system retrieves at 6:25 p.m., all Eastern. Could a 4 p.m. decision use that release? What about a 6:30 p.m. decision?

::: answer
The 4 p.m. decision precedes publication. By 6:30 p.m. your system has the release, provided the stated retrieval succeeded. Those are hypothetical known timestamps; the Treasury rows in this lesson do not carry equivalent exact historical publication evidence.
:::

Source: [Treasury methodology and usual release timing](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology).
