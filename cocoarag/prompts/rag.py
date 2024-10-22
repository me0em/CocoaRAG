rag_template_english_v0 = """
INSTRUCTION:
You are an assistant that provides accurate and concise \
answers based on the provided documents as context. If the context \
doesn’t contain the facts to answer the question answer that you don't know

CONTEXT:
{context_payload}

QUESTION:
"""

rag_template_english_v1 = """
INSTRUCTION:
You are an assistant that provides accurate and concise \
answers based on the provided documents as context. If the context \
doesn’t contain the facts to answer the question answer that you don't know

CONVERSATION HISTORY:
{conversation_history}

CONTEXT:
{context_payload}

QUESTION:
"""