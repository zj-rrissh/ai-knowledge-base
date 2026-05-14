package com.kb.service;

import com.kb.client.FastApiClient;
import com.kb.model.entity.ChatMessage;
import com.kb.model.entity.ChatMessage.MessageRole;
import com.kb.model.entity.ChatSession;
import com.kb.repository.ChatMessageRepository;
import com.kb.repository.ChatSessionRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ChatServiceTest {

    @Mock
    private ChatSessionRepository sessionRepo;
    @Mock
    private ChatMessageRepository messageRepo;
    @Mock
    private FastApiClient fastApiClient;

    @InjectMocks
    private ChatService chatService;

    @Test
    void createSession_ShouldSetDefaultTitle_WhenTitleIsNull() {
        when(sessionRepo.save(any(ChatSession.class))).thenAnswer(invocation -> {
            ChatSession session = invocation.getArgument(0);
            session.setId(1L);
            return session;
        });

        ChatSession result = chatService.createSession(1L, null);

        assertEquals("新对话", result.getTitle());
        assertEquals(1L, result.getUserId());
        verify(sessionRepo).save(any(ChatSession.class));
    }

    @Test
    void createSession_ShouldUseGivenTitle() {
        when(sessionRepo.save(any(ChatSession.class))).thenAnswer(invocation -> {
            ChatSession session = invocation.getArgument(0);
            session.setId(2L);
            return session;
        });

        ChatSession result = chatService.createSession(1L, "My Session");

        assertEquals("My Session", result.getTitle());
        verify(sessionRepo).save(any(ChatSession.class));
    }

    @Test
    void listSessions_ShouldReturnSessionsOrderedByUpdatedAtDesc() {
        ChatSession s1 = new ChatSession();
        s1.setId(1L);
        ChatSession s2 = new ChatSession();
        s2.setId(2L);
        when(sessionRepo.findByUserIdOrderByUpdatedAtDesc(1L)).thenReturn(List.of(s1, s2));

        List<ChatSession> result = chatService.listSessions(1L);

        assertEquals(2, result.size());
        assertEquals(1L, result.get(0).getId());
        verify(sessionRepo).findByUserIdOrderByUpdatedAtDesc(1L);
    }

    @Test
    void deleteSession_ShouldDeleteById() {
        chatService.deleteSession(1L);

        verify(sessionRepo).deleteById(1L);
    }

    @Test
    void sendMessage_ShouldSaveUserMessageCallFastApiAndSaveAssistantMessage() {
        when(messageRepo.save(any(ChatMessage.class))).thenAnswer(invocation -> {
            ChatMessage msg = invocation.getArgument(0);
            if (msg.getRole() == MessageRole.user) {
                msg.setId(1L);
            } else if (msg.getRole() == MessageRole.assistant) {
                msg.setId(2L);
            }
            return msg;
        });

        Map<String, Object> aiResp = new HashMap<>();
        aiResp.put("answer", "AI response text");
        aiResp.put("sources", List.of("source1", "source2"));
        when(fastApiClient.chat(anyString(), anyString(), anyLong(), anyInt(), anyList())).thenReturn(aiResp);

        ChatMessage result = chatService.sendMessage(1L, "Hello", 1L);

        ArgumentCaptor<ChatMessage> captor = ArgumentCaptor.forClass(ChatMessage.class);
        verify(messageRepo, times(2)).save(captor.capture());
        List<ChatMessage> savedMessages = captor.getAllValues();

        assertEquals(MessageRole.user, savedMessages.get(0).getRole());
        assertEquals("Hello", savedMessages.get(0).getContent());
        assertEquals(1L, savedMessages.get(0).getSessionId());

        verify(fastApiClient).chat(eq("1"), eq("Hello"), eq(1L), eq(4), anyList());

        assertEquals(MessageRole.assistant, result.getRole());
        assertEquals("AI response text", result.getContent());
        assertNotNull(result.getSourceDocs());
    }

    @Test
    void sendMessage_ShouldHandleNullSources() {
        when(messageRepo.save(any(ChatMessage.class))).thenAnswer(invocation -> invocation.getArgument(0));

        Map<String, Object> aiResp = new HashMap<>();
        aiResp.put("answer", "AI response text");
        aiResp.put("sources", null);
        when(fastApiClient.chat(anyString(), anyString(), anyLong(), anyInt(), anyList())).thenReturn(aiResp);

        ChatMessage result = chatService.sendMessage(1L, "Hello", 1L);

        assertEquals("AI response text", result.getContent());
    }

    @Test
    void listMessages_ShouldReturnMessagesOrderedByCreatedAtAsc() {
        ChatMessage m1 = new ChatMessage();
        m1.setId(1L);
        ChatMessage m2 = new ChatMessage();
        m2.setId(2L);
        when(messageRepo.findBySessionIdOrderByCreatedAtAsc(1L)).thenReturn(List.of(m1, m2));

        List<ChatMessage> result = chatService.listMessages(1L);

        assertEquals(2, result.size());
        verify(messageRepo).findBySessionIdOrderByCreatedAtAsc(1L);
    }
}
