from typing import List, Dict, Any
import os

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document

class LLMClient:
    """Client for interacting with language models."""

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        # Map custom model names to OpenAI models if needed
        model_mapping = {
            "gpt-o4-mini": "gpt-3.5-turbo",  # Fallback to gpt-3.5-turbo for custom models
        }
        
        # Use mapped model name or original if not in mapping
        actual_model = model_mapping.get(model_name, model_name)
        
        # Initialize the model with error handling
        try:
            self.model = ChatOpenAI(model_name=actual_model)
        except Exception as e:
            print(f"Error initializing model {model_name}: {str(e)}")
            print(f"Falling back to gpt-3.5-turbo")
            self.model = ChatOpenAI(model_name="gpt-3.5-turbo")
            
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant that answers questions based on the provided context. "
                      "If you cannot answer the question based on the context, say so. "
                      "Always cite your sources using the document IDs provided."),
            ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer:")
        ])

    def generate_answer(self, question: str, context_docs: List[Document]) -> Dict[str, Any]:
        """Generate an answer based on the question and context documents."""
        try:
            # Format context from documents
            context_text = "\n\n".join([
                f"Document {i+1} (ID: {doc.metadata.get('source', 'unknown')}):\n{doc.page_content}"
                for i, doc in enumerate(context_docs)
            ])
            
            # Create the prompt
            prompt = self.prompt_template.format_messages(
                context=context_text,
                question=question
            )
            
            # Generate response
            response = self.model.invoke(prompt)
            
            # Extract answer and sources
            answer = response.content
            sources = [doc.metadata.get('source', 'unknown') for doc in context_docs]
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            return {
                "answer": f"I encountered an error while generating an answer: {str(e)}",
                "sources": []
            } 