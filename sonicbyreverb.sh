#!/usr/bin/env node

const web3 = require("@solana/web3.js");
const chalk = require("chalk");
const bs58 = require("bs58");

const BOLD_BLUE = '\x1b[1;34m';
const NC = '\x1b[0m';

console.log();
if (!web3.Connection) {
    console.error(`${BOLD_BLUE}Error: @solana/web3.js is not installed. Please install it using npm.${NC}`);
    process.exit(1);
}

const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});

readline.question(`Enter your solana wallet private key:`, async (privkey) => {
    const connection = new web3.Connection("https://devnet.sonic.game", 'confirmed');

    const from = web3.Keypair.fromSecretKey(bs58.decode(privkey));
    const to = web3.Keypair.generate();

    const txCount = 95;

    console.log();
    console.log(`${BOLD_BLUE}Generating ${txCount} transactions with random amounts and delays...${NC}`);
    console.log();

    for (let i = 0; i < txCount; i++) {
        // Generate a random amount between 0.001 and 0.003 SOL (adjust range as needed)
        const randomAmount = (Math.random() * (0.003 - 0.001) + 0.001).toFixed(4);
        const lamports = Math.round(parseFloat(randomAmount) * web3.LAMPORTS_PER_SOL);

        const transaction = new web3.Transaction().add(
            web3.SystemProgram.transfer({
                fromPubkey: from.publicKey,
                toPubkey: to.publicKey,
                lamports: lamports,
            }),
        );

        try {
            const signature = await web3.sendAndConfirmTransaction(
                connection,
                transaction,
                [from],
                {
                    commitment: 'confirmed',
                }
            );

            console.log(chalk.blue('Transaction successful. Tx hash:'), signature);
            console.log("Amount sent:", randomAmount, "SOL");
            console.log();
        } catch (error) {
            console.error(chalk.red('Transaction failed:'), error.message);
            console.log();
        }

        // Generate a random delay between 1 and 5 seconds
        const randomDelay = Math.floor(Math.random() * 5) + 1;
        await new Promise(resolve => setTimeout(resolve, randomDelay * 1000));
    }

    readline.close();
});

