package com.kb.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Component
public class FastApiClient {
    private final RestTemplate restTemplate;
    private final String baseUrl;

    public FastApiClient(@Value("${app.fastapi.base-url}") String baseUrl) {
        this.baseUrl = baseUrl;
        this.restTemplate = new RestTemplate();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> ingest(String filePath, Long documentId, Long userId) {
        var body = Map.of("file_path", filePath, "document_id", documentId, "user_id", userId);
        return restTemplate.postForObject(baseUrl + "/ingest", body, Map.class);
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> chat(String sessionId, String query, Long userId, int topK) {
        var body = Map.of("session_id", sessionId, "query", query, "user_id", userId, "top_k", topK);
        return restTemplate.postForObject(baseUrl + "/chat", body, Map.class);
    }

    public void deleteChunks(Long documentId, Long userId) {
        // Reserve for future chunk-level deletion via FastAPI
    }
}
