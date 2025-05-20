from web3 import Web3
import json

# Ganache Local RPC URL
GANACHE_URL = "http://127.0.0.1:7545"  # Ensure this matches your Ganache RPC URL
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# Contract address and ABI
CONTRACT_ADDRESS = Web3.to_checksum_address("0x398028380f1EDD55A4E60904451Fa235027c8E24")  # Replace with your deployed contract address
with open("app/EcoPointsABI.json") as abi_file:  # Ensure this matches the correct path to your ABI file
    ABI = json.load(abi_file)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# Validate Ethereum address
def validate_address(address):
    if not w3.is_address(address):
        raise ValueError(f"Invalid Ethereum address: {address}")
    return w3.to_checksum_address(address)

# Award points to the admin address (simplified)
def award_points(points):
    try:
        # Use the admin Ethereum address for all transactions
        admin_address = "0x35fFF0c795c70F97D04624B2404B9c23BCa76357"  # Replace with your Ganache account address
        admin_private_key = "0xcb3a6b6c7a7974cf54439faf32fc8f2f511117a8f5ef05de5bbf623a9e78c5c3"  # Replace with the private key of the same Ganache account

        # Ensure points are integers
        points = int(points)

        # Get the nonce for the sender address
        nonce = w3.eth.get_transaction_count(admin_address)

        # Build the transaction
        txn = contract.functions.awardPoints(admin_address, points).build_transaction({
            'from': admin_address,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce
        })

        # Sign the transaction
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=admin_private_key)

        # Send the signed transaction
        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for the transaction receipt
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
        return txn_receipt

    except Exception as e:
        raise RuntimeError(f"Error awarding points: {str(e)}")

# Retrieve points for a user
def get_points(user_address):
    try:
        # Validate and checksum the user address
        user_address = validate_address(user_address)

        # Call the smart contract function to get points
        return contract.functions.getPoints(user_address).call()

    except Exception as e:
        raise RuntimeError(f"Error retrieving points: {str(e)}")
