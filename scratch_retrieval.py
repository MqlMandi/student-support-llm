import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from backend.services.retriever import retrieve_context

question = "I would like to know The entry qualification for a master's programme by coursework at udsm"
context, sources = retrieve_context(question)
print("=== CONTEXT ===")
print(context)
print("=== SOURCES ===")
print(sources)
