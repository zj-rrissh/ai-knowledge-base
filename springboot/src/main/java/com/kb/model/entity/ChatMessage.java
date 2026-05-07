package com.kb.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "chat_messages")
@Data
public class ChatMessage {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_id", nullable = false)
    private Long sessionId;

    @Column(length = 20, nullable = false)
    @Enumerated(EnumType.STRING)
    private MessageRole role;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(name = "source_docs", columnDefinition = "JSON")
    private String sourceDocs;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    public enum MessageRole {
        user, assistant, system
    }
}
