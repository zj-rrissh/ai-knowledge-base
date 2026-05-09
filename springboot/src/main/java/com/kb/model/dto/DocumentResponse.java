package com.kb.model.dto;

import com.kb.model.entity.Document;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
public class DocumentResponse {
    private final Long id;
    private final String title;
    private final String filename;
    private final String filePath;
    private final Long fileSize;
    private final String fileType;
    private final Long userId;
    private final String uploaderName;
    private final String status;
    private final Integer chunkCount;
    private final String description;
    private final String tags;
    private final Long categoryId;
    private final Integer permissionLevel;
    private final LocalDateTime createdAt;
    private final LocalDateTime updatedAt;

    public DocumentResponse(Document doc, String uploaderName) {
        this.id = doc.getId();
        this.title = doc.getTitle() != null ? doc.getTitle() : doc.getFilename();
        this.filename = doc.getFilename();
        this.filePath = doc.getFilePath();
        this.fileSize = doc.getFileSize();
        this.fileType = doc.getFileType();
        this.userId = doc.getUserId();
        this.uploaderName = uploaderName;
        this.status = doc.getStatus().name();
        this.chunkCount = doc.getChunkCount();
        this.description = doc.getDescription();
        this.tags = doc.getTags();
        this.categoryId = doc.getCategoryId();
        this.permissionLevel = doc.getPermissionLevel();
        this.createdAt = doc.getCreatedAt();
        this.updatedAt = doc.getUpdatedAt();
    }
}
