from _ddb_http import to_item, from_item, to_av, from_av


import json


def test_workflow_scan_two_tables_isolated(cli, ddb_client, tmp_path):
    t1 = "wf_iso_a_12"
    t2 = "wf_iso_b_12"
    for t in (t1, t2):
        ddb_client.create_table(
            TableName=t,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
    ddb_client.put_item(TableName=t1, Item={"pk": {"S": "only1"}})
    ddb_client.put_item(TableName=t2, Item={"pk": {"S": "only2"}})
    r1 = cli("dynamodb", "scan", "--table-name", t1)
    assert r1.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r1.stdout)["Items"]} == {"only1"}
    r2 = cli("dynamodb", "scan", "--table-name", t2)
    assert r2.returncode == 0
    assert {i["pk"]["S"] for i in json.loads(r2.stdout)["Items"]} == {"only2"}
