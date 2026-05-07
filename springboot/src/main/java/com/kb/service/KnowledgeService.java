package com.kb.service;

import com.kb.model.entity.Document;
import com.kb.model.entity.Document.DocStatus;
import com.kb.repository.DocumentRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@Service
public class KnowledgeService {
    private final DocumentRepository docRepo;
    private final FileStorageService fileStorage;

    public KnowledgeService(DocumentRepository docRepo, FileStorageService fileStorage) {
        this.docRepo = docRepo;
        this.fileStorage = fileStorage;
    }

    public Document upload(MultipartFile file, Long userId) throws IOException {
        String filePath = fileStorage.store(file, userId);
        Document doc = new Document();
        doc.setFilename(file.getOriginalFilename());
        doc.setFilePath(filePath);
        doc.setFileSize(file.getSize());
        doc.setFileType(file.getContentType());
        doc.setUserId(userId);
        doc.setStatus(DocStatus.indexed);
        doc.setChunkCount(0);
        return docRepo.save(doc);
    }

    public Page<Document> list(Long userId, int page, int size) {
        return docRepo.findByUserIdOrderByCreatedAtDesc(userId, PageRequest.of(page, size));
    }

    public void delete(Long id, Long userId) throws IOException {
        Document doc = docRepo.findById(id).orElseThrow();
        fileStorage.delete(doc.getFilePath());
        docRepo.delete(doc);
    }
}
