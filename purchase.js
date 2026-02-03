// purchase.js
import { ethers } from "https://cdnjs.cloudflare.com";

const TOKEN_ADDRESS = "0xc128052d1C0E0CB95dFa8b39Bc5e89a999eC7d71";
const ERC20_ABI = [
    "function transfer(address to, uint256 amount) public returns (bool)",
    "function decimals() view returns (uint8)",
    "function symbol() view returns (string)"
];

export async function executePurchase(merchantAddress, price) {
    if (!window.ethereum) {
        alert("Please install MetaMask to continue.");
        return;
    }

    try {
        const provider = new ethers.BrowserProvider(window.ethereum);
        const signer = await provider.getSigner();
        const contract = new ethers.Contract(TOKEN_ADDRESS, ERC20_ABI, signer);

        const decimals = await contract.decimals();
        const symbol = await contract.symbol();
        const amount = ethers.parseUnits(price.toString(), decimals);

        console.log(`Initiating transfer of ${price} ${symbol}...`);

        const tx = await contract.transfer(merchantAddress, amount);
        alert(`Transaction sent! Hash: ${tx.hash}`);

        const receipt = await tx.wait();
        console.log("Transaction Confirmed:", receipt);
        return receipt;
    } catch (error) {
        console.error("Transaction failed:", error);
        alert("Payment Error: " + (error.reason || error.message));
    }
}
