from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_multiple_get_each(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf46Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    for k in ("a", "b", "c"):
        r = cli(
            "dynamodb", "update-item", "--table-name", "Wf46Tbl",
            "--key", '{"pk":{"S":"' + k + '"}}',
            "--update-expression", "SET v = :v",
            "--expression-attribute-values", '{":v":{"S":"' + k + '"}}',
        )
        assert r.returncode == 0
    for k in ("a", "b", "c"):
        item = from_item(ddb_client.get_item(TableName="Wf46Tbl", Key={"pk": {"S": k}})["Item"])
        assert item["v"] == k
