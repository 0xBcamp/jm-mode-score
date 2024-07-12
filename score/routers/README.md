
## [COVALENT](https://goldrush.dev/) : mode score model based on your ETH wallet address

```bash
    POST {BASE_URL}/credit_score/covalent
```

Headers

```bash
    {"Content-Type": "application/json"}
```

Body

```bash
      {
        "chainid": "ETHEREUM_CHAINID_FOR_NOW"
        "eth_address": "YOUR_ETH_WALLET_ADDRESS",
        "covalent_key": "FREE_COVALENT_API_KEY",
        "coinmarketcap_key": "YOUR_COINMARKETCAP_KEY",
      }
```

Response: **200**

- Sample response for a test ETH address

```bash
    {
        "endpoint": "/credit_score/covalent",
        "status": "success",
        "score": 686,    
    }
    }
```

- Generalized Typescript response

```bash
    export interface IScoreResponseCovalent {
        endpoint: '/credit_score/covalent';
        status: 'success' | 'error';
        score: number;
        };
    }
```

Response: **400**

- Sample error response from a non-existing ETH wallet address

```bash
    {
        "endpoint": "/credit_score/covalent",
        "status": "error",
        "message": "Malformed address provided: 0xnonexistentethwalletaddressexample"
    }
```

## KYC : KYC verification model

```bash
    POST {BASE_URL}/kyc
```

Headers

```bash
    {"Content-Type": "application/json"}
```

Body

```bash
      {
        "chosen_validator": "YOUR_CHOSEN_VALIDATOR",
        "coinmarketcap_key": "YOUR_COINMARKETCAP_KEY",

        "eth_address" [optional]: "YOUR_ETH_WALLET_ADDRESS",
        "covalent_key" [optional]: "FREE_COVALENT_API_KEY",
      }
```

Response: **200**

- Sample response from Plaid Sandbox environment

```bash
    {
        "endpoint": "/kyc",
        "status": "success",
        "validator": "plaid",
        "kyc_verified": true,
    }
```

- Generalized Typescript response

```bash
    export interface IScoreResponseKYC {
        endpoint: '/kyc';
        status: 'success' | 'error';
        validator: 'covalent';
        kyc_verified: boolean;
    }
```

Response: **400**

- Sample error response from an expired Coinbase access token

```bash
    {
        "endpoint": "/kyc",
        "status": "error",
        "message": "Unable to fetch accounts data: The access token expired"
    }
```
