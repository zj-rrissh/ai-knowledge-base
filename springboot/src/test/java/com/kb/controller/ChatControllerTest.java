package com.kb.controller;

import com.kb.model.entity.ChatMessage;
import com.kb.model.entity.ChatSession;
import com.kb.service.ChatService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ChatControllerTest {

    @Mock
    private ChatService chatService;

    @InjectMocks
    private ChatController chatController;

    @BeforeEach
    void setUp() {
        SecurityContextHolder.getContext().setAuthentication(
                new UsernamePasswordAuthenticationToken("1", null,
                        List.of(new SimpleGrantedAuthority("ROLE_USER"))));
    }

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void createSession_ShouldReturn200() {
        ChatSession session = new ChatSession();
        session.setId(1L);
        session.setUserId(1L);
        session.setTitle("新对话");
        when(chatService.createSession(anyLong(), any())).thenReturn(session);

        ResponseEntity<ChatSession> result = chatController.createSession(
                Map.of("title", "新对话"), SecurityContextHolder.getContext().getAuthentication());

        assertEquals(200, result.getStatusCode().value());
        assertEquals(1L, result.getBody().getId());
        assertEquals("新对话", result.getBody().getTitle());
    }

    @Test
    void createSession_ShouldUseNullTitle_WhenNotProvided() {
        ChatSession session = new ChatSession();
        session.setId(2L);
        session.setUserId(1L);
        session.setTitle("新对话");
        when(chatService.createSession(anyLong(), isNull())).thenReturn(session);

        ResponseEntity<ChatSession> result = chatController.createSession(
                Map.of(), SecurityContextHolder.getContext().getAuthentication());

        assertEquals(200, result.getStatusCode().value());
        assertEquals("新对话", result.getBody().getTitle());
    }

    @Test
    void listSessions_ShouldReturn200() {
        ChatSession s1 = new ChatSession();
        s1.setId(1L);
        ChatSession s2 = new ChatSession();
        s2.setId(2L);
        when(chatService.listSessions(1L)).thenReturn(List.of(s1, s2));

        ResponseEntity<List<ChatSession>> result = chatController.listSessions(
                SecurityContextHolder.getContext().getAuthentication());

        assertEquals(200, result.getStatusCode().value());
        assertEquals(2, result.getBody().size());
    }

    @Test
    void deleteSession_ShouldReturn200() {
        ResponseEntity<Map<String, String>> result = chatController.deleteSession(1L);

        assertEquals(200, result.getStatusCode().value());
        assertEquals("删除成功", result.getBody().get("message"));
    }

    @Test
    void sendMessage_ShouldReturn200() {
        ChatMessage msg = new ChatMessage();
        msg.setId(1L);
        msg.setSessionId(1L);
        msg.setContent("Response");
        when(chatService.sendMessage(anyLong(), anyString(), anyLong())).thenReturn(msg);

        ResponseEntity<ChatMessage> result = chatController.sendMessage(1L,
                Map.of("query", "Hello"), SecurityContextHolder.getContext().getAuthentication());

        assertEquals(200, result.getStatusCode().value());
        assertEquals("Response", result.getBody().getContent());
    }

    @Test
    void listMessages_ShouldReturn200() {
        ChatMessage m1 = new ChatMessage();
        m1.setId(1L);
        ChatMessage m2 = new ChatMessage();
        m2.setId(2L);
        when(chatService.listMessages(1L)).thenReturn(List.of(m1, m2));

        ResponseEntity<List<ChatMessage>> result = chatController.listMessages(1L);

        assertEquals(200, result.getStatusCode().value());
        assertEquals(2, result.getBody().size());
    }

    @Test
    void deleteSession_ShouldCallService() {
        ResponseEntity<Map<String, String>> result = chatController.deleteSession(999L);

        assertEquals(200, result.getStatusCode().value());
        assertEquals("删除成功", result.getBody().get("message"));
    }
}
