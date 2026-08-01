from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_missing_table_then_create(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "put-item", "--table-name", "Wf21Tbl",
                 "--item", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    result = cli("dynamodb", "create-table", "--table-name", "Wf21Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf21Tbl",
                 "--item", '{"pk":{"S":"x"},"v":{"S":"ok"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf21Tbl", Key={"pk": {"S": "x"}})
    assert from_item(resp["Item"]) == {"pk": "x", "v": "ok"}
