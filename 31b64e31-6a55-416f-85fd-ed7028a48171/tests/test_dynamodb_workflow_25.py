from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_condition_fail_leaves_original_multi(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf26Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf26Tbl",
                 "--item", '{"pk":{"S":"cf"},"count":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf26Tbl",
                 "--item", '{"pk":{"S":"cf"},"count":{"N":"2"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf26Tbl", Key={"pk": {"S": "cf"}})
    assert resp["Item"]["count"]["N"] == "1"
