import logging

import pytest

from execution_repair_pipeline.surgery_guard import SAFEGRAD_LOGGER, guarded


def test_clean_safegrad_run_returns_its_path():
    def train():
        logging.getLogger(SAFEGRAD_LOGGER).warning("unrelated warning")
        return "/ckpt/C"

    assert guarded(train) == "/ckpt/C"


def test_skipped_surgery_invalidates_the_arm():
    def train():
        log = logging.getLogger(SAFEGRAD_LOGGER)
        for _ in range(3):
            log.warning("SafeGradHFTrainer: failed to compute alignment gradient (%s); skipping surgery this step.", "CUDA out of memory")
        return "/ckpt/C"

    with pytest.raises(ValueError, match="skipped its alignment step 3 time"):
        guarded(train)
    assert not any(type(h).__name__ == "SkipCounter" for h in logging.getLogger(SAFEGRAD_LOGGER).handlers)
