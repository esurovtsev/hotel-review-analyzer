import os
import json
import pandas as pd
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
openai_model = "gpt-4o-mini"
openai_temperature = 0.7


def analyze_text_with_openai(text):
    """
    Analyze a single text using OpenAI API for sentiment and key topics, returning structured JSON output.

    Args:
        text (str): Input text to analyze.

    Returns:
        dict: Structured analysis results including key topics and sentiment.
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant for text analysis.",
                },
                {
                    "role": "user", 
                    "content": f"""
                        Analyze the following text and provide the result in JSON format. The JSON should include:
                        - "key_topics": A list of key topics mentioned in the text.
                        - "sentiment": An object that contains a summary of the overall sentiment (only values allowed as overal sentiment are: "positive", "neutral", or "negative") along with reasoning.

                        Text: {text}

                        Your response should be in JSON format. Do not include any explanations, only provide a RFC8259 compliant.

                        The JSON output should be in the following format:
                        {{
                            "key_topics": [
                                "hotel cleanliness",
                                "service speed"
                            ],
                            "sentiment": {{
                                "summary": "neutral",
                                "reasoning": "the text mentions a positive aspect of cleanliness"
                            }}
                        }}

                        Do not include markdown code blocks in your response. Remove the ```json markdown from the output.
                    """
                }
            ],
            model=openai_model,
            temperature=openai_temperature
        )

        # Parse the JSON output from the response
        structured_analysis = response.choices[0].message.content.strip()

        # Validate and parse the JSON output
        if not structured_analysis:
            print("Error: Received an empty response from OpenAI.")
            return None

        # Convert the JSON string to a Python dictionary
        analysis_result = json.loads(structured_analysis)
        analysis_result["review"] = text
        return analysis_result

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("Raw Response:", structured_analysis)
        return None
    except Exception as e:
        print(f"Error analyzing text: {e}")
        return None


def generalize_key_topics_with_openai(topics_list):
    """
    Use OpenAI to group similar topics and generalize them, while maintaining traceability.

    Args:
        topics_list (list of str): A flat list of all topics for a specific sentiment.

    Returns:
        dict: A dictionary mapping generalized topics to their specific topics.
    """
    try:
        # Prepare topics as input for AI
        topics_string = "\n".join(topics_list)
        prompt = f"""
            Group the following topics into specific, distinct categories based on logical themes. Avoid overly broad or generic groupings. 

            Each generalized topic should clearly represent a single theme, such as cleanliness, service, food, or facilities. Do not combine unrelated topics into the same group.

            Your goal is to maximize diversity in categories while keeping logical connections. 
            Provide each generalized topic as a key, and list the specific topics it includes as values.
            Do not include any explanations, only provide a JSON outputR that is FC8259 compliant.

            Topics:
            {topics_string}

            Example output:
            {{
            "Cleanliness": ["room cleanliness"],
            "Staff Performance": ["staff helpfulness", "service speed"],
            "Food Quality": ["food quality", "breakfast variety"],
            "Overall Hotel Quality": ["hotel quality"]
            }}

            Do not include markdown code blocks in your response. Remove the ```json markdown from the output.
        """
        # Send the request to OpenAI
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant for topic analysis."},
                {"role": "user", "content": prompt}
            ],
            model=openai_model,
            temperature=openai_temperature
        )

        # Parse the JSON response
        generalized_topics = json.loads(response.choices[0].message.content.strip())
        return generalized_topics

    except Exception as e:
        print(f"Error generalizing topics with OpenAI: {e}")
        return {}


def batch_process_texts(input_file, output_file, limit=None, chunk_size=1000):
    """
    Batch process multiple texts for analysis and save the results to a JSON file.

    Args:
        input_file (str): Path to the input CSV file with a 'text' column.
        output_file (str): Path to save the analyzed results.
        limit (int, optional): Maximum number of rows to analyze. Defaults to None (no limit).
        chunk_size (int, optional): Number of rows to read per chunk. Defaults to 1000.

    Returns:
        None
    """
    rows_processed = 0  # Counter for the number of rows processed
    results = []  # List to store analysis results

    # Process the file in chunks
    for chunk in pd.read_csv(input_file, chunksize=chunk_size):
        # Ensure 'text' column exists in the chunk
        if 'text' not in chunk.columns:
            print("Error: Input file must contain a 'text' column.")
            return

        # Iterate through rows in the chunk
        for _, row in chunk.iterrows():
            if limit and rows_processed >= limit:
                break  # Stop processing if the limit is reached

            # Analyze the text
            text = row['text']
            analysis = analyze_text_with_openai(text)
            if analysis:
                results.append(analysis)
                rows_processed += 1

        # Break outer loop if limit is reached
        if limit and rows_processed >= limit:
            break

    # Save the analyzed results
    with open(output_file, "w") as json_file:
        json.dump(results, json_file, indent=4)

    print(f"Processed {rows_processed} rows and saved results to {output_file}")


def group_reviews_by_sentiment(input_file):
    """
    Group reviews by sentiment and return grouped reviews.

    Args:
        input_file (str): Path to the JSON file with analysis results.

    Returns:
        dict: Grouped reviews by sentiment (positive, negative, neutral).
    """
    with open(input_file, "r") as file:
        data = json.load(file)

    grouped_reviews = {"positive": [], "negative": [], "neutral": []}

    for entry in data:
        sentiment = entry["sentiment"]["summary"]
        if sentiment in grouped_reviews:
            grouped_reviews[sentiment].append(entry)

    return grouped_reviews


def process_and_save_generalized_topics(input_file, output_file):
    """
    Generalize topics for positive and negative reviews and save the updated dataset.

    Args:
        input_file (str): Path to the JSON file with grouped reviews.
        output_file (str): Path to save the updated JSON file.

    Returns:
        None
    """
    grouped_reviews = group_reviews_by_sentiment(input_file)

    key_topics_by_sentiment = {"positive": [], "negative": []}
    for sentiment, reviews in grouped_reviews.items():
        if sentiment == "neutral":
            continue
        for review in reviews:
            key_topics_by_sentiment[sentiment].extend(review["key_topics"])

    generalized_topics_by_sentiment = {}
    for sentiment, topics in key_topics_by_sentiment.items():
        print(f"Generalizing topics for {sentiment.capitalize()} sentiment...")
        generalized_topics = generalize_key_topics_with_openai(topics)
        generalized_topics_by_sentiment[sentiment] = generalized_topics

    for sentiment, reviews in grouped_reviews.items():
        if sentiment in generalized_topics_by_sentiment:
            generalized_topics = generalized_topics_by_sentiment[sentiment]
            for review in reviews:
                review["generalized_key_topics"] = list({
                    general_topic
                    for general_topic, specific_topics in generalized_topics.items()
                    if any(specific_topic in review["key_topics"] for specific_topic in specific_topics)
                })

    with open(output_file, "w") as file:
        json.dump(grouped_reviews, file, indent=4)

    print(f"Generalized topics and updated dataset saved to {output_file}")


if __name__ == "__main__":
    input_path = "data/processed/hotel_reviews_filtered.csv"
    output_analysis_path = "data/processed/1_analysis.json"
    output_generalized_path = "data/processed/1_generalized.json"

    # Process the first 100 reviews in chunks of 1000 rows each
    batch_process_texts(input_path, output_analysis_path, limit=10, chunk_size=100)
    # Generalize topics and save
    process_and_save_generalized_topics(output_analysis_path, output_generalized_path)