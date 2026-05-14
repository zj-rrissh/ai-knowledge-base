package com.kb.service;

import com.kb.client.FastApiClient;
import com.kb.model.dto.DocumentResponse;
import com.kb.model.entity.Document;
import com.kb.model.entity.Document.DocStatus;
import com.kb.model.entity.User;
import com.kb.repository.DocumentRepository;
import com.kb.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.mock.web.MockMultipartFile;

import java.io.IOException;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class KnowledgeServiceTest {

    @Mock
    private DocumentRepository docRepo;
    @Mock
    private UserRepository userRepo;
    @Mock
    private FileStorageService fileStorage;
    @Mock
    private FastApiClient fastApiClient;

    @InjectMocks
    private KnowledgeService knowledgeService;

    @Test
    void upload_ShouldSucceed_WhenFastApiReturnsIndexed() throws IOException {
        MockMultipartFile file = new MockMultipartFile(
                "file", "test.pdf", "application/pdf", "content".getBytes());

        when(fileStorage.store(any(), anyLong())).thenReturn("/tmp/uploads/1/uuid.pdf");
        when(docRepo.save(any(Document.class))).thenAnswer(invocation -> {
            Document doc = invocation.getArgument(0);
            if (doc.getId() == null) {
                doc.setId(1L);
            }
            return doc;
        });

        Map<String, Object> ingestResp = new HashMap<>();
        ingestResp.put("status", "indexed");
        ingestResp.put("chunk_count", 5);
        when(fastApiClient.ingest(anyString(), anyLong(), anyLong(), anyString())).thenReturn(ingestResp);

        Document result = knowledgeService.upload(file, "Test Title", "Test Desc", "tag1,tag2", 1L);

        assertNotNull(result);
        assertEquals("test.pdf", result.getFilename());
        assertEquals("application/pdf", result.getFileType());
        assertEquals(DocStatus.indexed, result.getStatus());
        assertEquals(5, result.getChunkCount());

        verify(fileStorage).store(any(), eq(1L));
        verify(docRepo, times(2)).save(any(Document.class));
        verify(fastApiClient).ingest(anyString(), eq(1L), eq(1L), anyString());
    }

    @Test
    void upload_ShouldSetFailed_WhenFastApiReturnsFailed() throws IOException {
        MockMultipartFile file = new MockMultipartFile(
                "file", "test.pdf", "application/pdf", "content".getBytes());

        when(fileStorage.store(any(), anyLong())).thenReturn("/tmp/uploads/1/uuid.pdf");
        when(docRepo.save(any(Document.class))).thenAnswer(invocation -> {
            Document doc = invocation.getArgument(0);
            if (doc.getId() == null) {
                doc.setId(1L);
            }
            return doc;
        });

        Map<String, Object> ingestResp = new HashMap<>();
        ingestResp.put("status", "failed");
        when(fastApiClient.ingest(anyString(), anyLong(), anyLong(), anyString())).thenReturn(ingestResp);

        Document result = knowledgeService.upload(file, "Title", null, null, 1L);

        assertEquals(DocStatus.failed, result.getStatus());
    }

    @Test
    void upload_ShouldSetFailed_WhenFastApiThrowsException() throws IOException {
        MockMultipartFile file = new MockMultipartFile(
                "file", "test.pdf", "application/pdf", "content".getBytes());

        when(fileStorage.store(any(), anyLong())).thenReturn("/tmp/uploads/1/uuid.pdf");
        when(docRepo.save(any(Document.class))).thenAnswer(invocation -> {
            Document doc = invocation.getArgument(0);
            if (doc.getId() == null) {
                doc.setId(1L);
            }
            return doc;
        });

        when(fastApiClient.ingest(anyString(), anyLong(), anyLong(), anyString()))
                .thenThrow(new RuntimeException("API unavailable"));

        Document result = knowledgeService.upload(file, "Title", null, null, 1L);

        assertEquals(DocStatus.failed, result.getStatus());
    }

    @Test
    void list_ShouldReturnPagedResultsWithUploaderName() {
        Document doc = new Document();
        doc.setId(1L);
        doc.setFilename("test.pdf");
        doc.setUserId(1L);
        Page<Document> page = new PageImpl<>(List.of(doc));
        when(docRepo.findByUserIdOrderByCreatedAtDesc(eq(1L), any(PageRequest.class))).thenReturn(page);

        User user = new User();
        user.setUsername("testuser");
        when(userRepo.findById(1L)).thenReturn(Optional.of(user));

        Page<DocumentResponse> result = knowledgeService.list(1L, 0, 20);

        assertEquals(1, result.getContent().size());
        assertEquals("testuser", result.getContent().get(0).getUploaderName());
        assertEquals("test.pdf", result.getContent().get(0).getFilename());

        verify(docRepo).findByUserIdOrderByCreatedAtDesc(eq(1L), any(PageRequest.class));
        verify(userRepo).findById(1L);
    }

    @Test
    void list_ShouldUseUnknown_WhenUserNotFound() {
        Document doc = new Document();
        doc.setId(1L);
        doc.setUserId(1L);
        Page<Document> page = new PageImpl<>(List.of(doc));
        when(docRepo.findByUserIdOrderByCreatedAtDesc(eq(1L), any(PageRequest.class))).thenReturn(page);
        when(userRepo.findById(1L)).thenReturn(Optional.empty());

        Page<DocumentResponse> result = knowledgeService.list(1L, 0, 20);

        assertEquals("未知", result.getContent().get(0).getUploaderName());
    }

    @Test
    void delete_ShouldSucceed_WhenOwnershipVerified() throws IOException {
        Document doc = new Document();
        doc.setId(1L);
        doc.setUserId(1L);
        doc.setFilePath("/tmp/test.pdf");
        when(docRepo.findById(1L)).thenReturn(Optional.of(doc));

        knowledgeService.delete(1L, 1L);

        verify(fileStorage).delete("/tmp/test.pdf");
        verify(docRepo).delete(doc);
    }

    @Test
    void delete_ShouldThrow_WhenUserIsNotOwner() throws Exception {
        Document doc = new Document();
        doc.setId(1L);
        doc.setUserId(2L);
        when(docRepo.findById(1L)).thenReturn(Optional.of(doc));

        RuntimeException ex = assertThrows(RuntimeException.class,
                () -> knowledgeService.delete(1L, 1L));
        assertEquals("无权删除该文档", ex.getMessage());

        verify(fileStorage, never()).delete(anyString());
        verify(docRepo, never()).delete(any());
    }

    @SuppressWarnings("unchecked")
    @Test
    void normalizeContentType_ShouldMapCorrectly() throws Exception {
        Method method = KnowledgeService.class.getDeclaredMethod(
                "normalizeContentType", String.class, String.class);
        method.setAccessible(true);

        // Known content type should be returned as-is
        String result = (String) method.invoke(knowledgeService, "application/pdf", "test.pdf");
        assertEquals("application/pdf", result);

        // application/octet-stream with .md extension -> text/markdown
        result = (String) method.invoke(knowledgeService, "application/octet-stream", "test.md");
        assertEquals("text/markdown", result);

        // null content type with .txt extension -> text/plain
        result = (String) method.invoke(knowledgeService, null, "test.txt");
        assertEquals("text/plain", result);

        // null content type with null filename -> null
        result = (String) method.invoke(knowledgeService, null, null);
        assertNull(result);

        // application/octet-stream with unknown extension -> keep octet-stream
        result = (String) method.invoke(knowledgeService, "application/octet-stream", "test.xyz");
        assertEquals("application/octet-stream", result);
    }
}
