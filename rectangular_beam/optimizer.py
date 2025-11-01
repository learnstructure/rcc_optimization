# import numpy as np
# import math


# def predict_beam_design(input_data, models):
#     """
#     Predicts beam design (b, d, Ast) using all available models.
#     Returns a dictionary of predictions keyed by model name.
#     """

#     # --- Validate Input ---
#     required = ["fck", "fy", "Mu"]
#     for key in required:
#         if key not in input_data:
#             raise ValueError(f"Missing required input: {key}")

#     fck = float(input_data["fck"])
#     fy = float(input_data["fy"])
#     Mu = float(input_data["Mu"])

#     X = np.array([[fck, fy, Mu]])

#     all_predictions = {}

#     for name, model in models.items():
#         try:
#             preds = model.predict(X)
#             # Assume each model outputs [b, d, Ast]
#             b, d, Ast = map(float, preds[0])
#             all_predictions[name] = {
#                 "b": math.ceil(b),
#                 "d": math.ceil(d),
#                 "Ast": math.ceil(Ast),
#             }
#         except Exception as e:
#             all_predictions[name] = {"error": str(e)}

#     result = {"input": {"fck": fck, "fy": fy, "Mu": Mu}, "predictions": all_predictions}

#     return result

import numpy as np
import math

# --- Import your validation and cost functions ---
from rectangular_beam.validation import (
    get_xul,
    calculate_moment_capacity,
    Ast_limits,
    bd_ratio,
    get_cost,
    is_valid_design,
)


def correct_invalid_predictions(
    y_pred, X_test, step_percent=0.01, max_step_percent=0.2
):
    """
    Corrects invalid beam designs by perturbing b, d, Ast to satisfy design checks.
    """
    corrected_preds = []

    for i in range(len(y_pred)):
        b, d, Ast = y_pred[i]
        fck, fy, Mu = X_test[i]

        # Already valid and b >= 200
        if is_valid_design(b, d, Ast, fck, fy, Mu) and b >= 200:
            corrected_preds.append([b, d, Ast])
            continue

        found_valid = False
        min_cost = float("inf")
        best_combo = [b, d, Ast]

        # Try step perturbations
        for p in np.arange(step_percent, max_step_percent + step_percent, step_percent):
            delta_b = b * p
            delta_d = d * p
            delta_Ast = Ast * p

            for db in [-delta_b, 0, delta_b]:
                new_b = b + db
                if new_b < 200:
                    continue

                for dd in [-delta_d, 0, delta_d]:
                    new_d = d + dd
                    for dAst in [-delta_Ast, 0, delta_Ast]:
                        new_Ast = Ast + dAst

                        if is_valid_design(new_b, new_d, new_Ast, fck, fy, Mu):
                            cost = get_cost(new_b, new_d, new_Ast)
                            if cost < min_cost:
                                min_cost = cost
                                best_combo = [new_b, new_d, new_Ast]
                                found_valid = True

            if found_valid:
                break  # exit early

        best_combo[0] = max(best_combo[0], 200)
        corrected_preds.append(best_combo)

    return np.array(corrected_preds)


def predict_beam_design(input_data, models):
    """
    Predicts beam design (b, d, Ast) using all available models and corrects invalid predictions.
    Returns a dictionary of predictions keyed by model name.
    """

    # --- Validate Input ---
    required = ["fck", "fy", "Mu"]
    for key in required:
        if key not in input_data:
            raise ValueError(f"Missing required input: {key}")

    fck = float(input_data["fck"])
    fy = float(input_data["fy"])
    Mu = float(input_data["Mu"])

    X = np.array([[fck, fy, Mu]])

    all_predictions = {}
    y_pred = []
    X_test = []

    # --- Get raw predictions ---
    for name, model in models.items():
        try:
            preds = model.predict(X)
            b, d, Ast = map(float, preds[0])
            y_pred.append([b, d, Ast])
            X_test.append([fck, fy, Mu])
        except Exception as e:
            all_predictions[name] = {"error": str(e)}

    # --- Correct invalid predictions ---
    if y_pred:
        corrected = correct_invalid_predictions(y_pred, X_test)
        for idx, name in enumerate(models.keys()):
            b, d, Ast = corrected[idx]
            all_predictions[name] = {
                "b": math.ceil(b),
                "d": math.ceil(d),
                "Ast": math.ceil(Ast),
            }

    result = {"input": {"fck": fck, "fy": fy, "Mu": Mu}, "predictions": all_predictions}

    return result
