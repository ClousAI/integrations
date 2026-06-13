/**
 * Tiny runnable Vercel AI SDK example using the Clous tools.
 *
 * Install: npm install
 * Env:     CLOUS_API_KEY (Clous), OPENAI_API_KEY (the model)
 * Run:     npx tsx src/example.ts
 */

import { openai } from "@ai-sdk/openai";
import { generateText } from "ai";

import { clousTools } from "./clous-tools";

async function main() {
  if (!process.env.CLOUS_API_KEY) {
    throw new Error("Set CLOUS_API_KEY first (get one at https://clous.ai).");
  }

  const { text } = await generateText({
    model: openai("gpt-4o-mini"),
    maxSteps: 6,
    tools: clousTools,
    prompt:
      "Resolve the ticker MSFT to a CIK, then list Microsoft's three most recent 8-K filings.",
  });

  console.log(text);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
