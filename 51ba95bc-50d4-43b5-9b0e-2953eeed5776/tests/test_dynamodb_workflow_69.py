from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_then_missing_table_get_negative(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_ptmg1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_ptmg1",
                 "--item", '{"pk":{"S":"pm1"},"v":{"S":"stored"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Tbl_ptmg1_x",
                 "--key", '{"pk":{"S":"pm1"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl_ptmg1", Key={"pk": {"S": "pm1"}})
    assert from_item(resp["Item"]) == {"pk": "pm1", "v": "stored"}
