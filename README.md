<!-- README section #1 — drop into README.md. Figure path assumes repo-root-relative. -->

## Regime structure under uncertainty

Corn does not behave like a single process. Across 2016–2026 it moved through distinct **regimes** — stretches where volatility, trend, positioning, and fundamentals were internally consistent — separated by sharp structural breaks. This section detects those breaks empirically and characterizes each regime, because a forecaster that averages across fundamentally different states is confidently wrong in all of them. The aim is not a tighter price prediction; it is an honest map of *which state the market is in and how far it sits from its neighbors* — the foundation for quantifying uncertainty rather than hiding it.

### Method

Changepoints are detected from price alone, deliberately blind to external events, so the breaks are not biased toward what we expected to find. Detection runs on two representations, because a regime can change in two independent ways: a shift in the **mean/level** (trend) and a shift in **variance** (volatility). We use `ruptures` (PELT) with a penalty chosen from a stability sweep — the breakpoint count is robust across a range of penalties rather than hand-picked. Each candidate break is then validated with the test appropriate to its kind: a Chow test for level breaks, an F-test on return variance for volatility breaks. Because the dates were selected by the detector before testing, the reported p-values measure how *sharp* each break is, not pristine discovery inference; the stability sweep is the evidence that the breaks are real.

The other four sources — CFTC positioning, NOAA drought, FRED macro, USDA WASDE — are **not** used for detection. They enter at characterization: once the breaks define the regimes, these series describe what each regime *was*.

![Seven regimes from validated changepoints](notebooks/figures/01_regime_structure.png)

### Seven regimes

Two trend walls (Jan 2021, Aug 2023) plus five validated volatility breaks carve the decade into seven regimes:

| Regime | Span | Vol | Spec net (% OI) | Ending stocks (MMT) | Character |
|---|---|---|---|---|---|
| calm | 2016 – Jan '21 | 21% | n/a¹ | n/a¹ | range-bound baseline |
| breakout | Jan – Apr '21 | 26% | +29% | 38 | level breakout, specs pile in |
| burst (spr '21) | Apr – Jul '21 | 44% | +26% | 36 | weather-driven volatility burst |
| sustained high | Jul '21 – Sep '22 | 31% | +25% | 36 | elevated; spans Russia–Ukraine |
| cooling | Sep '22 – May '23 | 17% | +16% | 33 | high price, volatility cools |
| burst (spr '23) | May – Jul '23 | 43% | +1% | 57 | breakdown burst, specs gone |
| reverted | Aug '23 – 2026 | 21% | −0% | 51 | settled to a higher floor |

¹ CFTC and WASDE coverage begins in 2021; the calm-era fundamentals are uncovered, not zero.

### What the regimes reveal

The headline result is that **volatility alone cannot define a regime.** The spring 2021 and spring 2023 bursts ran nearly identical realized volatility (44% vs 43%) yet were opposite states. Spring 2021 was a crowded bull run-up — speculators net long 26% of open interest, stocks tight at 36 MMT, price rising. Spring 2023 was a breakdown — positioning flat at +1%, stocks loose at 57 MMT, price falling. A model aware only of volatility would treat the two identically and mistime both. This is the core argument for regime-aware, multi-factor features.

**The reversion found a higher floor.** The post-2023 calm settled near 440¢ against the 2016–2020 baseline of 366¢. Corn calmed down, but not back to where it started — "mean reversion" here reverts to a new level, not the old one, which is precisely the assumption a naïve long-run-average model gets wrong.

**COVID was not a regime change for corn.** The early-2020 dip is absorbed entirely inside the calm baseline with no break. Corn's volatility era was 2021–2022 — weather first, then geopolitics — and the equity/energy COVID reflex does not transfer to this commodity.

**Drought *level* does not drive volatility.** The highest drought reading of the decade (the 2022–23 cooling regime) coincided with the *lowest* volatility. It is drought *surprise*, not standing stress, that moves the market — a direct instruction for how drought should be featurized downstream (as a change or percentile, not a raw level).

### Limits, stated plainly

Detection uses front-month price only; term-structure shape (contango/backwardation) needs a second curve point and is deferred. Positioning and fundamentals are uncovered before 2021. The seven-regime segmentation is deliberately parsimonious — smaller wiggles such as the 2019 bump and the COVID dip were not carved out because they did not survive validation. The value of this analysis is not that it forecasts the next regime; it is that it makes the *current* regime, and its distance from its neighbors, explicit and measurable.

### Why this feeds the model

These regimes are never handed to the model as discrete labels. They justify a set of **continuous** regime features — volatility percentile, positioning extremity, drought change, macro state — that let a single forecaster condition on the state of the world instead of averaging over incompatible ones. The system's job is to recognize the regime it is in and to widen its uncertainty when that regime is unfamiliar.

## Baselines — the wall before regime features
 
Before adding any regime intelligence, we establish how well simple, honest methods forecast the **30-day-ahead corn return**. The target is the return, not the price level, on purpose: a tree model cannot predict above the prices it trained on, so a level target would flatline straight through the 2021 breakout. Every model is scored under **walk-forward evaluation** — train on the past, predict 30 days forward, slide the origin, never peek — with a 30-day embargo so training targets can't overlap the test window. Out-of-sample spans 2020–2026 (1,586 predictions).
 
The benchmark is the **random walk**: predict a zero return ("no change"). On a near-efficient market it is a stubborn bar, and the skill metric `1 − RMSE_model / RMSE_RW` measures whether anything actually beats it.
 
| Model | RMSE | MAE | Skill vs RW |
|---|---|---|---|
| Random walk | 0.0952 | 0.0736 | 0.000 |
| Seasonal naïve | 0.1199 | 0.0943 | −0.260 |
| AR(1) | 0.0989 | 0.0764 | −0.039 |
| Vanilla XGBoost | 0.0980 | 0.0776 | −0.030 |
 
Both naïve methods lose to the random walk: corn's calendar doesn't repeat (seasonal naïve, −26%) and recent momentum carries no usable edge (AR(1), −4%). The vanilla XGBoost — the first model allowed nonlinear structure, but deliberately blind to regime features — also fails to beat the wall in aggregate (−3%, well within the noise of overlapping targets). **Price-only signal does not beat "predict nothing."**
 
![Vanilla XGBoost vs random walk, RMSE improvement by year](notebooks/figures/02_xgb_vs_rw_by_year.png)
 
The aggregate hides the real finding: the vanilla model's skill is **regime-dependent**. It beats the random walk in the trending years — 2021 (breakout), 2023 (roll-over), 2024 (the decline into the lows) — where momentum features have a direction to grab. It loses in shock and calm years — 2020 (choppy pre-breakout), the 2022 Ukraine whipsaw, 2025 (tariff-policy noise), and the 2026 reverted plateau where the random walk is already near-optimal. The model has genuine edge but no idea *when* it has it, so it applies the same confidence in every regime and gets punished half the time.
 
That heterogeneity is the empirical case for the next stage. Regime features give the system awareness of which state it is in — lean on signal in trending regimes, widen uncertainty in shock and calm ones. The dispersion in the figure is exactly the opportunity the regime layer is built to capture, and the vanilla XGBoost RMSE of **0.0980** is the number it must beat.
 
**Caveats, stated plainly.** The 30-day targets overlap heavily, so the effective independent sample is far smaller than 1,586 and the year-to-year swings carry noise — read the pattern, not the third decimal. 2026 is a partial year and its result is the least reliable of the seven. And the honest reading of the whole table is the project's thesis in miniature: forecasting commodity prices is hard, the random walk is hard to beat, and the value of this system is in *quantifying what it doesn't know*, not in a tighter point forecast.