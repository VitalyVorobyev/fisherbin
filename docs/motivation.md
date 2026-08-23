# Motivation

## Problem

Many analyses start with high-dimensional observations $x$ but ultimately estimate a much smaller parameter vector $\theta$.

Sometimes the data must be reduced to a finite number of bins: for template fits, interpretability, storage, speed, or compatibility with existing inference tools. Conventional binning groups observations by geometric proximity in $x$. In several dimensions this scales poorly and does not directly optimize the quality of parameter estimation.

FisherBin asks a different question:

> Given a fixed number of bins, how should observations be grouped to preserve as much information as possible about the parameters of interest?

The key idea is to represent each observation by its **score**

$$
s(x;\theta_0)=\nabla_\theta \log p(x\mid\theta)\big|_{\theta_0},
$$

or the corresponding score of an event intensity. Two observations should share a bin when they have similar parameter sensitivity, even if they are far apart in the original observation space.

## Scope

The core problem is intentionally small:

- input: score vectors and optional event weights;
- output: a mapping from score space to a finite set of bins;
- objective: retain Fisher information after binning.

How the scores are obtained is a separate concern. They may come from an analytic model, linear components, automatic differentiation, finite differences, a simulator, or a learned estimator.

## Applications

The method is useful whenever a continuous or high-dimensional measurement must be reduced while preserving information for parameter estimation. Candidate areas include:

- template and mixture fits in physics and other sciences;
- spectroscopy and chemometrics;
- astronomy and photon/event data analysis;
- hyperspectral and remote-sensing measurements;
- mass spectrometry and chromatography;
- microscopy and other photon-counting instruments;
- distributed sensing or bandwidth-limited measurements;
- simulation-based inference.

The common structure matters more than the domain: many observed variables, relatively few parameters, and a finite representation required downstream.

## Non-goals

FisherBin is not a general compression library, a neural-network quantizer, or a complete inference framework. It focuses only on information-aware partitioning and the diagnostics needed to trust that partition.
