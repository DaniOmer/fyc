from langchain_community.document_loaders import TextLoader

def load_problem_description(file_path: str) -> str:
    """
    Charge l'énoncé du problème depuis un fichier texte

    Args:
        file_path: Chemin vers le fichier contenant l'énoncé

    Returns:
        Contenu du fichier sous forme de texte
    """
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()

    return documents[0].page_content

if __name__ == "__main__":
    # Test du chargement
    description = load_problem_description("problem_description.txt")
    print("Énoncé chargé avec succès:")
    print(description)