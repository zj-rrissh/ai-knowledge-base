package com.kb.service;

import com.kb.model.dto.AuthRequest;
import com.kb.model.dto.AuthResponse;
import com.kb.model.entity.User;
import com.kb.repository.UserRepository;
import com.kb.security.JwtUtil;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepo;
    @Mock
    private PasswordEncoder passwordEncoder;
    @Mock
    private JwtUtil jwtUtil;
    @Mock
    private StringRedisTemplate redisTemplate;
    @Mock
    private ValueOperations<String, String> valueOps;

    @InjectMocks
    private AuthService authService;

    @Test
    void register_ShouldSucceed_WhenUsernameNotExists() {
        AuthRequest req = new AuthRequest();
        req.setUsername("newuser");
        req.setPassword("password123");

        when(userRepo.existsByUsername("newuser")).thenReturn(false);
        when(passwordEncoder.encode("password123")).thenReturn("encoded-password");
        when(userRepo.save(any(User.class))).thenAnswer(invocation -> {
            User user = invocation.getArgument(0);
            user.setId(1L);
            return user;
        });
        when(jwtUtil.generateAccessToken(1L, "newuser", "USER")).thenReturn("access-token");
        when(jwtUtil.generateRefreshToken(1L)).thenReturn("refresh-token");
        when(redisTemplate.opsForValue()).thenReturn(valueOps);

        AuthResponse response = authService.register(req);

        assertNotNull(response);
        assertEquals("access-token", response.getAccessToken());
        assertEquals("refresh-token", response.getRefreshToken());
        assertEquals("newuser", response.getUsername());

        verify(userRepo).existsByUsername("newuser");
        verify(passwordEncoder).encode("password123");
        verify(userRepo).save(any(User.class));
        verify(jwtUtil).generateAccessToken(1L, "newuser", "USER");
        verify(jwtUtil).generateRefreshToken(1L);
        verify(valueOps).set("token:1", "access-token", 2, TimeUnit.HOURS);
    }

    @Test
    void register_ShouldThrow_WhenUsernameExists() {
        AuthRequest req = new AuthRequest();
        req.setUsername("existinguser");
        req.setPassword("password123");

        when(userRepo.existsByUsername("existinguser")).thenReturn(true);

        RuntimeException ex = assertThrows(RuntimeException.class, () -> authService.register(req));
        assertEquals("用户名已存在", ex.getMessage());

        verify(userRepo, never()).save(any());
        verify(jwtUtil, never()).generateAccessToken(any(), any(), any());
        verify(jwtUtil, never()).generateRefreshToken(any());
    }

    @Test
    void login_ShouldSucceed() {
        AuthRequest req = new AuthRequest();
        req.setUsername("testuser");
        req.setPassword("password123");

        User user = new User();
        user.setId(1L);
        user.setUsername("testuser");
        user.setPassword("encoded-password");
        user.setRole("USER");

        when(userRepo.findByUsername("testuser")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("password123", "encoded-password")).thenReturn(true);
        when(jwtUtil.generateAccessToken(1L, "testuser", "USER")).thenReturn("access-token");
        when(jwtUtil.generateRefreshToken(1L)).thenReturn("refresh-token");
        when(redisTemplate.opsForValue()).thenReturn(valueOps);

        AuthResponse response = authService.login(req);

        assertNotNull(response);
        assertEquals("access-token", response.getAccessToken());
        assertEquals("refresh-token", response.getRefreshToken());
        assertEquals("testuser", response.getUsername());

        verify(valueOps).set("token:1", "access-token", 2, TimeUnit.HOURS);
    }

    @Test
    void login_ShouldThrow_WhenUserNotFound() {
        AuthRequest req = new AuthRequest();
        req.setUsername("nonexistent");
        req.setPassword("password123");

        when(userRepo.findByUsername("nonexistent")).thenReturn(Optional.empty());

        RuntimeException ex = assertThrows(RuntimeException.class, () -> authService.login(req));
        assertEquals("用户不存在", ex.getMessage());
    }

    @Test
    void login_ShouldThrow_WhenPasswordWrong() {
        AuthRequest req = new AuthRequest();
        req.setUsername("testuser");
        req.setPassword("wrong-password");

        User user = new User();
        user.setId(1L);
        user.setUsername("testuser");
        user.setPassword("encoded-password");

        when(userRepo.findByUsername("testuser")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("wrong-password", "encoded-password")).thenReturn(false);

        RuntimeException ex = assertThrows(RuntimeException.class, () -> authService.login(req));
        assertEquals("密码错误", ex.getMessage());
    }

    @Test
    void register_ShouldStoreTokenInRedis() {
        AuthRequest req = new AuthRequest();
        req.setUsername("newuser");
        req.setPassword("password123");

        when(userRepo.existsByUsername("newuser")).thenReturn(false);
        when(passwordEncoder.encode("password123")).thenReturn("encoded-password");
        when(userRepo.save(any(User.class))).thenAnswer(invocation -> {
            User user = invocation.getArgument(0);
            user.setId(1L);
            return user;
        });
        when(jwtUtil.generateAccessToken(1L, "newuser", "USER")).thenReturn("access-token");
        when(jwtUtil.generateRefreshToken(1L)).thenReturn("refresh-token");
        when(redisTemplate.opsForValue()).thenReturn(valueOps);

        authService.register(req);

        verify(valueOps).set(eq("token:1"), eq("access-token"), eq(2L), eq(TimeUnit.HOURS));
    }

    @Test
    void login_ShouldStoreTokenInRedis() {
        AuthRequest req = new AuthRequest();
        req.setUsername("testuser");
        req.setPassword("password123");

        User user = new User();
        user.setId(1L);
        user.setUsername("testuser");
        user.setPassword("encoded-password");
        user.setRole("USER");

        when(userRepo.findByUsername("testuser")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("password123", "encoded-password")).thenReturn(true);
        when(jwtUtil.generateAccessToken(1L, "testuser", "USER")).thenReturn("access-token");
        when(jwtUtil.generateRefreshToken(1L)).thenReturn("refresh-token");
        when(redisTemplate.opsForValue()).thenReturn(valueOps);

        authService.login(req);

        verify(valueOps).set(eq("token:1"), eq("access-token"), eq(2L), eq(TimeUnit.HOURS));
    }

    @Test
    void login_ShouldGenerateTokens() {
        AuthRequest req = new AuthRequest();
        req.setUsername("testuser");
        req.setPassword("password123");

        User user = new User();
        user.setId(1L);
        user.setUsername("testuser");
        user.setPassword("encoded-password");
        user.setRole("USER");

        when(userRepo.findByUsername("testuser")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("password123", "encoded-password")).thenReturn(true);
        when(jwtUtil.generateAccessToken(1L, "testuser", "USER")).thenReturn("access-token");
        when(jwtUtil.generateRefreshToken(1L)).thenReturn("refresh-token");
        when(redisTemplate.opsForValue()).thenReturn(valueOps);

        authService.login(req);

        verify(jwtUtil).generateAccessToken(1L, "testuser", "USER");
        verify(jwtUtil).generateRefreshToken(1L);
    }
}
