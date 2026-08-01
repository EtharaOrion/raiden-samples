from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_recreate_preserves_data(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_rpd1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_rpd1",
                 "--item", '{"pk":{"S":"rp1"},"v":{"S":"kept"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_rpd1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ResourceInUseException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl_rpd1", Key={"pk": {"S": "rp1"}})
    assert from_item(resp["Item"]) == {"pk": "rp1", "v": "kept"}
