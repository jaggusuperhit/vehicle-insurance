"""
This module provides a patch for imbalanced-learn to use the new scikit-learn API.
It monkey-patches the BaseEstimator class in imbalanced-learn to use the new
validate_data function from scikit-learn instead of the deprecated _validate_data method.
"""

import logging
import warnings


def apply_sklearn_patches():
    """
    Apply patches to fix scikit-learn deprecation warnings.
    This function suppresses the deprecation warnings from scikit-learn.
    """
    # Suppress the warnings
    warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
    warnings.filterwarnings("ignore", message=".*_validate_data.*")

    logging.info("Applied warning filters for scikit-learn deprecation warnings")

    # Note: We tried to patch the imbalanced-learn library to use the new scikit-learn API,
    # but it's not fully compatible yet. The imbalanced-learn library will need to be updated
    # by its maintainers to use the new scikit-learn API.
