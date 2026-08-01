from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_all_types_roundtrip(cli, ddb_client, tmp_path):
    t = "wf_alltypes_35"
    ddb_client.create_table(
        TableName=t,
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    ddb_client.put_item(TableName=t, Item={
        "pk": {"S": "a"},
        "s": {"S": "text"},
        "n": {"N": "42"},
        "b": {"BOOL": False},
        "ss": {"SS": ["x", "y"]},
    })
    r1 = cli("dynamodb", "scan", "--table-name", t)
    assert r1.returncode == 0
    item = json.loads(r1.stdout)["Items"][0]
    assert item["s"]["S"] == "text"
    assert item["n"]["N"] == "42"
    assert item["b"]["BOOL"] is False
    assert set(item["ss"]["SS"]) == {"x", "y"}
    stored = ddb_client.get_item(TableName=t, Key={"pk": {"S": "a"}})["Item"]
    assert set(stored["ss"]["SS"]) == {"x", "y"}
