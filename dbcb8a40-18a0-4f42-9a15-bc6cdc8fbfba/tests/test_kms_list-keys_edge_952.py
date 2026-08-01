def test_list_keys_marker_returns_next_disjoint_page(cli, kms):
    import json

    for i in range(4):
        kms.rpc("CreateKey", {"Description": "marker-page-%d" % i})

    first = cli("kms", "list-keys", "--limit", "2")
    assert first.returncode == 0, first.stderr
    page1 = json.loads(first.stdout)
    assert len(page1["Keys"]) == 2
    assert page1["Truncated"] is True
    assert page1["NextMarker"]

    second = cli("kms", "list-keys", "--limit", "2", "--marker", page1["NextMarker"])
    assert second.returncode == 0, second.stderr
    page2 = json.loads(second.stdout)
    assert len(page2["Keys"]) == 2

    ids1 = {k["KeyId"] for k in page1["Keys"]}
    ids2 = {k["KeyId"] for k in page2["Keys"]}
    assert not (ids1 & ids2), "marker was ignored; pages overlap"
