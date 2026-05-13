package com.kb.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
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
        Map<String, Object> body = new HashMap<>();
        body.put("file_path", filePath);
        body.put("document_id", documentId);
        body.put("user_id", userId);
        return restTemplate.postForObject(baseUrl + "/ingest", body, Map.class);
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> chat(String sessionId, String query, Long userId, int topK) {
        Map<String, Object> body = new HashMap<>();
        body.put("session_id", sessionId);
        body.put("query", query);
        body.put("user_id", userId);
        body.put("top_k", topK);
        return restTemplate.postForObject(baseUrl + "/chat", body, Map.class);
    }

    public void deleteChunks(Long documentId, Long userId) {
        String url = baseUrl + "/ingest/" + documentId + "?user_id=" + userId;
        restTemplate.delete(url);
    }
}
