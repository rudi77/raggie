import { useState } from 'react';
import { queryText2Sql, QueryResponse } from '../services/api';

export function Text2SqlQuery() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await queryText2Sql({ question });
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Function to render the result as a table if it's an array of objects
  const renderResultTable = () => {
    if (!response || !response.result) return null;

    // Check if result is an array of objects
    if (Array.isArray(response.result) && response.result.length > 0 && typeof response.result[0] === 'object') {
      const headers = Object.keys(response.result[0]);

      return (
        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-700 text-gray-200">
                {headers.map((header) => (
                  <th key={header} className="px-4 py-2 border border-gray-600">
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {response.result.map((row, rowIndex) => (
                <tr key={rowIndex} className="bg-gray-800 text-gray-300">
                  {headers.map((header) => (
                    <td key={`${rowIndex}-${header}`} className="px-4 py-2 border border-gray-600">
                      {row[header] !== null && row[header] !== undefined ? String(row[header]) : ''}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    // If not an array of objects, just display the formatted result
    return (
      <div className="mt-4 p-4 bg-gray-800 rounded-md text-gray-300">
        <pre className="whitespace-pre-wrap">{response.formatted_result}</pre>
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6 text-white">SQL Query Assistant</h2>
      
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex flex-col space-y-4">
          <div>
            <label htmlFor="question" className="block text-sm font-medium text-gray-300 mb-2">
              Ask your question
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="e.g., Show me the total sales by product category"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Processing...' : 'Submit Query'}
          </button>
        </div>
      </form>

      {error && (
        <div className="p-4 mb-4 bg-red-900 text-red-200 rounded-md">
          <p className="font-medium">Error:</p>
          <p>{error}</p>
        </div>
      )}

      {response && (
        <div className="mt-6">
          <div className="mb-4">
            <h3 className="text-lg font-medium text-white mb-2">Generated SQL:</h3>
            <pre className="p-4 bg-gray-800 rounded-md text-gray-300 overflow-x-auto">
              <code>{response.sql}</code>
            </pre>
          </div>

          <div>
            <h3 className="text-lg font-medium text-white mb-2">Results:</h3>
            {renderResultTable()}
          </div>
        </div>
      )}
    </div>
  );
} 