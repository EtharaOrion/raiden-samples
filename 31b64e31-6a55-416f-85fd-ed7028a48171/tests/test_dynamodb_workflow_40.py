from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_dup_create_then_data_survives(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf41Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf41Tbl",
                 "--item", '{"pk":{"S":"keep"},"v":{"S":"orig"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "Wf41Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ResourceInUseException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf41Tbl", Key={"pk": {"S": "keep"}})
    assert from_item(resp["Item"]) == {"pk": "keep", "v": "orig"}
