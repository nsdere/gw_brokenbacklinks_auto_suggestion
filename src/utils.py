import os
import faiss
import pickle
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
import pandas as pd

class Utils:

    def embed_documents(self, documents):
        tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        tokens = tokenizer(documents, padding=True, truncation=True, return_tensors='pt')
        
        with torch.no_grad():
            model_output = model(**tokens)
        
        embeddings = model_output.last_hidden_state.mean(dim=1)
        
        return embeddings.numpy()

    def calculate_save_embeddings(self, document_dir, collection_name):
        file_names = []
        documents = []

        for file_name in os.listdir(document_dir):
            file_path = os.path.join(document_dir, file_name)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                documents.append(file.read())
                file_names.append(file_name)

        embeddings = self.embed_documents(documents)

        d = embeddings.shape[1]
        index = faiss.IndexFlatIP(d)  # Using L2 distance
        #index = faiss.IndexNNDescentFlat(d, 1)
        index.add(embeddings)
        faiss.write_index(index, f"{collection_name}.faiss")

        save_file_name = collection_name + ".pkl"
        with open(save_file_name, "wb") as f:
            pickle.dump(file_names, f)

    def search_for_similar(self, query, website, k, top_pages_path):
        query_embedding = self.embed_documents(query)
        index_name = "data/" + website + ".faiss"
        file_names_path = "data/" + website + ".pkl"
        with open(file_names_path, "rb") as f:
            file_names = pickle.load(f)

        index = faiss.read_index(index_name)
        distances, indices = index.search(query_embedding, k)

        results_files = []
        results_distances = []
        results_indices = []
        for i, idx in enumerate(indices[0]):
            results_files.append(file_names[idx])
            results_distances.append(distances[0][i])
            results_indices.append(idx)

        df = pd.DataFrame({
            'File Name': results_files,
            'Distance': results_distances,
            'Index': results_indices
        })

        df_csv = pd.read_csv(top_pages_path)
        merged_df = pd.merge(df, df_csv,left_on= 'File Name', right_on='file_name_with_extension', how='left')
        merged_df.sort_values(by='Distance', ascending=True, inplace=True)
        merged_df.drop_duplicates(subset=['File Name'], keep='first', inplace=True)
        #merged_df.drop(columns=['Unnamed: 3', 'Unnamed: 4', 'file_name'], inplace=True)
        return merged_df
    

    def json_file_handler(file_path, mode, json_data=None):
        """
        Function to handle JSON files.

        Parameters
        ----------
        file_path : str
            Path to the JSON file.
        mode : str
            Mode to use when handling the JSON file. Use 'read' or 'write'.
        json_data : str
            JSON data to write to the file. Only used when mode is 'write'.

        Returns
        -------
        str
            JSON data from the file. Only used when mode is 'read'.

        Raises
        ------
        ValueError
            If mode is not 'read' or 'write'.
        """
        if mode == "write":
            with open(file_path, "w") as file:
                json.dump(json.loads(json_data), file)
        elif mode == "read":
            with open(file_path, "r") as file:
                return json.dumps(json.load(file))
        else:
            raise ValueError("Invalid mode. Use 'read' or 'write'.")


    def read_write_file(file_path: str, mode: str, string_data: str = None) -> str:
        """
        Function to handle reading and writing files.

        Parameters
        ----------
        file_path : str
            Path to the file.
        mode : str
            Mode to use when handling the file. Use 'r' for read, 'w' for write, or 'a' for append.
        string_data : str
            String data to write to the file. Only used when mode is 'w' or 'a'.

        Returns
        -------
        str
            String data from the file. Only used when mode is 'r'.

        Raises
        ------
        ValueError
            If mode is not 'r', 'w', or 'a'.
        """
        with open(file_path, mode) as file:
            if mode == "w" or mode == "a":
                file.write(string_data)
            elif mode == "r":
                string_data = file.read()
            else:
                raise ValueError(
                    "Invalid mode. Please use 'r' for read, 'w' for write, or 'a' for append."
                )
        return string_data


    def get_firefall_generations(json_object):
        """
        Function to get the generations from a Firefall JSON object.

        Parameters
        ----------
        json_object : dict
            JSON object from a Firefall response.

        Returns
        -------
        list
            List of generations from the Firefall response.
        """
        content_objects = []
        if "generations" in json_object:
            for generation in json_object["generations"]:
                for item in generation:
                    if "message" in item and "content" in item["message"]:
                        content_objects.append(json.loads(item["message"]["content"]))
        return content_objects
