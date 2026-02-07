import axios, { AxiosInstance, AxiosError } from "axios";

// Normalize the base URL: extract just the origin (protocol + host)
// This ensures we always have a clean base URL to append /api/v1 paths to
function normalizeBaseUrl(url: string): string {
  let normalized = url.trim();

  // Remove trailing slashes
  while (normalized.endsWith('/')) {
    normalized = normalized.slice(0, -1);
  }

  // Try to extract just the origin (protocol + host + port)
  // This handles cases where the URL includes paths like /api/v1 or /api/v1/chat
  try {
    const urlObj = new URL(normalized);
    return urlObj.origin; // Returns just "https://example.com" without any path
  } catch {
    // If URL parsing fails, do manual cleanup
    // Remove common API path suffixes
    const suffixesToRemove = ['/api/v1/chat', '/api/v1', '/api'];
    for (const suffix of suffixesToRemove) {
      if (normalized.endsWith(suffix)) {
        normalized = normalized.slice(0, -suffix.length);
        break;
      }
    }
    return normalized;
  }
}

const API_BASE_URL = normalizeBaseUrl(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

// Log the configured base URL for debugging
if (typeof window !== 'undefined') {
  console.log("[API Client] Base URL configured:", API_BASE_URL);
  console.log("[API Client] Original NEXT_PUBLIC_API_URL:", process.env.NEXT_PUBLIC_API_URL);
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  user_message_id: string;
  assistant_message_id: string;
  processing_time_ms: number;
}

export interface ConversationSummary {
  id: string;
  user_id: string;
  created_at: string;
  last_message_at: string;
}

export interface ConversationListResponse {
  conversations: ConversationSummary[];
  page: number;
  page_size: number;
  total: number;
}

export interface MessageResponse {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ConversationDetail {
  id: string;
  user_id: string;
  created_at: string;
  last_message_at: string;
  messages: MessageResponse[];
}

export interface DeleteConversationResponse {
  success: boolean;
  conversation_id: string;
  message: string;
}

export interface ApiError {
  detail: string;
  status?: number;
}

class ApiClient {
  private client: AxiosInstance;
  private tokenProvider?: () => string | null;
  private onUnauthorized?: () => void;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000, // 30 seconds
    });

    // Request interceptor to add JWT token
    this.client.interceptors.request.use(
      (config) => {
        if (this.tokenProvider) {
          const rawToken = this.tokenProvider();
          if (rawToken) {
            // Trim whitespace and newlines that can cause ISO-8859-1 encoding errors
            const token = rawToken.trim().replace(/[\r\n]/g, '');
            config.headers.Authorization = `Bearer ${token}`;
            console.log("[API Request]", config.method?.toUpperCase(), `${config.baseURL}${config.url}`, "- Token present");
          } else {
            console.warn("[API Request]", config.method?.toUpperCase(), `${config.baseURL}${config.url}`, "- No token!");
          }
        } else {
          console.warn("[API Request]", config.method?.toUpperCase(), `${config.baseURL}${config.url}`, "- No token provider!");
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        // Log full error for debugging
        console.error("API Error:", {
          url: error.config?.url,
          method: error.config?.method,
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          message: error.message,
        });

        if (error.response?.status === 401) {
          // Unauthorized - redirect to login
          if (this.onUnauthorized) {
            this.onUnauthorized();
          }
        }

        // Handle network errors (no response)
        if (!error.response) {
          const apiError: ApiError = {
            detail: `Network error: ${error.message}. Is the backend running on ${API_BASE_URL}?`,
            status: 0,
          };
          return Promise.reject(apiError);
        }

        // Transform error to consistent format
        const apiError: ApiError = {
          detail:
            error.response?.data?.detail ||
            error.response?.data?.message ||
            (typeof error.response?.data === "string" ? error.response.data : null) ||
            error.message ||
            "An unexpected error occurred",
          status: error.response?.status,
        };

        return Promise.reject(apiError);
      }
    );
  }

  /**
   * Set the token provider function (T086)
   */
  setTokenProvider(provider: () => string | null) {
    this.tokenProvider = provider;
  }

  /**
   * Set the unauthorized handler (T087)
   */
  setOnUnauthorized(handler: () => void) {
    this.onUnauthorized = handler;
  }

  /**
   * Send a chat message (T085)
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>(
      "/api/v1/chat",
      request
    );
    return response.data;
  }

  /**
   * Get list of conversations with pagination (T085)
   */
  async getConversations(
    page: number = 1,
    pageSize: number = 20
  ): Promise<ConversationListResponse> {
    const response = await this.client.get<ConversationListResponse>(
      "/api/v1/conversations",
      {
        params: { page, page_size: pageSize },
      }
    );
    return response.data;
  }

  /**
   * Get conversation detail with message history (T085)
   */
  async getConversationDetail(id: string): Promise<ConversationDetail> {
    const response = await this.client.get<ConversationDetail>(
      `/api/v1/conversations/${id}`
    );
    return response.data;
  }

  /**
   * Delete a conversation (T085)
   */
  async deleteConversation(id: string): Promise<DeleteConversationResponse> {
    const response = await this.client.delete<DeleteConversationResponse>(
      `/api/v1/conversations/${id}`
    );
    return response.data;
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get("/health");
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export default ApiClient;
