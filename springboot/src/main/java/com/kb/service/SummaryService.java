package com.kb.service;

import com.kb.client.FastApiClient;
import com.kb.model.entity.ChatMessage;
import com.kb.model.entity.ChatSession;
import com.kb.repository.ChatMessageRepository;
import com.kb.repository.ChatSessionRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

@Service
public class SummaryService {

    private static final Logger log = LoggerFactory.getLogger(SummaryService.class);

    private final ChatMessageRepository messageRepo;
    private final ChatSessionRepository sessionRepo;
    private final FastApiClient fastApiClient;

    public SummaryService(ChatMessageRepository messageRepo,
                          ChatSessionRepository sessionRepo,
                          FastApiClient fastApiClient) {
        this.messageRepo = messageRepo;
        this.sessionRepo = sessionRepo;
        this.fastApiClient = fastApiClient;
    }

    @Async("summaryTaskExecutor")
    public CompletableFuture<Void> updateSummary(Long sessionId) {
        try {
            List<ChatMessage> messages = messageRepo
                    .findBySessionIdOrderByCreatedAtAsc(sessionId);
            List<Map<String, String>> history = new ArrayList<>();
            for (ChatMessage msg : messages) {
                Map<String, String> h = new HashMap<>();
                h.put("role", msg.getRole().name());
                h.put("content", msg.getContent());
                history.add(h);
            }

            String summary = fastApiClient.summarize(
                    String.valueOf(sessionId), history);

            ChatSession session = sessionRepo.findById(sessionId)
                    .orElseThrow(() -> new RuntimeException(
                            "Session not found: " + sessionId));
            session.setSummary(summary);
            sessionRepo.save(session);

            log.info("Summary updated for session {}", sessionId);
        } catch (Exception e) {
            log.error("Failed to update summary for session {}", sessionId, e);
        }
        return CompletableFuture.completedFuture(null);
    }
}
