package com.kb.controller;

import com.kb.model.dto.AuthRequest;
import com.kb.model.dto.AuthResponse;
import com.kb.service.AuthService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.ResponseEntity;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AuthControllerTest {

    @Mock
    private AuthService authService;

    @InjectMocks
    private AuthController authController;

    @Test
    void register_ShouldReturnAuthResponse() {
        AuthRequest req = new AuthRequest();
        req.setUsername("testuser");
        req.setPassword("pass123");

        AuthResponse resp = new AuthResponse("access-token", "refresh-token", "testuser");
        when(authService.register(any())).thenReturn(resp);

        ResponseEntity<AuthResponse> result = authController.register(req);

        assertEquals(200, result.getStatusCode().value());
        assertEquals("testuser", result.getBody().getUsername());
        assertEquals("access-token", result.getBody().getAccessToken());
        assertEquals("refresh-token", result.getBody().getRefreshToken());
    }

    @Test
    void login_ShouldReturnAuthResponse() {
        AuthRequest req = new AuthRequest();
        req.setUsername("testuser");
        req.setPassword("pass123");

        AuthResponse resp = new AuthResponse("access-token", "refresh-token", "testuser");
        when(authService.login(any())).thenReturn(resp);

        ResponseEntity<AuthResponse> result = authController.login(req);

        assertEquals(200, result.getStatusCode().value());
        assertEquals("testuser", result.getBody().getUsername());
        assertEquals("access-token", result.getBody().getAccessToken());
    }

    @Test
    void refresh_ShouldReturn200() {
        ResponseEntity<Map<String, String>> result = authController.refresh("Bearer test-token");

        assertEquals(200, result.getStatusCode().value());
        assertEquals("refresh endpoint ready", result.getBody().get("message"));
    }
}
