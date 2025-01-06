import pandas as pd
import ast


def extract_overall_rating(rating_str):
    """
    Extract the 'overall' rating from the JSON-like string in the 'ratings' column.
    """
    try:
        # Convert string to dictionary
        rating_dict = ast.literal_eval(rating_str)
        # Extract the 'overall' value
        return rating_dict.get('overall', None)
    except (ValueError, SyntaxError):
        return None  # Handle parsing errors gracefully


def transform_csv(input_file, output_file, chunk_size=100000, helpful_votes_threshold=5):
    """
    Transforms a large CSV file by applying filtering criteria and saving 
    the result.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to save the transformed CSV file.
        chunk_size (int): Number of rows to process in each chunk.
        helpful_votes_threshold (int): Minimum number of helpful votes 
        for inclusion.

    Returns:
        None
    """
    write_header = True  # Write header only for the first chunk

    # Process the CSV file in chunks
    for chunk in pd.read_csv(input_file, chunksize=chunk_size):
        # Extract the 'overall' rating
        chunk['overall'] = chunk['ratings'].apply(
            lambda x: extract_overall_rating(x) if isinstance(x, str) else None)

        # Filter rows based on 'overall' rating
        filtered_chunk = chunk[(chunk['overall'] == 2) | (chunk['overall'] == 3)]

        # Filter rows with non-empty 'text'
        filtered_chunk = filtered_chunk.dropna(subset=['text'])
        filtered_chunk = filtered_chunk[filtered_chunk['text'].str.strip() != ""]

        # Filter rows with valid 'date_stayed'
        filtered_chunk = filtered_chunk.dropna(subset=['date_stayed'])

        # Convert 'date_stayed' to datetime format (Month Year)
        filtered_chunk['date_stayed'] = pd.to_datetime(
            filtered_chunk['date_stayed'], format='%B %Y', errors='coerce'
        )
        filtered_chunk = filtered_chunk.dropna(subset=['date_stayed'])

        # Filter rows with 'num_helpful_votes' greater than the threshold
        filtered_chunk = filtered_chunk[filtered_chunk['num_helpful_votes'] >= helpful_votes_threshold]

        # Append the filtered chunk to the output CSV
        filtered_chunk.to_csv(output_file, mode='a', header=write_header, index=False)

        # After the first chunk, set header to False
        write_header = False

    print(f"Filtered data saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    input_path = "../data/raw/reviews.csv"
    output_path = "../data/processed/hotel_reviews_filtered.csv"
    transform_csv(input_path, output_path)