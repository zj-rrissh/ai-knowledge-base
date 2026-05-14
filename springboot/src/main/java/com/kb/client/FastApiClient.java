package com.kb.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
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
    public Map<String, Object> ingest(String filePath, Long documentId, Long userId,
                                      String title) {
        Map<String, Object> body = new HashMap<>();
        body.put("file_path", filePath);
        body.put("document_id", documentId);
        body.put("user_id", userId);
        body.put("metadata", Map.of("title", title != null ? title : ""));
        return restTemplate.postForObject(baseUrl + "/ingest", body, Map.class);
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> chat(String sessionId, String query, Long userId, int topK,
                                     List<Map<String, String>> history, String summary) {
        Map<String, Object> body = new HashMap<>();
        body.put("session_id", sessionId);
        body.put("query", query);
        body.put("user_id", userId);
        body.put("top_k", topK);
        body.put("history", history != null ? history : List.of());
        if (summary != null) {
            body.put("summary", summary);
        }
        return restTemplate.postForObject(baseUrl + "/chat", body, Map.class);
    }

    @SuppressWarnings("unchecked")
    public String summarize(String sessionId, List<Map<String, String>> history) {
        Map<String, Object> body = new HashMap<>();
        body.put("session_id", sessionId);
        body.put("history", history != null ? history : List.of());
        Map<String, Object> response = restTemplate.postForObject(
                baseUrl + "/chat/summarize", body, Map.class);
        return (String) response.get("summary");
    }

    public void deleteChunks(Long documentId, Long userId) {
        String url = baseUrl + "/ingest/" + documentId + "?user_id=" + userId;
        restTemplate.delete(url);
    }
}
