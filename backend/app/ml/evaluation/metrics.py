from __future__ import annotations

from dataclasses import asdict, dataclass

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score


@dataclass
class ClassificationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float | None


def calculate_classification_metrics(y_true, y_pred, y_prob=None) -> ClassificationMetrics:
    roc_auc = None
    if y_prob is not None:
        try:
            roc_auc = float(roc_auc_score(y_true, y_prob, multi_class="ovr"))
        except Exception:  # noqa: BLE001
            roc_auc = None
    return ClassificationMetrics(
        accuracy=float(accuracy_score(y_true, y_pred)),
        precision=float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        recall=float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        f1=float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        roc_auc=roc_auc,
    )

