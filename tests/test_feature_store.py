from feature_store.store import FeatureStore


def _sample_rows():
    return [
        {"v1": 0.1, "amount_log": 1.5, "label": 0},
        {"v1": 0.2, "amount_log": 2.1, "label": 1},
    ]


def test_write_and_read_round_trip(tmp_path):
    store = FeatureStore(root=tmp_path / "fs")
    version = store.write_feature_group("txns", _sample_rows())

    df = store.read_feature_group("txns")
    assert len(df) == 2
    assert "amount_log" in df.columns

    df_pinned = store.read_feature_group("txns", version=version)
    assert len(df_pinned) == 2


def test_multiple_versions_are_tracked(tmp_path):
    store = FeatureStore(root=tmp_path / "fs")
    v1 = store.write_feature_group("txns", _sample_rows())
    v2 = store.write_feature_group("txns", _sample_rows() + _sample_rows())

    assert v1 != v2
    versions = store.list_versions("txns")
    assert len(versions) == 2

    latest_df = store.read_feature_group("txns")  # defaults to latest
    assert len(latest_df) == 4


def test_missing_group_raises(tmp_path):
    store = FeatureStore(root=tmp_path / "fs")
    try:
        store.read_feature_group("does_not_exist")
        assert False, "expected KeyError"
    except KeyError:
        pass