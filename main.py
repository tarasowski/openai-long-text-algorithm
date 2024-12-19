from openai import OpenAI
import os

TEXT_GENERATION_MODEL = "gpt-4o-mini-2024-07-18" #"gpt-4"
TEXT_FORMATTING_MODEL = "gpt-4o-mini-2024-07-18"


client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)

# Function to count words in a text
def count_words(text):
    return len(text.split())


def format_text(generated_text):
  print(f"Start formatting the final output...")
  formatted_response = client.chat.completions.create(
      model=TEXT_FORMATTING_MODEL,
      messages=[
        {"role": "system", "content": "You are a precise writer."},
        {"role": "user", "content": f"The current text is:\n\n{generated_text}\n\n"
         f"Format this text, breakdown into meaningful paragraphs."}
        ],
      max_tokens=3000,
      temperature=0.7,
      )
  response = formatted_response.choices[0].message.content
  return response

# Function to generate text of a specific word count
def generate_text_exact_words(user_input, target_word_count):
    prompt = (
        f"Write an article or text based on the following input:\n\n"
        f"\"{user_input}\"\n\n"
        f"The article must be exactly {target_word_count} words long. "
        f"Be clear, concise, and focused on the topic without a summary or conclusion at the end."
    )

    # Call OpenAI's new ChatCompletion API
    response = client.chat.completions.create(
        model=TEXT_GENERATION_MODEL,
        messages=[
            {"role": "system", "content": "You are a precise writer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.7,
    )

    generated_text = response.choices[0].message.content
    word_count = count_words(generated_text)

    # If word count is insufficient, append additional content
    if word_count < target_word_count:
        additional_words_needed = target_word_count - word_count
        print(f"Generated text has {word_count} words. Adding {additional_words_needed} more words.")

        # Add the previous context to the messages
        additional_response = client.chat.completions.create(
            model=TEXT_GENERATION_MODEL,
            messages=[
                {"role": "system", "content": "You are a precise writer."},
                {"role": "user", "content": f"Write an article or text based on the following input:\n\n\"{user_input}\"\n\n"
                 f"The article must be exactly {target_word_count} words long."
                 f"Current text:\n\n{generated_text}\n\n"
                 f"Expand on the topic to add {additional_words_needed} words while maintaining coherence without a summary or conclusion at the end."}
            ],
            max_tokens=3000,
            temperature=0.7,
        )

        # Append the additional content to the original text
        generated_text += "\n\n" + additional_response.choices[0].message.content
        print(generated_text)

    # Final word count adjustment if needed
    final_word_count = count_words(generated_text)
    print("final word count: ", final_word_count)

    # If the generated text exceeds the target, truncate it
    if final_word_count > target_word_count:
        generated_text = " ".join(generated_text.split()[:target_word_count])

    # If the generated text is shorter than the target, generate additional content
    elif final_word_count < target_word_count:
        remaining_words = target_word_count - final_word_count
        print(f"Final text is short by {remaining_words} words. Generating additional content...")

        # Use the current content as context and generate the missing words
        additional_response = client.chat.completions.create(
            model=TEXT_GENERATION_MODEL,
            messages=[
                {"role": "system", "content": "You are a precise writer."},
                {"role": "user", "content": f"The current text is:\n\n{generated_text}\n\n"
                 f"Expand this text to ensure it reaches exactly {target_word_count} words. "
                 f"Add {remaining_words} more words in a coherent manner."
                 f"Don't duplicate information from the the provided text, add new information."}
            ],
            max_tokens=3000,
            temperature=0.7,
        )

        # Append the additional content to the original text
        additional_content = additional_response.choices[0].message.content
        generated_text += "\n\n" + additional_content

        # Ensure the final text meets the exact word count
        final_word_count = count_words(generated_text)
        if final_word_count > target_word_count:
            generated_text = " ".join(generated_text.split()[:target_word_count])

    response = format_text(generated_text)
    return response

# Example usage
if __name__ == "__main__":
    user_topic = input("Enter the topic you want the text to be about: ")
    target_word_count = 1500

    result = generate_text_exact_words(user_topic, target_word_count)
    with open("generated_text.txt", "w") as file:
        file.write(result)

    print("Text generated and saved as 'generated_text.txt'.")

