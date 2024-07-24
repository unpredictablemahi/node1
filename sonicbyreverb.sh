#!/usr/bin/env node

import { Connection, Keypair, Transaction, SystemProgram, sendAndConfirmTransaction, LAMPORTS_PER_SOL } from "@solana/web3.js";
import chalk from "chalk";
import bs58 from "bs58";
import readline from "readline";

const BOLD_BLUE = '\033[1;34m';
const NC = '\033[0m';

console.log();
if (!Connection) {
    console.error(`${BOLD_BLUE}Error: @solana/web3.js is not installed. Please install it using npm.${NC}`);
    process.exit(1);
}

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.question(`Enter your Solana wallet private key:`, async (privkey) => {
    try {
        const connection = new Connection("https://api.devnet.solana.com", 'confirmed');

        const from = Keypair.fromSecretKey(bs58.decode(privkey));
        const to = Keypair.generate();

        const txCount = 95;

        console.log();
        console.log(`${BOLD_BLUE}Generating ${txCount} transactions with random amounts and delays...${NC}`);
        console.log();

        for (let i = 0; i < txCount; i++) {
            // Generate a random amount between 0.001 and 0.003 SOL (adjust range as needed)
            const randomAmount = (Math.random() * (0.003 - 0.001) + 0.001).toFixed(4);
            const lamports = Math.round(parseFloat(randomAmount) * LAMPORTS_PER_SOL);

            const transaction = new Transaction().add(
                SystemProgram.transfer({
                    fromPubkey: from.publicKey,
                    toPubkey: to.publicKey,
                    lamports: lamports,
                }),
            );

            try {
                const signature = await sendAndConfirmTransaction(
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
    } catch (error) {
        console.error(chalk.red('Error:'), error.message);
    } finally {
        rl.close();
    }
});
