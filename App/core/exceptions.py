class DocumentProcessingError(Exception):
    pass


class EmbeddingError(Exception):
    pass


class RetrievalError(Exception):
    pass


class LLMGenerationError(Exception):
    pass


class UnsupportedFileTypeError(Exception):
    pass