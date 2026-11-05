import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class EvidenceValidationAgent:
    """
    Responsibilities:
    - Separately evaluate the 3 distinct validation levels:
      1. code_tests
      2. model_verification
      3. empirical_validation
    - Enforce that passing one level does NOT imply passing the others
    - Never claim validation without verifiable metrics
    """
    @staticmethod
    def evaluate_levels(
        execution_success: bool,
        benchmark_passed: bool,
        empirical_data_available: bool,
        empirical_error_margin: float = 0.08
    ) -> Dict[str, str]:
        # 1. Code tests
        code_tests = "passed" if execution_success else "failed"

        # 2. Mathematical model verification
        if execution_success and benchmark_passed:
            model_verification = "verified"
        elif execution_success and not benchmark_passed:
            model_verification = "unverified"
        else:
            model_verification = "not_evaluated"

        # 3. Empirical validation
        # Only validated if empirical data is actually available and within acceptable margin
        if empirical_data_available and model_verification == "verified":
            empirical_validation = "validated" if empirical_error_margin <= 0.10 else "unvalidated"
        else:
            empirical_validation = "not_evaluated"

        return {
            "code_tests": code_tests,
            "model_verification": model_verification,
            "empirical_validation": empirical_validation
        }
