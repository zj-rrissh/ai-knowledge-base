package com.kb.controller;

import com.kb.model.dto.DocumentResponse;
import com.kb.model.entity.Document;
import com.kb.service.KnowledgeService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;

import java.io.IOException;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class KnowledgeControllerTest {

    @Mock
    private KnowledgeService knowledgeService;

    @InjectMocks
    private KnowledgeController knowledgeController;

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
    void listDocuments_ShouldReturnPagedResult() {
        Document doc = new Document();
        doc.setId(1L);
        doc.setFilename("test.pdf");
        doc.setStatus(Document.DocStatus.indexed);
        Page<DocumentResponse> page = new PageImpl<>(List.of(
                new DocumentResponse(doc, "testuser")));
        when(knowledgeService.list(anyLong(), anyInt(), anyInt())).thenReturn(page);

        ResponseEntity<Page<DocumentResponse>> result = knowledgeController.list(0, 20,
                SecurityContextHolder.getContext().getAuthentication());

        assertEquals(200, result.getStatusCode().value());
        assertEquals(1, result.getBody().getContent().size());
        assertEquals("test.pdf", result.getBody().getContent().get(0).getFilename());
        assertEquals("testuser", result.getBody().getContent().get(0).getUploaderName());
    }

    @Test
    void listDocuments_ShouldUseDefaultPagination() {
        Document doc = new Document();
        doc.setId(1L);
        doc.setFilename("default.pdf");
        Page<DocumentResponse> page = new PageImpl<>(List.of(
                new DocumentResponse(doc, "testuser")));
        when(knowledgeService.list(anyLong(), eq(0), eq(20))).thenReturn(page);

        ResponseEntity<Page<DocumentResponse>> result = knowledgeController.list(0, 20,
                SecurityContextHolder.getContext().getAuthentication());

        assertEquals(200, result.getStatusCode().value());
        assertEquals(1, result.getBody().getContent().size());
    }

    @Test
    void deleteDocument_ShouldReturn200() throws IOException {
        ResponseEntity<java.util.Map<String, String>> result = knowledgeController.delete(1L,
                SecurityContextHolder.getContext().getAuthentication());

        assertEquals(200, result.getStatusCode().value());
        assertEquals("删除成功", result.getBody().get("message"));
    }

    @Test
    void uploadDocument_ShouldReturn200() throws IOException {
        Document doc = new Document();
        doc.setId(1L);
        doc.setFilename("uploaded.pdf");
        doc.setFileType("application/pdf");
        doc.setStatus(Document.DocStatus.indexing);
        when(knowledgeService.upload(any(), any(), any(), any(), anyLong())).thenReturn(doc);

        MockMultipartFile file = new MockMultipartFile(
                "file", "uploaded.pdf", "application/pdf", "content".getBytes());

        ResponseEntity<Document> result = knowledgeController.upload(
                file, "My Doc", "A test document", "test,doc",
                SecurityContextHolder.getContext().getAuthentication());

        assertEquals(200, result.getStatusCode().value());
        assertEquals(1L, result.getBody().getId());
        assertEquals("uploaded.pdf", result.getBody().getFilename());
        assertEquals("application/pdf", result.getBody().getFileType());
    }

    @Test
    void uploadDocument_ShouldWorkWithoutOptionalParams() throws IOException {
        Document doc = new Document();
        doc.setId(2L);
        doc.setFilename("minimal.pdf");
        doc.setFileType("application/pdf");
        when(knowledgeService.upload(any(), isNull(), isNull(), isNull(), anyLong())).thenReturn(doc);

        MockMultipartFile file = new MockMultipartFile(
                "file", "minimal.pdf", "application/pdf", "content".getBytes());

        ResponseEntity<Document> result = knowledgeController.upload(
                file, null, null, null,
                SecurityContextHolder.getContext().getAuthentication());

        assertEquals(200, result.getStatusCode().value());
        assertEquals("minimal.pdf", result.getBody().getFilename());
    }
}
