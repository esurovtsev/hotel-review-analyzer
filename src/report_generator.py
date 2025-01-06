import os
import json
from collections import Counter
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
openai_model = "gpt-4o-mini"
openai_temperature = 0.7


def load_analysis_data(input_file):
    with open(input_file, "r") as json_file:
        data = json.load(json_file)
    return data


def summarize_insights(data):
    report_data = {}
    report_data["review_counts"] = {
        sentiment: len(reviews) for sentiment, reviews in data.items()
    }
    report_data["generalized_topics_by_sentiment"] = {
        sentiment: dict(Counter([topic for review in reviews for topic in review["generalized_key_topics"]]))
        for sentiment, reviews in data.items()
    }
    return report_data


def calculate_percentage_distribution(report_data):
    percentage_distributions = {}
    for sentiment, topics in report_data["generalized_topics_by_sentiment"].items():
        total_mentions = sum(topics.values())
        if total_mentions > 0:
            percentage_distributions[sentiment] = {
                topic: (count / total_mentions) * 100 for topic, count in topics.items()
            }
        else:
            percentage_distributions[sentiment] = {}
    report_data["percentage_distribution_by_sentiment"] = percentage_distributions
    return report_data


def group_reviews_by_top_topics(data, report_data, top_n=3):
    negative_topic_percentages = sorted(
        report_data["percentage_distribution_by_sentiment"]["negative"].items(),
        key=lambda x: x[1],
        reverse=True
    )
    top_worst_topics = [topic for topic, _ in negative_topic_percentages[:top_n]]
    grouped_reviews = {topic: [] for topic in top_worst_topics}
    for review in data.get("negative", []):
        for topic in top_worst_topics:
            if topic in review["generalized_key_topics"]:
                grouped_reviews[topic].append(review)
    return {"top_worst_topics": top_worst_topics, "grouped_reviews_by_topic": grouped_reviews}


def generate_problem_description_and_recommendations(topic, reviews):
    """
    Generate a short description of the problem and recommendations for a given topic using OpenAI.

    Args:
        topic (str): The topic for which the description and recommendations are generated.
        reviews (list of dict): List of reviews related to the topic.

    Returns:
        dict: A dictionary containing the topic, AI-generated description, and recommendations.
    """
    # Create a numbered list of reviews
    numbered_reviews = "\n".join([f"{i + 1}. {review['review']}" for i, review in enumerate(reviews)])
    
    # Construct the AI prompt
    prompt = f"""
        The following is a list of reviews related to the topic: "{topic}".

        Reviews:
        {numbered_reviews}

        Based on these reviews:
        1. Generate a short description of the key problem related to this topic.
        2. Provide a list of actionable recommendations to address the identified problem.
        
        Your response should be in the following format:
        {{
            "problem_description": "Short description of the problem.",
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2",
                ...
            ]
        }}
        
        Please ensure the response is in valid JSON format. Do not include any explanations, only provide a JSON outputR that is FC8259 compliant.
        Do not include markdown code blocks in your response. Remove the ```json markdown from the output.

    """

    try:
        # Send the prompt to OpenAI
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant for analyzing reviews and suggesting improvements."},
                {"role": "user", "content": prompt}
            ],
            model=openai_model,
            temperature=openai_temperature
        )

        # Parse the AI-generated response
        ai_response = json.loads(response.choices[0].message.content.strip())

        # Return the results
        return {
            "topic": topic,
            "problem_description": ai_response.get("problem_description", "No description provided."),
            "recommendations": ai_response.get("recommendations", [])
        }

    except Exception as e:
        print(f"Error generating description and recommendations for topic '{topic}': {e}")
        return {
            "topic": topic,
            "problem_description": "Error generating description.",
            "recommendations": []
        }


def merge_problems_and_recommendations(problems_summary):
    """
    Use OpenAI to merge overlapping problems and recommendations into a general summary.

    Args:
        problems_summary (list of dict): List of problem descriptions and recommendations for each topic.

    Returns:
        dict: A dictionary containing the general problem description and consolidated recommendations.
    """
    # Prepare the input for AI
    problems_input = "\n".join([
        f"""
        Topic: {item['topic']}
        Problem Description: {item['problem_description']}
        Recommendations: {', '.join(item['recommendations'])}
        """
        for item in problems_summary
    ])
    
    # Construct the AI prompt
    prompt = f"""
        The following are problem descriptions and recommendations for various hotel-related issues:

        {problems_input}

        Your task:
        1. Identify overlapping problems and merge them into a single general description of the hotel's issues.
        2. Consolidate the recommendations into a unified list, eliminating redundancies. Keep in the list only significant recommendations. The list should contain 5 recommendations at most.
        3. Provide the output in the following format:
        {{
            "general_problem_description": "A summary of the hotel's main problems.",
            "consolidated_recommendations": [
                "Recommendation 1",
                "Recommendation 2",
                ...
            ]
        }}
        4. Make all generated texts easy to read and understand. Create recommendations in plain and attractive language.

        Please ensure the response is in valid JSON format. Do not include any explanations, only provide a JSON outputR that is FC8259 compliant.
        Do not include markdown code blocks in your response. Remove the ```json markdown from the output.
    """

    try:
        # Send the prompt to OpenAI
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant for consolidating problems and recommendations."},
                {"role": "user", "content": prompt}
            ],
            model=openai_model,
            temperature=openai_temperature
        )

        # Parse the AI-generated response
        consolidated_results = json.loads(response.choices[0].message.content.strip())
        return consolidated_results

    except Exception as e:
        print(f"Error merging problems and recommendations: {e}")
        return {
            "general_problem_description": "Error generating description.",
            "consolidated_recommendations": []
        }


def save_report_data(report_data, output_file):
    with open(output_file, "w") as json_file:
        json.dump(report_data, json_file, indent=4)
    print(f"Report data successfully saved to {output_file}")


def generate_report_data(input_path, output_path):
    """
    Main function to generate report data by processing the input JSON.

    Args:
        input_path (str): Path to the input analysis JSON file.
        output_path (str): Path to save the final report JSON file.

    Returns:
        dict: Final report data dictionary.
    """
    # Step 1: Load data
    data = load_analysis_data(input_path)

    # Step 2: Summarize insights
    report_data = summarize_insights(data)

    # Step 3: Calculate percentage distribution
    report_data = calculate_percentage_distribution(report_data)

    # Step 4: Identify top worst topics and group reviews
    step_4_results = group_reviews_by_top_topics(data, report_data)

    # Step 5: Generate problem descriptions and recommendations
    report_data["problems_summary"] = [
        generate_problem_description_and_recommendations(topic, reviews)
        for topic, reviews in step_4_results["grouped_reviews_by_topic"].items()
    ]

    # Step 6: Merge problems and recommendations
    merged_results = merge_problems_and_recommendations(report_data["problems_summary"])
    report_data["general_problem_description"] = merged_results.get("general_problem_description", "No description provided.")
    report_data["consolidated_recommendations"] = merged_results.get("consolidated_recommendations", [])

    # Step 7: Save report data
    save_report_data(report_data, output_path)

    return report_data


if __name__ == "__main__":
    # File paths
    input_path = "data/processed/generalized.json"
    output_path = "data/processed/report_data.json"

    # Generate report data
    generate_report_data(input_path, output_path)