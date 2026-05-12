package com.kb.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockMultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

class FileStorageServiceTest {

    @TempDir
    Path tempDir;

    private FileStorageService fileStorageService;

    @BeforeEach
    void setUp() throws IOException {
        fileStorageService = new FileStorageService(tempDir.toString());
    }

    @Test
    void store_ShouldSavePdfFileSuccessfully() throws IOException {
        MockMultipartFile file = new MockMultipartFile(
                "file", "test.pdf", "application/pdf", "pdf content".getBytes());

        String storedPath = fileStorageService.store(file, 1L);

        assertNotNull(storedPath);
        assertTrue(storedPath.endsWith(".pdf"));
        assertTrue(Files.exists(Path.of(storedPath)));
        assertEquals("pdf content", Files.readString(Path.of(storedPath)));
    }

    @Test
    void store_ShouldCreateUserDirectoryIfNotExists() throws IOException {
        MockMultipartFile file = new MockMultipartFile(
                "file", "doc.pdf", "application/pdf", "content".getBytes());

        Path userDir = tempDir.resolve("99");
        assertFalse(Files.exists(userDir));

        String storedPath = fileStorageService.store(file, 99L);

        assertTrue(Files.exists(userDir));
        assertTrue(Files.exists(Path.of(storedPath)));
    }

    @Test
    void store_ShouldRejectUnsupportedFileType() {
        MockMultipartFile file = new MockMultipartFile(
                "file", "image.png", "image/png", "png content".getBytes());

        IllegalArgumentException ex = assertThrows(IllegalArgumentException.class,
                () -> fileStorageService.store(file, 1L));
        assertTrue(ex.getMessage().contains("不支持的文件类型"));
    }

    @Test
    void store_ShouldAcceptMdFile_WithNullContentType() throws IOException {
        MockMultipartFile file = new MockMultipartFile(
                "file", "readme.md", null, "# Markdown content".getBytes());

        String storedPath = fileStorageService.store(file, 1L);

        assertNotNull(storedPath);
        assertTrue(storedPath.endsWith(".md"));
        assertTrue(Files.exists(Path.of(storedPath)));
    }

    @Test
    void store_ShouldAcceptTxtFile_WithOctetStreamContentType() throws IOException {
        MockMultipartFile file = new MockMultipartFile(
                "file", "notes.txt", "application/octet-stream", "text content".getBytes());

        String storedPath = fileStorageService.store(file, 1L);

        assertNotNull(storedPath);
        assertTrue(storedPath.endsWith(".txt"));
        assertTrue(Files.exists(Path.of(storedPath)));
    }

    @Test
    void store_ShouldRejectOctetStreamWithoutKnownExtension() {
        MockMultipartFile file = new MockMultipartFile(
                "file", "unknown.bin", "application/octet-stream", "binary".getBytes());

        assertThrows(IllegalArgumentException.class,
                () -> fileStorageService.store(file, 1L));
    }

    @Test
    void delete_ShouldRemoveExistingFile() throws IOException {
        MockMultipartFile file = new MockMultipartFile(
                "file", "delete-me.pdf", "application/pdf", "to delete".getBytes());
        String storedPath = fileStorageService.store(file, 1L);
        assertTrue(Files.exists(Path.of(storedPath)));

        fileStorageService.delete(storedPath);

        assertFalse(Files.exists(Path.of(storedPath)));
    }

    @Test
    void delete_ShouldNotThrow_WhenFileNotExists() {
        assertDoesNotThrow(() -> fileStorageService.delete("/nonexistent/path/file.pdf"));
    }
}
