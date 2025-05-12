// API service for handling backend requests

const API_BASE_URL = 'http://localhost:9001';

export interface QueryResponse {
  sql: string;
  result: any;
  formatted_result: string;
}

export interface QueryRequest {
  question: string;
}

/**
 * Sends a question to the text2sql API and returns the response
 */
export async function queryText2Sql(request: QueryRequest): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/text2sql/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to process query');
  }

  return response.json();
}

/**
 * Gets an explanation of the SQL that would be generated for a question
 */
export async function explainText2Sql(request: QueryRequest): Promise<{ sql: string }> {
  const response = await fetch(`${API_BASE_URL}/text2sql/explain`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to explain query');
  }

  return response.json();
} 