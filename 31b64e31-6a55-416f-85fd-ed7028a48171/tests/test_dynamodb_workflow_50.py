from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_matches_cli_output_state(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf51Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf51Tbl",
                 "--item", '{"pk":{"S":"o"},"a":{"S":"x"},"b":{"N":"5"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf51Tbl",
                 "--key", '{"pk":{"S":"o"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf51Tbl", Key={"pk": {"S": "o"}})
    assert from_item(resp["Item"]) == {"pk": "o", "a": "x", "b": 5}
