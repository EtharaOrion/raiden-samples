from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_condition_not_exists_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_cond1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cond1",
                 "--item", '{"pk":{"S":"k1"},"v":{"S":"original"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_cond1",
                 "--item", '{"pk":{"S":"k1"},"v":{"S":"changed"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Tbl_cond1", Key={"pk": {"S": "k1"}})
    assert from_item(resp["Item"]) == {"pk": "k1", "v": "original"}
