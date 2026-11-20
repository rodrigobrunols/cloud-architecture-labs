package com.demo.pool.connectionpollhikaricprdsproxy;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class SlowController {
    private final JdbcTemplate jdbc;
    public SlowController(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    @GetMapping("/slow")
    @Transactional
    public String slow() {
        jdbc.queryForObject("SELECT pg_sleep(2)", Object.class);
        return "ok";
    }

    @GetMapping("/fixed")
    public String fixed() throws InterruptedException {
        Thread.sleep(2000);                                   // slow external call, no connection held
        jdbc.queryForObject("SELECT 1", Integer.class);       // short DB work, a few ms
        return "ok";
    }
}
