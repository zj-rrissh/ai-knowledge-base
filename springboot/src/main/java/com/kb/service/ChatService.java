package com.kb.service;

import com.kb.client.FastApiClient;
import com.kb.model.entity.ChatMessage;
import com.kb.model.entity.ChatSession;
import com.kb.model.entity.ChatMessage.MessageRole;
import com.kb.repository.ChatMessageRepository;
import com.kb.repository.ChatSessionRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ChatService {
    private final ChatSessionRepository sessionRepo;
    private final ChatMessageRepository messageRepo;
    private final FastApiClient fastApiClient;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public ChatService(ChatSessionRepository sessionRepo, ChatMessageRepository messageRepo,
                       FastApiClient fastApiClient) {
        this.sessionRepo = sessionRepo;
        this.messageRepo = messageRepo;
        this.fastApiClient = fastApiClient;
    }

    public ChatSession createSession(Long userId, String title) {
        ChatSession session = new ChatSession();
        session.setUserId(userId);
        session.setTitle(title != null ? title : "新对话");
        return sessionRepo.save(session);
    }

    public List<ChatSession> listSessions(Long userId) {
        return sessionRepo.findByUserIdOrderByUpdatedAtDesc(userId);
    }

    public void deleteSession(Long sessionId) {
        sessionRepo.deleteById(sessionId);
    }

    @SuppressWarnings("unchecked")
    public ChatMessage sendMessage(Long sessionId, String query, Long userId) {
        List<ChatMessage> historyMessages = messageRepo.findBySessionIdOrderByCreatedAtAsc(sessionId);
        List<Map<String, String>> history = new ArrayList<>();
        for (ChatMessage msg : historyMessages) {
            Map<String, String> h = new HashMap<>();
            h.put("role", msg.getRole().name());
            h.put("content", msg.getContent());
            history.add(h);
        }

        ChatMessage userMsg = new ChatMessage();
        userMsg.setSessionId(sessionId);
        userMsg.setRole(MessageRole.user);
        userMsg.setContent(query);
        messageRepo.save(userMsg);

        Map<String, Object> aiResp = fastApiClient.chat(
                String.valueOf(sessionId), query, userId, 4, history);

        ChatMessage assistantMsg = new ChatMessage();
        assistantMsg.setSessionId(sessionId);
        assistantMsg.setRole(MessageRole.assistant);
        assistantMsg.setContent((String) aiResp.get("answer"));

        try {
            Object sources = aiResp.get("sources");
            assistantMsg.setSourceDocs(objectMapper.writeValueAsString(sources));
        } catch (Exception ignored) {}

        return messageRepo.save(assistantMsg);
    }

    public List<ChatMessage> listMessages(Long sessionId) {
        return messageRepo.findBySessionIdOrderByCreatedAtAsc(sessionId);
    }
}
