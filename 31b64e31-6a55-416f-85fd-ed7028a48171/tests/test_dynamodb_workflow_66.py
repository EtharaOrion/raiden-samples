from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_seed_via_ddbclient_cli_condition_fail(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf67Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="Wf67Tbl", Item={"pk": {"S": "s"}, "v": {"S": "seeded"}})
    result = cli("dynamodb", "put-item", "--table-name", "Wf67Tbl",
                 "--item", '{"pk":{"S":"s"},"v":{"S":"overwrite"}}',
                 "--condition-expression", "attribute_not_exists(pk)")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf67Tbl", Key={"pk": {"S": "s"}})
    assert from_item(resp["Item"]) == {"pk": "s", "v": "seeded"}
