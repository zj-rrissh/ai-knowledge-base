package com.kb.service;

import com.kb.model.dto.AuthRequest;
import com.kb.model.dto.AuthResponse;
import com.kb.model.entity.User;
import com.kb.repository.UserRepository;
import com.kb.security.JwtUtil;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

@Service
public class AuthService {
    private final UserRepository userRepo;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final StringRedisTemplate redisTemplate;

    public AuthService(UserRepository userRepo, PasswordEncoder passwordEncoder,
                       JwtUtil jwtUtil, StringRedisTemplate redisTemplate) {
        this.userRepo = userRepo;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
        this.redisTemplate = redisTemplate;
    }

    public AuthResponse register(AuthRequest req) {
        if (userRepo.existsByUsername(req.getUsername())) {
            throw new RuntimeException("用户名已存在");
        }
        User user = new User();
        user.setUsername(req.getUsername());
        user.setPassword(passwordEncoder.encode(req.getPassword()));
        user = userRepo.save(user);

        String access = jwtUtil.generateAccessToken(user.getId(), user.getUsername(), user.getRole());
        String refresh = jwtUtil.generateRefreshToken(user.getId());
        redisTemplate.opsForValue().set("token:" + user.getId(), access, 2, TimeUnit.HOURS);

        return new AuthResponse(access, refresh, user.getUsername());
    }

    public AuthResponse login(AuthRequest req) {
        User user = userRepo.findByUsername(req.getUsername())
                .orElseThrow(() -> new RuntimeException("用户不存在"));
        if (!passwordEncoder.matches(req.getPassword(), user.getPassword())) {
            throw new RuntimeException("密码错误");
        }

        String access = jwtUtil.generateAccessToken(user.getId(), user.getUsername(), user.getRole());
        String refresh = jwtUtil.generateRefreshToken(user.getId());
        redisTemplate.opsForValue().set("token:" + user.getId(), access, 2, TimeUnit.HOURS);

        return new AuthResponse(access, refresh, user.getUsername());
    }
}
