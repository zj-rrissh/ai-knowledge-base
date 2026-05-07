package com.kb.service;

import com.kb.client.FastApiClient;
import com.kb.model.entity.Document;
import com.kb.model.entity.Document.DocStatus;
import com.kb.repository.DocumentRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@Service
public class KnowledgeService {
    private final DocumentRepository docRepo;
    private final FileStorageService fileStorage;
    private final FastApiClient fastApiClient;

    public KnowledgeService(DocumentRepository docRepo, FileStorageService fileStorage,
                            FastApiClient fastApiClient) {
        this.docRepo = docRepo;
        this.fileStorage = fileStorage;
        this.fastApiClient = fastApiClient;
    }

    public Document upload(MultipartFile file, Long userId) throws IOException {
        String filePath = fileStorage.store(file, userId);
        Document doc = new Document();
        doc.setFilename(file.getOriginalFilename());
        doc.setFilePath(filePath);
        doc.setFileSize(file.getSize());
        doc.setFileType(file.getContentType());
        doc.setUserId(userId);
        doc.setStatus(DocStatus.indexing);
        doc = docRepo.save(doc);

        try {
            Map<String, Object> resp = fastApiClient.ingest(filePath, doc.getId(), userId);
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

    public Page<Document> list(Long userId, int page, int size) {
        return docRepo.findByUserIdOrderByCreatedAtDesc(userId, PageRequest.of(page, size));
    }

    public void delete(Long id, Long userId) throws IOException {
        Document doc = docRepo.findById(id).orElseThrow();
        fileStorage.delete(doc.getFilePath());
        docRepo.delete(doc);
    }
}
