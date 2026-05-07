package com.kb.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Set;
import java.util.UUID;

@Service
public class FileStorageService {
    private final Path baseDir;
    private static final Set<String> ALLOWED_TYPES = Set.of(
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/markdown",
            "text/plain"
    );

    public FileStorageService(@Value("${app.upload.dir}") String uploadDir) throws IOException {
        this.baseDir = Paths.get(uploadDir).toAbsolutePath().normalize();
        Files.createDirectories(this.baseDir);
    }

    public String store(MultipartFile file, Long userId) throws IOException {
        String contentType = file.getContentType();
        if (contentType == null || !ALLOWED_TYPES.contains(contentType)) {
            throw new IllegalArgumentException("不支持的文件类型: " + contentType);
        }

        Path userDir = baseDir.resolve(userId.toString());
        Files.createDirectories(userDir);

        String ext = getExtension(file.getOriginalFilename());
        String storedName = UUID.randomUUID().toString() + ext;
        Path targetPath = userDir.resolve(storedName);
        file.transferTo(targetPath.toFile());

        return targetPath.toString();
    }

    public void delete(String filePath) throws IOException {
        Files.deleteIfExists(Path.of(filePath));
    }

    private String getExtension(String filename) {
        if (filename == null || !filename.contains(".")) return "";
        return filename.substring(filename.lastIndexOf("."));
    }
}
