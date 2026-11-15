import logging

SAFEGRAD_LOGGER = "safetune.interventions.harden.safegrad"
SKIP_MARKERS = ("skipping surgery", "cannot compute alignment gradient")


class SkipCounter(logging.Handler):
    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self.skipped = 0
        self.first = ""

    def emit(self, record: logging.LogRecord) -> None:
        message = record.getMessage()
        if any(marker in message for marker in SKIP_MARKERS):
            self.skipped += 1
            self.first = self.first or message[:200]


def guarded(train_fn):
    logger = logging.getLogger(SAFEGRAD_LOGGER)
    counter = SkipCounter()
    logger.addHandler(counter)
    try:
        path = train_fn()
    finally:
        logger.removeHandler(counter)
    if counter.skipped:
        raise ValueError(f"SafeGrad skipped its alignment step {counter.skipped} time(s), so this arm is plain SFT, not SafeGrad; first warning: {counter.first}")
    return path
