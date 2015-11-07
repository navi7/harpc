#!/usr/bin/env bash

echo -n '{"name": "ivan@example.com", "account_type": "beer_buyer"}' | python rpc_call.py account create
echo -n '{"name": "jura@example.com", "account_type": "basic_user"}' | python rpc_call.py account create

echo -n '{"name": "jura@example.com"}' | python rpc_call.py account get_by_name

echo -n '{"name": "WarmBeer"}' | python rpc_call.py product create
echo -n '{"name": "ColdBeer"}' | python rpc_call.py product create
echo -n '{"name": "BlueBeer"}' | python rpc_call.py product create


echo -n '{"name": "BigBackyard"}' | python rpc_call.py warehouse create

echo -n '{"warehouse": "BigBackyard", "product": "ColdBeer", "quantity": 840}' | python rpc_call.py warehouse intake
echo -n '{"warehouse": "BigBackyard", "product": "ColdBeer", "quantity": 320 }' | python rpc_call.py warehouse intake
echo -n '{"warehouse": "BigBackyard", "product": "WarmBeer", "quantity": 200}' | python rpc_call.py warehouse intake

echo -n '{"warehouse": "BigBackyard", "buyer": "ivan@example.com", "product": "ColdBeer", "quantity": 365}' | python rpc_call.py warehouse ship_to
echo -n '{"warehouse": "BigBackyard", "buyer": "jura@example.com", "product": "WarmBeer", "quantity": 1}' | python rpc_call.py warehouse ship_to

