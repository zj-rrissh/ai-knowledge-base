package com.kb.model.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "documents")
@Data
public class Document {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String filename;

    @Column(name = "file_path", nullable = false)
    private String filePath;

    @Column(name = "file_size")
    private Long fileSize;

    @Column(name = "file_type", length = 20)
    private String fileType;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(length = 20, nullable = false)
    @Enumerated(EnumType.STRING)
    private DocStatus status = DocStatus.pending;

    @Column(name = "chunk_count")
    private Integer chunkCount = 0;

    @Column(length = 500)
    private String description;

    @Column(length = 500)
    private String tags;

    @Column(name = "category_id")
    private Long categoryId;

    @Column(name = "permission_level")
    private Integer permissionLevel = 1;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(name = "updated_at")
    private LocalDateTime updatedAt = LocalDateTime.now();

    public enum DocStatus {
        pending, indexing, indexed, failed
    }
}
