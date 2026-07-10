from pipeline_lib import (
    causal_ml_audit,
    causal_models,
    construct_variables,
    descriptive_audit,
    final_memo,
    sensitivity,
)


if __name__ == "__main__":
    construct_variables()
    descriptive_audit()
    causal_models()
    sensitivity()
    causal_ml_audit()
    final_memo()
