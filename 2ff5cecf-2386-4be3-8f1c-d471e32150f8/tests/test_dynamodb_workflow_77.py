from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multi_delete_and_get_all_gone(cli, ddb_client, tmp_path):
    for nm in ("Wf78A", "Wf78B"):
        ddb_client.create_table(
            TableName=nm,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        ddb_client.put_item(TableName=nm, Item={"pk": {"S": "x"}})
    for nm in ("Wf78A", "Wf78B"):
        rd = cli("dynamodb", "delete-table", "--table-name", nm)
        assert rd.returncode == 0
    for nm in ("Wf78A", "Wf78B"):
        rg = cli(
            "dynamodb", "get-item", "--table-name", nm,
            "--key", '{"pk":{"S":"x"}}',
        )
        assert rg.returncode != 0
        assert "ResourceNotFoundException" in rg.stderr
