package com.kb.controller;

import com.kb.model.entity.Document;
import com.kb.service.KnowledgeService;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Map;

@RestController
@RequestMapping("/api/knowledge")
public class KnowledgeController {
    private final KnowledgeService knowledgeService;

    public KnowledgeController(KnowledgeService knowledgeService) {
        this.knowledgeService = knowledgeService;
    }

    @PostMapping("/documents")
    public ResponseEntity<Document> upload(@RequestParam("file") MultipartFile file,
                                           Authentication auth) throws IOException {
        Long userId = Long.parseLong(auth.getPrincipal().toString());
        return ResponseEntity.ok(knowledgeService.upload(file, userId));
    }

    @GetMapping("/documents")
    public ResponseEntity<Page<Document>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            Authentication auth) {
        Long userId = Long.parseLong(auth.getPrincipal().toString());
        return ResponseEntity.ok(knowledgeService.list(userId, page, size));
    }

    @DeleteMapping("/documents/{id}")
    public ResponseEntity<Map<String, String>> delete(@PathVariable Long id,
                                                       Authentication auth) throws IOException {
        Long userId = Long.parseLong(auth.getPrincipal().toString());
        knowledgeService.delete(id, userId);
        return ResponseEntity.ok(Map.of("message", "删除成功"));
    }
}
