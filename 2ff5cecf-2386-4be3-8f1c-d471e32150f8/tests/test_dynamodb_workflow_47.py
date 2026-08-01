from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_leaves_others_gettable(cli, ddb_client, tmp_path):
    for nm in ("Wf48A", "Wf48B"):
        ddb_client.create_table(
            TableName=nm,
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
    ddb_client.put_item(TableName="Wf48B", Item={"pk": {"S": "k"}, "v": {"S": "keep"}})
    rd = cli("dynamodb", "delete-table", "--table-name", "Wf48A")
    assert rd.returncode == 0
    result = cli(
        "dynamodb", "get-item", "--table-name", "Wf48B",
        "--key", '{"pk":{"S":"k"}}',
    )
    assert result.returncode == 0
    item = from_item(ddb_client.get_item(TableName="Wf48B", Key={"pk": {"S": "k"}})["Item"])
    assert item["v"] == "keep"
