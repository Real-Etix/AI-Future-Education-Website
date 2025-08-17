import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class RetrievalModel():
    '''
    This class mainly deals with comparing the input text with the text from the vector database with similarity score.
    '''
    def __init__(self, model_name, model_path, df_path, vectorDB_path):
        self.sentence_model_name = model_name
        self.model_path = model_path
        self.df_path = df_path
        self.vectorDB_path = vectorDB_path
        self.model = None
        print('Initialize LLM with init_sentence_llm() method.')

    def init_sentence_llm(self):
        print('Loading LLM for encoding...')
        try:
            self.model = SentenceTransformer(self.model_path)
            print('Load from local path')
        except Exception as e:
            print(f'Could not load from local path: {e}')
            print('Loading model from HuggingFace...')
            self.model = SentenceTransformer(self.sentence_model_name)
            self.model.save(self.model_path)
            print('Saved model locally for future use')
    
    def obtain_most_similar(self, input, k=5):
        '''
        Gets the most similar item with the input
        '''

        if not self.model:
            return '沒有', '沒有'
        df = pd.read_csv(self.df_path)
        index = faiss.read_index(self.vectorDB_path)

        # Obtain the embeddings of the input
        input_embedding = self.model.encode([input], convert_to_tensor=True)
        input_embedding = input_embedding.detach().cpu().numpy().astype('float32')

        # Get the k-most similar sentences
        _, indices = index.search(input_embedding, k)

        # Rerank based on similarity scores
        query_embedding = self.model.encode([input])
        top_k_results = [df['兩難'][idx] for idx in indices[0]]
        top_k_embeddings = self.model.encode(top_k_results) # type: ignore
        similarity_scores = np.dot(top_k_embeddings, query_embedding.T).flatten()
        reranked_indices = np.argsort(similarity_scores)[::-1]

        # Obtain the best result
        idx = indices[0][reranked_indices[0]]
        return df['兩難'][idx], df['主題'][idx]





if __name__ == '__main__':
    model_name = 'DMetaSoul/sbert-chinese-general-v2'
    model_path = 'backend/model/sentence_encoder'
    csv_path = 'backend/database/scenario.csv'
    index_path = 'backend/database/scenario.index'
    system = RetrievalModel(model_name, model_path, csv_path, index_path)
    system.init_sentence_llm()
    input_sentence = "遵守承諾還是去生日派對"
    scenario, themes = system.obtain_most_similar(input_sentence)
    print('Scenario:',scenario)
    print('Themes:', themes)