import asyncio
import aiohttp
import json
from dotenv import load_dotenv
import os
import time

load_dotenv()

API_KEY = os.getenv('GRAPH_API_KEY')
URL = f"https://gateway.thegraph.com/api/{API_KEY}/subgraphs/id/DLuE98kEb5pQNXAcKFQGQgfSQ57Xdou4jnVbAEqMfy3B"

QUERY = """
{
  users(first: 1000, skip: %d, orderBy: id) {
    id
    borrowedReservesCount
    lifetimeRewards
    borrowHistory(first: 1000, orderBy: timestamp, orderDirection: asc) {
      action
      amount
      assetPriceUSD
      borrowRate
      borrowRateMode
      stableTokenDebt
      variableTokenDebt
      timestamp
      txHash
      caller {
        id
      }
      reserve {
        name
        symbol
        decimals
        debtCeiling
      }
      referrer {
        id
      }
    }
    liquidationCallHistory(first: 1000 orderBy: timestamp orderDirection: desc) {
      action
      collateralAmount
      collateralAssetPriceUSD
      principalAmount
      principalReserve {
        name
        symbol
        decimals
      }
      liquidator
      timestamp
      txHash
    }
    mintUnbackedHistory(first: 1000 orderBy: timestamp orderDirection: desc) {
      amount
      timestamp
    }
    backUnbackedHistory(first: 1000 orderBy: timestamp orderDirection: desc) {
      amount
      backer {
        id
      }
      timestamp
    }
    rebalanceStableBorrowRateHistory(first: 1000 orderBy: timestamp orderDirection: desc) {
      action
      borrowRateFrom
      borrowRateTo
      timestamp
      txHash
    }
    redeemUnderlyingHistory(first: 1000 orderBy: timestamp orderDirection: desc) {
      action
      amount
      assetPriceUSD
      reserve {
        name
        symbol
        decimals
      }
      timestamp
      txHash
    }
    repayHistory(first: 1000 orderBy: timestamp orderDirection: desc) {
      action
      amount
      assetPriceUSD
      repayer {
        id
      }
      reserve {
        name
        symbol
        decimals
      }      
      timestamp
      txHash
      useATokens
    }
    supplyHistory(first: 1000 orderBy: timestamp orderDirection: desc)  {
      action
      amount
      assetPriceUSD
      caller {
        id
      }
      reserve {
        name
        symbol
        decimals
      }      
      timestamp
      txHash
    }
    swapHistory(first: 1000 orderBy: timestamp orderDirection: desc) {
      action
      borrowRateModeFrom
      borrowRateModeTo
      stableBorrowRate
      variableBorrowRate
      timestamp
      txHash
    }
    usageAsCollateralHistory(first: 1000 orderBy: timestamp orderDirection: desc){
      action
      fromState
      toState
      txHash
      timestamp
    }
    userEmodeSetHistory(first: 1000 orderBy: timestamp orderDirection: desc){
      action
      categoryId
      id
      timestamp
      txHash
    }
  }
}
"""


async def fetch_data(session, skip):
    headers = {'Content-Type': 'application/json'}
    data = {
        'query': QUERY % skip,
        'variables': {}
    }

    for attempt in range(3):
        try:
            async with session.post(URL, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Attempt {attempt + 1} failed for skip {skip}. Status: {response.status}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for skip {skip}. Error: {str(e)}")

        if attempt < 2:
            await asyncio.sleep(1)
    print(f"All attempts failed for skip {skip}")
    return None


async def main():
    skip = 0
    batch_size = 5
    all_results = []

    async with aiohttp.ClientSession() as session:
        while True:
            tasks = [fetch_data(session, skip + i * 1000) for i in range(batch_size)]
            results = await asyncio.gather(*tasks)

            valid_results = [r for r in results if r is not None and r.get('data', {}).get('users')]
            all_results.extend(valid_results)

            with open('arb_results.json', 'w') as f:
                json.dump(all_results, f)

            if len(valid_results) < batch_size:
                print("No more results or too many failures. Stopping.")
                break

            skip += batch_size * 1000
            print(f"Processed up to skip {skip}")

            await asyncio.sleep(1)


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time} seconds")