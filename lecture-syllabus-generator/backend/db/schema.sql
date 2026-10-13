-- ============================================================
-- lecture-syllabus-generator DDL (与 models.py 等价)
-- SQLite 实现，字段与 MySQL 兼容
-- ============================================================

CREATE TABLE IF NOT EXISTS task (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       VARCHAR(255) DEFAULT '未命名任务',
    status      VARCHAR(32)  DEFAULT 'pending',  -- pending/running/success/failed/partial
    page_count  INTEGER      DEFAULT 0,
    error_msg   TEXT,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS page (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id              INTEGER NOT NULL,
    page_no              INTEGER NOT NULL,          -- 逻辑页码
    filename             VARCHAR(512) NOT NULL,
    file_path            VARCHAR(512) NOT NULL,
    confidence           REAL    DEFAULT 0.0,
    low_confidence_flag  BOOLEAN DEFAULT 0,
    failed_flag          BOOLEAN DEFAULT 0,
    recognized_text      TEXT,
    error_msg            TEXT,
    created_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS knowledge_point (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id       INTEGER NOT NULL,
    page_id       INTEGER NOT NULL,
    content       TEXT NOT NULL,
    kp_type       VARCHAR(64) DEFAULT 'concept',   -- concept/conclusion/method/example
    source_type   VARCHAR(32) DEFAULT '课堂原话',   -- 课堂原话 / AI推断
    source_pages  VARCHAR(128) NOT NULL,           -- 如 "P1" 或 "P1,P2"
    dedup_key     VARCHAR(256) NOT NULL,
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE,
    FOREIGN KEY (page_id) REFERENCES page(id)
);

CREATE TABLE IF NOT EXISTS outline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER NOT NULL,
    markdown    TEXT NOT NULL,
    version     INTEGER DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outline_node (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    outline_id    INTEGER NOT NULL,
    level         INTEGER NOT NULL,   -- 1=模块, 2=知识点
    title         VARCHAR(512) NOT NULL,
    content       TEXT,
    source_type   VARCHAR(32),
    source_pages  VARCHAR(128),
    parent_id     INTEGER,
    sort_order    INTEGER DEFAULT 0,
    FOREIGN KEY (outline_id) REFERENCES outline(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES outline_node(id)
);

CREATE TABLE IF NOT EXISTS export_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER NOT NULL,
    file_size   INTEGER DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES task(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_page_task ON page(task_id);
CREATE INDEX IF NOT EXISTS idx_kp_task ON knowledge_point(task_id);
CREATE INDEX IF NOT EXISTS idx_outline_task ON outline(task_id);
CREATE INDEX IF NOT EXISTS idx_node_outline ON outline_node(outline_id);
CREATE INDEX IF NOT EXISTS idx_export_task ON export_log(task_id);