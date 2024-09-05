import asyncio
import aiohttp
import json
from dotenv import load_dotenv
import os
import time

load_dotenv()

API_KEY = os.getenv('GRAPH_API_KEY')
URL = f"https://gateway-arbitrum.network.thegraph.com/api/{API_KEY}/subgraphs/id/DeKnEST3JAyseNgA81k1rBDGfSyYwqvSzwm1EzfzSQ97"
URL = "https://api.studio.thegraph.com/query/10090/gho_token_subgraph/version/latest"

QUERY = """
{
  transfers(first: 1000, where: {transferIndex_gt: %d}, orderBy: transferIndex, orderDirection: asc) {
    from
    to
    value
    transferIndex
    borrowCap
    supplyCap
    totalVariableDebt
    variableBorrowRate
    blockNumber
    blockTimestamp
    transactionHash
  }
}
"""


async def fetch_data(session, last_transfer_index):
    headers = {'Content-Type': 'application/json'}
    data = {
        'query': QUERY % last_transfer_index,
        'variables': {}
    }

    for attempt in range(3):
        try:
            async with session.post(URL, json=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Attempt {attempt + 1} failed for transferIndex > {last_transfer_index}. Status: {response.status}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for transferIndex > {last_transfer_index}. Error: {str(e)}")

        if attempt < 2:
            await asyncio.sleep(1)
    print(f"All attempts failed for transferIndex > {last_transfer_index}")
    return None


async def main():
    last_transfer_index = -1
    all_results = []

    async with aiohttp.ClientSession() as session:
        while True:
            result = await fetch_data(session, last_transfer_index)

            if result is None or not result.get('data', {}).get('transfers'):
                print("No more results or too many failures. Stopping.")
                break

            transfers = result['data']['transfers']
            all_results.extend(transfers)

            with open('transfer_results.json', 'w') as f:
                json.dump(all_results, f)

            last_transfer_index = transfers[-1]['transferIndex']
            print(f"Processed up to transferIndex {last_transfer_index}")

            if len(transfers) < 1000:
                print("Less than 1000 transfers returned. This might be the last batch.")
                break

            await asyncio.sleep(1)

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time} seconds")