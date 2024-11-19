# CONTRACT VARIABLES REPLACEMENT
pushd service

cp .env.deploy .env

echo "Changing contract addresses..."
echo 'TOKEN_CONTRACT="{{token_contract}}"' >> .env
echo 'SHOP_CONTRACT="{{shop_contract}}"' >> .env
echo 'BANK_CONTRACT="{{bank_contract}}"' >> .env

echo "Copying private key..."
echo "{{team_key}}" > eth.key

popd