package com.kb.security;

import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.TimeUnit;

@Component
public class JwtAuthFilter extends OncePerRequestFilter {
    private final JwtUtil jwtUtil;
    private final StringRedisTemplate redisTemplate;

    public JwtAuthFilter(JwtUtil jwtUtil, StringRedisTemplate redisTemplate) {
        this.jwtUtil = jwtUtil;
        this.redisTemplate = redisTemplate;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (!StringUtils.hasText(header) || !header.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }

        String token = header.substring(7);
        if (!jwtUtil.validateToken(token)) {
            chain.doFilter(request, response);
            return;
        }

        Claims claims = jwtUtil.parseToken(token);
        String userId = claims.getSubject();
        String redisKey = "token:" + userId;
        if (Boolean.FALSE.equals(redisTemplate.hasKey(redisKey))) {
            chain.doFilter(request, response);
            return;
        }

        var auth = new UsernamePasswordAuthenticationToken(
                userId,
                null,
                List.of(new SimpleGrantedAuthority("ROLE_" + claims.get("role", String.class)))
        );
        SecurityContextHolder.getContext().setAuthentication(auth);

        redisTemplate.expire(redisKey, 2, TimeUnit.HOURS);

        chain.doFilter(request, response);
    }
}
