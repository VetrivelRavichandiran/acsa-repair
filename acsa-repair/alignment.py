"""Align semantically equivalent runtime events across source revisions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .trace import StateEvent


@dataclass(frozen=True)
class AlignedPair:
    reference: StateEvent
    candidate: StateEvent
    confidence: float
    rationale: str


def _location_similarity(reference: StateEvent, candidate: StateEvent) -> float:
    if reference.location.file != candidate.location.file:
        return 0.0
    distance = abs(reference.location.line - candidate.location.line)
    return max(0.0, 1.0 - distance / 20.0)


def align_events(reference_events: Iterable[StateEvent], candidate_events: Iterable[StateEvent]) -> list[AlignedPair]:
    """Greedily align by stable execution identity, then source proximity.

    This works when a patch shifts lines but preserves function, stack, iteration,
    and event sequence. Future versions can replace this with CFG/sequence alignment.
    """
    candidates = list(candidate_events)
    unused = set(range(len(candidates)))
    pairs: list[AlignedPair] = []

    for reference in reference_events:
        exact = [
            index for index in unused
            if candidates[index].alignment_key == reference.alignment_key
        ]
        if exact:
            chosen = max(exact, key=lambda index: _location_similarity(reference, candidates[index]))
            rationale = "matched function, stack, iteration, and event sequence"
            confidence = 0.85 + 0.15 * _location_similarity(reference, candidates[chosen])
        else:
            fallback = [
                index for index in unused
                if candidates[index].function == reference.function
                and candidates[index].iteration == reference.iteration
                and candidates[index].call_stack == reference.call_stack
            ]
            if not fallback:
                continue
            chosen = min(fallback, key=lambda index: abs(candidates[index].event_id - reference.event_id))
            confidence = 0.45 * _location_similarity(reference, candidates[chosen])
            rationale = "fallback match on function, stack, and iteration"
        unused.remove(chosen)
        pairs.append(AlignedPair(reference, candidates[chosen], round(confidence, 3), rationale))
    return pairs
