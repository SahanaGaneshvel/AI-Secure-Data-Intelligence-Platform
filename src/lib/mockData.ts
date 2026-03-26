/**
 * Mock Data - Used ONLY for demo UX convenience
 *
 * IMPORTANT: The only active use of this file is mockInputSample
 * as default textarea content in Analysis Studio.
 *
 * All other mock exports have been removed as they were unused dead code.
 */

// ACTIVE USE: Default textarea content for Analysis Studio
// This is NOT a backend fallback - it's just starter content for the textarea
export const mockInputSample = `{
  "user": "admin",
  "email": "jdoe@company.com",
  "token": "ghp_xYz123AbCdEfGhIjKlMnOpQrStUvWxYz",
  "query": "SELECT * FROM users WHERE id = 1 OR 1=1;"
}`;
