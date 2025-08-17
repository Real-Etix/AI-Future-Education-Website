import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

if __name__ == "__main__":
    # Load the CSV file
    print('Loading CSV file...')
    df = pd.read_csv('backend/database/scenario.csv')
    # Load a pre-trained model for generating embeddings
    print('Loading LLM for encoding...')
    try:
        model = SentenceTransformer('backend/model/sentence_encoder')
        print('Load from local path')
    except Exception as e:
        print(f'Could not load from local path: {e}')
        print('Loading model from HuggingFace...')
        model = SentenceTransformer('DMetaSoul/sbert-chinese-general-v2')
        model.save('backend/model/sentence_encoder')
        print('Saved model locally for future use')
    scenarios = df['兩難'].tolist()  # Convert to list
    # Generate embeddings
    print('Generating embeddings...')
    embeddings = model.encode(scenarios, show_progress_bar=True)
    # Display the shape of the embeddings
    print('Embedding database shape', embeddings.shape)  # Should be (number_of_scenarios, embedding_dimension)
    # Create a new DataFrame with IDs and embeddings
    embeddings_df = pd.DataFrame(embeddings)  # Create a DataFrame from the embeddings
    embeddings_df['id'] = df['id']  # Add the ID column from the original DataFrame
    # Optionally, rename the columns for clarity
    embeddings_df.columns = [f'embedding_{i}' for i in range(embeddings_df.shape[1] - 1)] + ['id']
    # Convert embeddings to a numpy array
    embedding_matrix = np.array(embeddings_df.iloc[:, :-1].values).astype('float32')  # Exclude the ID column
    # Create a FAISS index
    print('Generate vector database...')
    index = faiss.IndexFlatL2(embedding_matrix.shape[1])  # L2 distance
    index.add(embedding_matrix)  # type: ignore
    # Optionally, you can save the index to disk
    faiss.write_index(index, 'backend/database/scenario.index')