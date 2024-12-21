import OpenAI from "openai"
import fs from "fs"

const TEXT_GENERATION_MODEL = "gpt-4o-mini-2024-07-18"; // "gpt-4"
const TEXT_FORMATTING_MODEL = "gpt-4o-mini-2024-07-18";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
})

// Function to count words in a text
function countWords(text) {
  return text.split(/\s+/).filter(word => word).length;
}

async function formatText(generatedText, targetWordCount) {
  console.log("Start formatting the final output...");
  const formattedResponse = await openai.chat.completions.create({
    model: TEXT_FORMATTING_MODEL,
    messages: [
      { role: "system", content: "You are a precise writer." },
      {
        role: "user",
        content: `Keep the word count of ${targetWordCount} and format the text:\n\n${generatedText}`,
      },
    ],
    max_tokens: 4000,
    temperature: 0.1,
  });

  return formattedResponse.choices[0].message.content;
}

// Function to generate text of a specific word count
async function generateTextExactWords(userInput, targetWordCount) {
  let prompt = `Write an article or text based on the following input:\n\n"${userInput}"\n\nThe article must be exactly ${targetWordCount} words long. Be clear, concise, and focused on the topic without a summary or conclusion at the end.`;

  console.log("Starting content generation....")
  let response = await openai.chat.completions.create({
    model: TEXT_GENERATION_MODEL,
    messages: [
      { role: "system", content: "You are a precise writer." },
      { role: "user", content: prompt },
    ],
    max_tokens: 4000,
    temperature: 0.7,
  });

  let generatedText = response.choices[0].message.content;
  let wordCount = countWords(generatedText);

  // If word count is insufficient, append additional content
  while (wordCount < targetWordCount) {
    const additionalWordsNeeded = targetWordCount - wordCount;
    console.log(`Generated text has ${wordCount} words. Adding ${additionalWordsNeeded} more words.`);

    const additionalResponse = await openai.chat.completions.create({
      model: TEXT_GENERATION_MODEL,
      messages: [
        { role: "system", content: "You are a precise writer." },
        {
          role: "user",
          content: `Write an article or text based on the following input:\n\n"${userInput}"\n\nThe article must be exactly ${targetWordCount} words long. Current text:\n\n${generatedText}\n\nExpand on the topic to add ${additionalWordsNeeded} words while maintaining coherence without a summary or conclusion at the end.`,
        },
      ],
      max_tokens: 4000,
      temperature: 0.7,
    });

    generatedText += "\n\n" + additionalResponse.choices[0].message.content;
    wordCount = countWords(generatedText);
  }

  // If the generated text exceeds the target, truncate it
  if (wordCount > targetWordCount) {
    generatedText = generatedText.split(/\s+/).slice(0, targetWordCount).join(" ");
  }

  // Format the final output
  const formattedResponse = await formatText(generatedText, targetWordCount);
  return [generatedText, formattedResponse];
}

// Example usage
(async () => {
  const userTopic = "What to do in Andorra during the winter break?";
  const targetWordCount = 2500;

  const [generatedText, formattedResponse] = await generateTextExactWords(userTopic, targetWordCount);
  fs.writeFileSync("generated_text.txt", generatedText, "utf8");
  fs.writeFileSync("formatted_response.txt", formattedResponse, "utf8");

  console.log("Text generated and saved as 'generated_text.txt'.");
})();

