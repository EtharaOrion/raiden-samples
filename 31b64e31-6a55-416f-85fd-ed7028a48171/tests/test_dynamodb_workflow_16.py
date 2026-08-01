from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_ddbclient_seed_cli_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf17Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="Wf17Tbl", Item={"pk": {"S": "seed"}, "v": {"S": "byhttp"}})
    result = cli("dynamodb", "get-item", "--table-name", "Wf17Tbl",
                 "--key", '{"pk":{"S":"seed"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf17Tbl", Key={"pk": {"S": "seed"}})
    assert from_item(resp["Item"]) == {"pk": "seed", "v": "byhttp"}
