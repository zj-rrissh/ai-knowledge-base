package com.kb.controller;

import com.kb.model.entity.ChatMessage;
import com.kb.model.entity.ChatSession;
import com.kb.service.ChatService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/chat")
public class ChatController {
    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping("/sessions")
    public ResponseEntity<ChatSession> createSession(@RequestBody Map<String, String> body,
                                                      Authentication auth) {
        Long userId = Long.parseLong(auth.getPrincipal().toString());
        return ResponseEntity.ok(chatService.createSession(userId, body.get("title")));
    }

    @GetMapping("/sessions")
    public ResponseEntity<List<ChatSession>> listSessions(Authentication auth) {
        Long userId = Long.parseLong(auth.getPrincipal().toString());
        return ResponseEntity.ok(chatService.listSessions(userId));
    }

    @DeleteMapping("/sessions/{id}")
    public ResponseEntity<Map<String, String>> deleteSession(@PathVariable Long id) {
        chatService.deleteSession(id);
        return ResponseEntity.ok(Map.of("message", "删除成功"));
    }

    @PostMapping("/sessions/{id}/messages")
    public ResponseEntity<ChatMessage> sendMessage(@PathVariable Long id,
                                                    @RequestBody Map<String, String> body,
                                                    Authentication auth) {
        Long userId = Long.parseLong(auth.getPrincipal().toString());
        return ResponseEntity.ok(chatService.sendMessage(id, body.get("query"), userId));
    }

    @GetMapping("/sessions/{id}/messages")
    public ResponseEntity<List<ChatMessage>> listMessages(@PathVariable Long id) {
        return ResponseEntity.ok(chatService.listMessages(id));
    }
}
