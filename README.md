# GHO User research
Research on GHO users

## Pulling data

After creating a virtual environment, create a `.env` file with your subgraph API key as `GRAPH_API_KEY` or set up an environment variable.

Then run
```
pip install requirements.txt
python pull_data_from_subgraph.py
```

This will create a `results.json` file with the subgraph dump

