package com.kb.security;

import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class JwtAuthFilterTest {

    @Mock
    private JwtUtil jwtUtil;
    @Mock
    private StringRedisTemplate redisTemplate;
    @Mock
    private HttpServletRequest request;
    @Mock
    private HttpServletResponse response;
    @Mock
    private FilterChain chain;
    @Mock
    private Claims claims;

    @InjectMocks
    private JwtAuthFilter filter;

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void doFilter_ShouldSetAuthentication_WithValidBearerToken() throws Exception {
        when(request.getHeader("Authorization")).thenReturn("Bearer valid-token");
        when(jwtUtil.validateToken("valid-token")).thenReturn(true);
        when(jwtUtil.parseToken("valid-token")).thenReturn(claims);
        when(claims.getSubject()).thenReturn("1");
        when(claims.get("role", String.class)).thenReturn("USER");
        when(redisTemplate.hasKey("token:1")).thenReturn(true);

        filter.doFilterInternal(request, response, chain);

        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        assertNotNull(auth);
        assertEquals("1", auth.getPrincipal());
        assertEquals(1, auth.getAuthorities().size());
        assertEquals("ROLE_USER", auth.getAuthorities().iterator().next().getAuthority());

        verify(redisTemplate).expire("token:1", 2, TimeUnit.HOURS);
        verify(chain).doFilter(request, response);
    }

    @Test
    void doFilter_ShouldSetDevAuth_WhenNoAuthorizationHeader() throws Exception {
        when(request.getHeader("Authorization")).thenReturn(null);

        filter.doFilterInternal(request, response, chain);

        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        assertNotNull(auth);
        assertEquals("1", auth.getPrincipal());

        verify(chain).doFilter(request, response);
    }

    @Test
    void doFilter_ShouldSetDevAuth_WhenTokenIsInvalid() throws Exception {
        when(request.getHeader("Authorization")).thenReturn("Bearer invalid-token");
        when(jwtUtil.validateToken("invalid-token")).thenReturn(false);

        filter.doFilterInternal(request, response, chain);

        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        assertNotNull(auth);
        assertEquals("1", auth.getPrincipal());

        verify(chain).doFilter(request, response);
    }

    @Test
    void doFilter_ShouldSetDevAuth_WhenRedisHasNoRecord() throws Exception {
        when(request.getHeader("Authorization")).thenReturn("Bearer valid-token");
        when(jwtUtil.validateToken("valid-token")).thenReturn(true);
        when(jwtUtil.parseToken("valid-token")).thenReturn(claims);
        when(claims.getSubject()).thenReturn("1");
        lenient().when(claims.get("role", String.class)).thenReturn("USER");
        when(redisTemplate.hasKey("token:1")).thenReturn(false);

        filter.doFilterInternal(request, response, chain);

        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        assertNotNull(auth);
        assertEquals("1", auth.getPrincipal());

        verify(chain).doFilter(request, response);
    }

    @Test
    void doFilter_ShouldAlwaysCallFilterChain() throws Exception {
        when(request.getHeader("Authorization")).thenReturn(null);

        filter.doFilterInternal(request, response, chain);

        verify(chain, times(1)).doFilter(request, response);
    }

    @Test
    void doFilter_ShouldCallFilterChain_WithValidTokenAndRedis() throws Exception {
        when(request.getHeader("Authorization")).thenReturn("Bearer valid-token");
        when(jwtUtil.validateToken("valid-token")).thenReturn(true);
        when(jwtUtil.parseToken("valid-token")).thenReturn(claims);
        when(claims.getSubject()).thenReturn("1");
        when(claims.get("role", String.class)).thenReturn("USER");
        when(redisTemplate.hasKey("token:1")).thenReturn(true);

        filter.doFilterInternal(request, response, chain);

        verify(chain, times(1)).doFilter(request, response);
    }

    @Test
    void doFilter_ShouldSetDevAuth_WithEmptyHeader() throws Exception {
        when(request.getHeader("Authorization")).thenReturn("");

        filter.doFilterInternal(request, response, chain);

        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        assertNotNull(auth);
        assertEquals("1", auth.getPrincipal());

        verify(chain).doFilter(request, response);
    }
}
