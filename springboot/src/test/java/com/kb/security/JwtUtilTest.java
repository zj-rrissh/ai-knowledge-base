package com.kb.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

import static org.junit.jupiter.api.Assertions.*;

class JwtUtilTest {

    private static final String SECRET = "test-secret-key-for-jwt-util-unit-test-1234567890";
    private static final long ACCESS_EXPIRATION = 7200000L;
    private static final long REFRESH_EXPIRATION = 604800000L;

    private JwtUtil jwtUtil;

    @BeforeEach
    void setUp() {
        jwtUtil = new JwtUtil(SECRET, ACCESS_EXPIRATION, REFRESH_EXPIRATION);
    }

    @Test
    void generateAccessToken_ShouldReturnValidJwt() {
        String token = jwtUtil.generateAccessToken(1L, "testuser", "USER");

        assertNotNull(token);
        String[] parts = token.split("\\.");
        assertEquals(3, parts.length, "JWT should have 3 parts separated by dots");
    }

    @Test
    void parseToken_ShouldExtractCorrectClaims() {
        String token = jwtUtil.generateAccessToken(1L, "testuser", "USER");

        Claims claims = jwtUtil.parseToken(token);

        assertEquals("1", claims.getSubject());
        assertEquals("testuser", claims.get("username"));
        assertEquals("USER", claims.get("role"));
        assertNotNull(claims.getIssuedAt());
        assertNotNull(claims.getExpiration());
    }

    @Test
    void validateToken_ShouldReturnTrue_ForValidToken() {
        String token = jwtUtil.generateAccessToken(1L, "testuser", "USER");

        assertTrue(jwtUtil.validateToken(token));
    }

    @Test
    void validateToken_ShouldReturnFalse_ForInvalidToken() {
        assertFalse(jwtUtil.validateToken("invalid-token-string"));
    }

    @Test
    void validateToken_ShouldReturnFalse_ForExpiredToken() {
        SecretKey key = Keys.hmacShaKeyFor(SECRET.getBytes(StandardCharsets.UTF_8));
        String expiredToken = Jwts.builder()
                .subject("1")
                .issuedAt(new Date(System.currentTimeMillis() - 7200000))
                .expiration(new Date(System.currentTimeMillis() - 3600000))
                .signWith(key)
                .compact();

        assertFalse(jwtUtil.validateToken(expiredToken));
    }

    @Test
    void generateRefreshToken_ShouldReturnValidJwt() {
        String token = jwtUtil.generateRefreshToken(1L);

        assertNotNull(token);
        assertEquals(3, token.split("\\.").length);
    }

    @Test
    void parseToken_ShouldExtractSubject_FromRefreshToken() {
        String token = jwtUtil.generateRefreshToken(1L);
        Claims claims = jwtUtil.parseToken(token);

        assertEquals("1", claims.getSubject());
    }

    @Test
    void validateToken_ShouldReturnFalse_ForMalformedToken() {
        assertFalse(jwtUtil.validateToken("abc.def"));
        assertFalse(jwtUtil.validateToken("a.b.c"));
        assertFalse(jwtUtil.validateToken("not-a-jwt-at-all"));
    }
}
