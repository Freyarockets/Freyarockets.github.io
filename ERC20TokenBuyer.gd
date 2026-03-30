extends Node2D

var web3 = preload("res://addons/godot_web3/godot_web3.gd")
var tokenContractAddress = "0xYourTokenAddress"
var uniswapRouterAddress = "0xUniswapRouterAddress"

var walletAddress = ""
var tokenBalance = 0.0

func _ready():
    # Connect to wallet
    connect_to_wallet()
    # Check token balance
    check_token_balance()

func connect_to_wallet():
    var provider = web3.Provider.new()
    provider.connect("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID")
    walletAddress = yield(provider.enable(), "completed") 
    print("Wallet connected: ", walletAddress)

func check_token_balance():
    var contract = web3.Contract.new(tokenContractAddress, abi)
    var balance = yield(contract.methods.balanceOf(walletAddress).call(), "completed")
    tokenBalance = balance / (10 ** 18)  # assuming 18 decimals
    print("Token balance: ", tokenBalance)

func approve_tokens(spender:String, amount:float):
    var contract = web3.Contract.new(tokenContractAddress, abi)
    yield(contract.methods.approve(spender, amount * (10 ** 18)).send({'from': walletAddress}), "completed")
    print("Tokens approved for spending:", amount)

func buy_tokens(amount:float):
    approve_tokens(uniswapRouterAddress, amount)
    # Create transaction to call Uniswap router to swap ETH for tokens
    var contract = web3.Contract.new(uniswapRouterAddress, uniswap_abi)
    yield(contract.methods.swapExactETHForTokens(
        amount*
        (10**18),
        ["0xETHAddress", tokenContractAddress],
        walletAddress,
        OS.get_unix_time() + 300
    ).send({'from': walletAddress, 'value': amount * (10 ** 18)}), "completed")
    print("Tokens purchased: ", amount)