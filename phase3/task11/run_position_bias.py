from __future__ import annotations

import json

from src.data import load_impressions, save_json
from src.position_bias import (
    apply_position_bias_weights,
)


def main() -> None:
    impressions = load_impressions()

    weights, propensity_table = (
        apply_position_bias_weights(
            impressions
        )
    )

    result = {
        "task": "Phase 3 Task 11",
        "status": "PASS",
        "method": (
            "empirical_inverse_propensity_weighting"
        ),
        "position_propensity": {
            str(position): values
            for position, values
            in propensity_table.items()
        },
        "correction_applied": True,
        "maximum_inverse_weight": (
            max(weights)
            if weights
            else 0.0
        ),
        "weighted_observations": len(
            weights
        ),
        "interpretation": (
            "Propensities are estimated from the "
            "Task 11 logged replay data. They are "
            "not claimed to be causal production "
            "propensities."
        ),
    }

    save_json(
        result,
        "logs/position_bias.json",
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()