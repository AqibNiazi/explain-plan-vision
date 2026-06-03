"""
Builds a probabilistic look-ahead tree over the top treatment actions.
Returns the probability-weighted expected urgency at leaf nodes —
a quantitative measure of plan robustness.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List

from backend.config import settings
from backend.planning.engine import TreatmentPlan

URGENCY_MAP = {"immediate": 5, "high": 4, "medium": 3, "low": 2, "none": 1}
URGENCY_REV = {v: k for k, v in URGENCY_MAP.items()}

SUCCESS_PROB = 0.65
PARTIAL_PROB = 0.25
FAILURE_PROB = 0.10


@dataclass
class DecisionNode:
    step             : int
    action           : str
    state_description: str
    expected_urgency : float
    probability      : float
    children         : List[Any] = field(default_factory=list)
    is_leaf          : bool = False

    def to_dict(self) -> dict:
        return {
            "step"        : self.step,
            "action"      : self.action,
            "state"       : self.state_description,
            "urgency"     : self.expected_urgency,
            "probability" : self.probability,
            "is_leaf"     : self.is_leaf,
            "children"    : [c.to_dict() for c in self.children],
        }


def build_tree(plan: TreatmentPlan, initial_urgency: str) -> DecisionNode:
    """Build a look-ahead tree over the top non-monitoring actions."""
    uval    = URGENCY_MAP.get(initial_urgency, 3)
    actions = [a for a in plan.actions
               if a.get("category") != "monitoring"][:settings.lookahead_steps]
    root    = DecisionNode(
        step=0, action="Initial state",
        state_description=f"Disease detected. Urgency: {initial_urgency}",
        expected_urgency=uval, probability=1.0,
    )
    _expand(root, actions, uval, 1.0, 0)
    return root


def _expand(node: DecisionNode, remaining: list, cur_u: float, prob: float, depth: int):
    if depth >= settings.lookahead_steps or not remaining:
        node.is_leaf = True
        return
    act   = remaining[0]
    rest  = remaining[1:]
    label = act["action"][:55] + "..." if len(act["action"]) > 55 else act["action"]

    suc_u  = max(1, cur_u - 1)
    suc    = DecisionNode(depth+1, label,
                          f"Success — urgency: {URGENCY_REV.get(int(suc_u), 'low')}",
                          suc_u, round(prob * SUCCESS_PROB, 4))
    _expand(suc, rest, suc_u, prob * SUCCESS_PROB, depth + 1)

    par    = DecisionNode(depth+1, label,
                          f"Partial — urgency unchanged: {URGENCY_REV.get(int(cur_u), 'medium')}",
                          cur_u, round(prob * PARTIAL_PROB, 4))
    _expand(par, rest, cur_u, prob * PARTIAL_PROB, depth + 1)

    fail_u = min(5, cur_u + 1)
    fail   = DecisionNode(depth+1, label,
                          f"Failure — urgency: {URGENCY_REV.get(int(fail_u), 'high')}",
                          fail_u, round(prob * FAILURE_PROB, 4), is_leaf=True)

    node.children = [suc, par, fail]


def expected_leaf_urgency(root: DecisionNode) -> float:
    """Probability-weighted expected urgency across all leaf nodes."""
    leaves  = _leaves(root)
    total_p = sum(l.probability for l in leaves)
    if total_p < 1e-8:
        return root.expected_urgency
    return sum(l.expected_urgency * l.probability for l in leaves) / total_p


def _leaves(node: DecisionNode) -> List[DecisionNode]:
    if node.is_leaf or not node.children:
        return [node]
    out: List[DecisionNode] = []
    for c in node.children:
        out.extend(_leaves(c))
    return out
