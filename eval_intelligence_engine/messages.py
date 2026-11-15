import re

LANGS = ("en", "fr", "es")

TEXT = {
    "use_case": {"en": "use case", "fr": "cas d'usage", "es": "caso de uso"},
    "summary": {
        "en": "version {v} · arms {arms} · contamination {c}",
        "fr": "version {v} · bras {arms} · contamination {c}",
        "es": "versión {v} · brazos {arms} · contaminación {c}",
    },
    "columns": {
        "en": ("metric", "tier", "risk", "oracle", "min n", "threshold"),
        "fr": ("métrique", "niveau", "risque", "oracle", "n min", "seuil"),
        "es": ("métrica", "nivel", "riesgo", "oráculo", "n mín", "umbral"),
    },
    "gap": {"en": "gap", "fr": "lacune", "es": "laguna"},
    "gap_note": {"en": "no valid oracle, kept visible", "fr": "aucun oracle valide, laissée visible", "es": "sin oráculo válido, se mantiene visible"},
    "draft_hash": {"en": "draft hash", "fr": "empreinte du brouillon", "es": "hash del borrador"},
    "approved": {"en": "approved", "fr": "approuvé", "es": "aprobado"},
    "verified": {"en": "VERIFIED", "fr": "VÉRIFIÉ", "es": "VERIFICADO"},
    "refused": {"en": "REFUSED", "fr": "REFUSÉ", "es": "RECHAZADO"},
    "rejected": {"en": "REJECTED", "fr": "REJETÉE", "es": "RECHAZADA"},
    "ok": {"en": "ok", "fr": "ok", "es": "ok"},
    "approval": {"en": "approval", "fr": "approbation", "es": "aprobación"},
    "holdout": {"en": "holdout", "fr": "réserve", "es": "reserva"},
    "suite_line": {
        "en": "{n:>5} prompts  {d:>5} distinct  top opening {o:.0%}",
        "fr": "{n:>5} prompts  {d:>5} distincts  ouverture max {o:.0%}",
        "es": "{n:>5} prompts  {d:>5} distintos  apertura máx {o:.0%}",
    },
    "suites_failed": {
        "en": "{k} suite(s) rejected in {where}",
        "fr": "{k} suite(s) rejetée(s) dans {where}",
        "es": "{k} suite(s) rechazada(s) en {where}",
    },
    "holdout_hash": {"en": "holdout sha256", "fr": "sha256 de la réserve", "es": "sha256 de la reserva"},
}

ERRORS = (
    (r"plan is not approved or its hash does not match",
     {"fr": "le plan n'est pas approuvé ou son empreinte ne correspond pas", "es": "el plan no está aprobado o su hash no coincide"}),
    (r"holdout hash does not match",
     {"fr": "l'empreinte de la réserve ne correspond pas", "es": "el hash de la reserva no coincide"}),
    (r"(\w+): (\d+) rows hold only (\d+) distinct prompts once digits are masked",
     {"fr": r"\1 : \2 lignes ne contiennent que \3 prompts distincts une fois les chiffres masqués",
      "es": r"\1: \2 filas contienen solo \3 prompts distintos al enmascarar los dígitos"}),
    (r"(\w+): one opening covers (\d+%) of the suite, limit is (\d+%)",
     {"fr": r"\1 : une même ouverture couvre \2 de la suite, la limite est \3",
      "es": r"\1: una misma apertura cubre \2 de la suite, el límite es \3"}),
    (r"(\w+): suite is empty", {"fr": r"\1 : la suite est vide", "es": r"\1: la suite está vacía"}),
)


def t(key: str, lang: str, **values) -> str:
    entry = TEXT[key].get(lang, TEXT[key]["en"])
    return entry.format(**values) if values else entry


def error(message: str, lang: str) -> str:
    if lang == "en":
        return message
    for pattern, translations in ERRORS:
        if re.fullmatch(pattern, message):
            return re.sub(pattern, translations[lang], message)
    return message
