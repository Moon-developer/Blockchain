"""main.py

FastApi server to interact with our Blockchain class

"""
__author__ = "Marco Fernandes"
__version__ = "1.0.0"
__maintainer__ = "Marco Fernandes"

__created__ = "2020/08/18"
__updated__ = "2020/08/18"

__status__ = "Testing"

from typing import List, Optional
from blockchain import Blockchain
from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4

app = FastAPI(title='Blockchain with FastApi')

# Instantiate the Blockchain
blockchain = Blockchain()

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')


# used to create a new transaction
class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: int


# used to access list of nodes when creating new ones
class Nodes(BaseModel):
    nodes: List[str]


# used to generate a response model for all our returns
class Response(BaseModel):
    message: Optional[str] = None
    new_chain: List[dict] = None
    total_nodes: list = None
    chain: List[dict] = None
    length: int = None
    index: int = None
    transactions: List[dict] = None
    proof: int = None
    previous_hash: str = None


@app.get('/mine/', status_code=200, response_model=Response, response_model_exclude_unset=True)
async def mine() -> dict:
    """
    Mine a new block
    :return: <dict> message, index, transaction, proof, previous hash
    """
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return response


@app.post('/transactions/new/', status_code=201, response_model=Response, response_model_exclude_unset=True)
async def new_transaction(values: Transaction) -> dict:
    """
    Create a new transaction to a block
    :param values: <Transaction> our new transaction to create 
    :return: <dict> message
    """
    index = blockchain.new_transaction(values.sender, values.recipient, values.amount)
    response = {'message': f'Transaction will be added to Block {index}'}
    return response


@app.get('/chain/', status_code=200, response_model=Response, response_model_exclude_unset=True)
async def full_chain() -> dict:
    """
    Gives users the full Blockchain.
    :return: <dict> chains, length of list
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return response


@app.post('/nodes/register/', status_code=201, response_model=Response, response_model_exclude_unset=True)
def register_nodes(values: Nodes) -> dict:
    """
    Accept a list of new nodes in the form of URLs
    :param values: <Nodes> list of nodes
    :return: <dict> message, new total nodes
    """
    for node in values.nodes:
        blockchain.register_node(node)
    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return response


@app.get('/nodes/resolve/', status_code=200, response_model=Response, response_model_exclude_unset=True)
def consensus() -> dict:
    """
    Resolves any conflicts — to ensure a node has the correct chain
    :return: <dict> message, latest chain
    """
    replaced = blockchain.resolve_conflicts()
    message = 'Our chain was replaced' if replaced else 'Our chain is authoritative'
    response = {'message': message, 'new_chain': blockchain.chain}
    return response
