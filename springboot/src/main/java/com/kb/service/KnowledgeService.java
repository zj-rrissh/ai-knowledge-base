package com.kb.service;

import com.kb.client.FastApiClient;
import com.kb.model.dto.DocumentResponse;
import com.kb.model.entity.Document;
import com.kb.model.entity.Document.DocStatus;
import com.kb.model.entity.User;
import com.kb.repository.DocumentRepository;
import com.kb.repository.UserRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@Service
public class KnowledgeService {
    private final DocumentRepository docRepo;
    private final UserRepository userRepo;
    private final FileStorageService fileStorage;
    private final FastApiClient fastApiClient;

    public KnowledgeService(DocumentRepository docRepo, UserRepository userRepo,
                            FileStorageService fileStorage, FastApiClient fastApiClient) {
        this.docRepo = docRepo;
        this.userRepo = userRepo;
        this.fileStorage = fileStorage;
        this.fastApiClient = fastApiClient;
    }

    public Document upload(MultipartFile file, String title, String description,
                           String tags, Long userId) throws IOException {
        String filePath = fileStorage.store(file, userId);
        Document doc = new Document();
        doc.setFilename(file.getOriginalFilename());
        doc.setFilePath(filePath);
        doc.setFileSize(file.getSize());
        doc.setFileType(normalizeContentType(file.getContentType(), file.getOriginalFilename()));
        doc.setUserId(userId);
        doc.setTitle(title != null ? title : file.getOriginalFilename());
        doc.setDescription(description);
        doc.setTags(tags);
        doc.setStatus(DocStatus.indexing);
        doc = docRepo.save(doc);

        try {
            Map<String, Object> resp = fastApiClient.ingest(filePath, doc.getId(), userId, doc.getTitle());
            if ("indexed".equals(resp.get("status"))) {
                doc.setStatus(DocStatus.indexed);
                doc.setChunkCount((Integer) resp.get("chunk_count"));
            } else {
                doc.setStatus(DocStatus.failed);
            }
        } catch (Exception e) {
            doc.setStatus(DocStatus.failed);
        }
        return docRepo.save(doc);
    }

    public Page<DocumentResponse> list(Long userId, int page, int size) {
        Page<Document> docs = docRepo.findByUserIdOrderByCreatedAtDesc(userId, PageRequest.of(page, size));
        User user = userRepo.findById(userId).orElse(null);
        String uploaderName = user != null ? user.getUsername() : "未知";
        return docs.map(doc -> new DocumentResponse(doc, uploaderName));
    }

    public void delete(Long id, Long userId) throws IOException {
        Document doc = docRepo.findById(id).orElseThrow();
        if (!doc.getUserId().equals(userId)) {
            throw new RuntimeException("无权删除该文档");
        }
        fileStorage.delete(doc.getFilePath());
        fastApiClient.deleteChunks(id, userId);
        docRepo.delete(doc);
    }

    private String normalizeContentType(String contentType, String filename) {
        if (contentType != null && !"application/octet-stream".equals(contentType)) {
            return contentType;
        }
        if (filename == null) {
            return contentType;
        }
        String lowerName = filename.toLowerCase();
        if (lowerName.endsWith(".pdf")) {
            return "application/pdf";
        }
        if (lowerName.endsWith(".md")) {
            return "text/markdown";
        }
        if (lowerName.endsWith(".txt")) {
            return "text/plain";
        }
        return contentType;
    }
}
