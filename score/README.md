## Mode Scoring on Mode Protocol 🔮 :ringed_planet: :mag:

for Proper explanation on how this application works, See [EXPLANATION](./EXPLANATION.md)

NOTE: Instead of Debank i am usinig Covalent(as they support mode network)

NOTE: All data is being tested on ethereum chain, but design in such a way that it can be switch to mode easily(will need top erc20 tokens on the mode network, and other stuffs )

**Onchain Transaction** model (powered by [Covalent](./images/modescore.drawio.png))

- :acount: account for credits, debits transactions, transfers, frequency, the cumulative balance now, and more
- :chains: fetch up to 100 top ERC20 tokens (by market capitalization) via [CoinMarketCap](https://coinmarketcap.com/) API
- :bar_chart: analyze time series of latest 400 transactions on wallet
- :investigate: inspect historical OHLCV for last 30 days


## Clone This Project :key: :lock: :package:

### 1. Clone locally

Download or clone the repo to your machine, running in terminal

```bash
git clone  ... my-project-name
cd my-project-name
```

### 2. Install dependencies

Create vitual environment
```bash
python<version> -m venv <virtual-environment-name>              # run in venv
source venv/bin/activate                                        # start venv
```

Run either of the commands below. You'll need either `pip` or `conda` package manager

```bash
pip install -r requirements.txt                                 # using pip
conda create --name <env_name> --file requirements.txt          # using Conda
```

### 3. Environment variables

Create a `.env` local file in your root folder. The required credentials are

```bash
PLAID_ENV='sandbox'
DATABASE_URL='postgres_url'
```

### 4. Execute locally

For testing th application use the Swagger API platform. Running the commands below will redirect you to the Swagger, where you'll be able to run _in the backend_ trial mode score calculations

```bash
cd my-project-name
uvicorn main:app –-reload
```

> :warning: The app will execute properly, only if you set up a correct and complete `.env` file. <br/>

Procure the necessary keys here:

- CoinMarketCap API key &#8594; follow the Developers guide [here](https://coinmarketcap.com/api/documentation/v1/#section/Introduction)
- Covalent API key &#8594; register [here](https://goldrush.dev/platform/auth/register/)


```bash
.
└───
    ├── config
    │   └── config.json               # contains all model parameters and weights - tune this file to alter the model
    ├── helpers
    │   ├── feedback.py               # string formatter returning a qualitative score feedback
    │   ├── helper.py                 # helper functions for data cleaning
    │   ├── metrics_covalent.py       # logic to analyze a user's ETH wallet data (powered by Covalent)
    │   ├── models.py                 # aggregate granular credit score logic into 4 metrics
    │   ├── risk.py                   # high/med/low risk indicators
    │   ├── score.py                  # aggregate score metrics into an actual credit score
    │   └── README.md                 # docs on credit score model & guideline to clone project
    ├── market
    │   └── coinmarketcap.py          # hit a few endpoints on Coinmarketcap (live exchange rate & top cryptos)
    ├── routers
    │   ├── covalent.py               # core execution logic - Covalent
    │   ├── kyc.py                    # core execution logic - KYC template
    │   └── README.md                 # docs on the API endpoints
    ├── support
    │   ├── assessment.py             # tracking memory allocation in database
    │   ├── crud.py                   # Create, Read, Update, Delete (CRUD) - database handler
    │   ├── database.py               # set up PostgreSQL database to store computed scores
    │   ├── models.py                 # clases with data to enter in new row of database
    │   └── schemas.py                # http request classes
    ├── tests
    │   ├── covalent                  # directory with 2 files: Covalent pytests & dummy test data json
    ├── validator
    │   ├── covalent.py               # functions calling Covalent API
    ├── LICENCE
    ├── main.py                       # core file - handle API calls, directing them to the router folder
    ├── Procfile                      # set up uvicorn app in Heroku
    ├── pytest.ini                    # pytest initializer
    ├── README.md                     # this landing page
    └── requirements.txt              # Python modules required to run this project
```


TODO:
- save score to db
- add stamina and and traffic
- Proper testing