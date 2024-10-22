## Не стал править без тебя
1. **class DAO** has **def get_connection(self)** which is **not used**.
	Location: cocoarag/dao/base.py
	Solution: Delete or rewrite everything else?
2. **class AddChunksToVectorStoreDAO** **doesn't use** arguments **user_id, user_group**. 
	Location: cocoarag/dao/documents.py
	Solution: Delete
3. **class AddFileDAO(DAO)** **not used**
	Location: cocoarag/dao/documents.py
	Solution: Delete
4. We had an idea to create **DAO (collection_id) -> [chunk_id]**.
	Location: cocoarag/dao/documents.py
	Status: not created.
	Question: Do we still need it?
5. Check out **class LoadConversationHistoryDAO** and (**UpdateConversationHistoryDAO** + **SaveConversationHistoryDAO**)
	Location: cocoarag/dao/queries.py
	**Task** for *Sanya*: Choose whether to use **Load..DAO** or both **Update...DAO + Save...DAO**.
6. create_files_table.py
	Location: cocoarag/db/
	Solution: Delete
7. conversation.py
	Location: cocoarag/services/
	Question: Do we need it?

## To-Do:
1. class FilterModel - Do we need to add anything else?
2. Надо как-то сделать универсальный промпт. Написать бы в задании, чтобы проверял есть ли conversation и из нее что-то брал
3. Нужно ли в conversation сохранять retrieve (или промт для llm)


## Проблемы:
1. Почему retriever все таки что-то вытащил? Пользователь голый - без документа и без ембеддингов!
```
(cocoarag) petr0leum@legion:~/Documents/ds_projects/LLMs/markov_rag$ python -m cocoarag.services.rag
======Creating new User========
User test_user_29fa87323b8d4ceebf70bf5020fad6ba saved successfully.
User : 29fa87323b8d4ceebf70bf5020fad6ba created
======Creating document and chunks for retriever========
======Saving conversation into bd========
======Answer with already existing conversation ========
Conversation with ID e71104da488f4de3b87690599a3a6903 not found.
=======QA for User=======
[]
Message example in history: {message}
==============
INSTRUCTION:
You are an assistant that provides accurate and concise answers based on the provided documents as context. If the context doesn’t contain the facts to answer the question answer that you don't know

CONVERSATION HISTORY:


CONTEXT:
{"document": ["King will be okey newx week!", "The king is a little bit sick", "The king is fine", "The king is dead.", "Long live the king!"]}

QUESTION:
==============
What is the name of Petya friend? And population in Paris?
==============
Conversation e71104da488f4de3b87690599a3a6903 saved successfully.
Conversation saved ...
trace_id=UUID('fe4e6e6c-d058-47d8-984b-3b54b3096bae') content="I don't know."
```

2. file_name у документа уникальный должен быть? Была ошибка - не записал

3. Проблема с general в langchain_pg_collection: (**DETAIL:  Key (name)=(general) already exists.**) А че мы дважды не запускали никогда?)
```
(cocoarag) petr0leum@legion:~/Documents/ds_projects/LLMs/markov_rag$ python -m cocoarag.services.rag
======Creating new User========
User test_user_d500aa671e6e4903b98c70f8486b6b70 saved successfully.
User : d500aa671e6e4903b98c70f8486b6b70 created
======Creating document and chunks for retriever========
Document name: Funny story (FROM services.rag) | Document ID: 16b42c6b2bf74280b944faaf2f9ef286
Document_id successfully extracted id: e3dcbf63-0c0a-498c-b7c5-1a731af581d0
AddDocumentService document_id: e3dcbf63-0c0a-498c-b7c5-1a731af581d0
Error inserting document: duplicate key value violates unique constraint "langchain_pg_collection_name_key"
DETAIL:  Key (name)=(general) already exists.
Documents for User d500aa671e6e4903b98c70f8486b6b70 saved
======Saving conversation into bd========
Conversation b8a660e9555c4bf593babc082f4d7e0a saved successfully.
Conversation b8a660e9555c4bf593babc082f4d7e0a for User d500aa671e6e4903b98c70f8486b6b70 uploaded
======Answer with already existing conversation ========
=======[QueryRAGSystemService]=======
===QA from DataBase for User [{'role': 'user', 'content': 'What is the capital of France?'}, {'role': 'assistant', 'content': 'The capital of France is Paris.'}, {'role': 'user', 'content': 'What is the population of Paris?'}, {'role': 'assistant', 'content': 'The population of Paris is              around 2.1 million.'}]
===QA type <class 'list'>
trace_id=UUID('d59f76a4-64bf-4231-88c4-a5789a298904') content="I didn't find any relevant documents"
```