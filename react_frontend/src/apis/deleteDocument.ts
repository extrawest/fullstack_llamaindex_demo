import { API_URL } from './config'; // Assuming API_URL is defined in config

/**
 * Calls the backend API to delete a document by its ID.
 * @param docId The ID of the document to delete.
 * @returns Promise<boolean> True if deletion was successful (status 200), false otherwise.
 */
const deleteDocumentApi = async (docId: string): Promise<boolean> => {
  if (!docId) {
    console.error('Document ID is required for deletion.');
    return false;
  }

  const url = `${API_URL}/deleteDocument?doc_id=${encodeURIComponent(docId)}`;

  try {
    const response = await fetch(url, {
      method: 'DELETE',
      headers: {
        // Add any necessary headers like Authorization if needed
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) { // Status 200-299
      // const result = await response.json(); // Optional: if backend returns data
      // console.log('Deletion successful:', result);
      return true;
    } else {
      // Handle non-OK responses (e.g., 404 Not Found, 500 Internal Server Error)
      const errorData = await response.json().catch(() => ({ error: 'Failed to parse error response' }));
      console.error(`Failed to delete document ${docId}. Status: ${response.status}. Error:`, errorData);
      return false;
    }
  } catch (error) {
    console.error(`Network or other error deleting document ${docId}:`, error);
    return false;
  }
};

export default deleteDocumentApi; 