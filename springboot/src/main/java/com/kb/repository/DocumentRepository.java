package com.kb.repository;

import com.kb.model.entity.Document;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DocumentRepository extends JpaRepository<Document, Long> {
    Page<Document> findByUserIdOrderByCreatedAtDesc(Long userId, Pageable pageable);
}
