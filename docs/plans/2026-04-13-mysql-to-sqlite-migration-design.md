# MySQL → SQLite 全量迁移设计

## 1. 概述

将 MySQL 数据库中的数据全量迁移到 SQLite，包括 7 张数据表。

**迁移顺序**遵循表依赖关系：先迁移被引用的表（主表），再迁移依赖表（从表）。

## 2. 待迁移表清单

| 顺序 | 表名 | 说明 |
|------|------|------|
| 1 | `user` | 用户表 |
| 2 | `note_risk` | 风险记录表 |
| 3 | `t_week_note` | 周记录表 |
| 4 | `t_note_detail` | 记录详情表（依赖 t_week_note） |
| 5 | `t_car_info` | 车辆信息表 |
| 6 | `t_car_pics` | 车辆图片表（依赖 t_car_info） |
| 7 | `t_chat_message` | 聊天记录表 |

## 3. MySQL vs SQLite 差异

| 差异点 | MySQL | SQLite | 处理方式 |
|--------|-------|--------|----------|
| 自增主键 | `AUTO_INCREMENT` | `AUTOINCREMENT` | SQLite 自动处理 |
| 字符集 | `utf8mb4` | TEXT | 直接存储 UTF-8 字符串 |
| 日期时间 | `DATETIME` | TEXT | 保持 ISO8601 字符串格式 |
| 外键约束 | 有 | 无 | 迁移时按顺序保证完整性 |
| BIT 类型 | BIT(1) | INTEGER | 0/1 值迁移 |

## 4. 迁移脚本结构

**文件路径：** `yail/tools/migrate_mysql_to_sqlite.py`

### 4.1 配置读取

```python
# MySQL 配置
from conf.db import rec_db
mysql_config = {
    'host': rec_db['host'],
    'port': rec_db['port'],
    'user': rec_db['user'],
    'password': rec_db['password'],
    'db': rec_db['db'],
    'charset': 'utf8mb4'
}

# SQLite 路径
from conf.db import SQLITE_DB_PATH
```

### 4.2 迁移流程

```
1. 连接 MySQL 和 SQLite
2. 禁用 SQLite 外键约束 (PRAGMA foreign_keys = OFF)
3. 开启 SQLite 事务 (BEGIN TRANSACTION)
4. 按顺序清空并迁移每张表
5. 提交事务 (COMMIT)
6. 恢复外键约束 (PRAGMA foreign_keys = ON)
```

### 4.3 表迁移逻辑

```python
def migrate_table(mysql_conn, sqlite_conn, table_name, columns):
    # 1. 清空 SQLite 表
    sqlite_conn.execute(f"DELETE FROM {table_name}")
    
    # 2. 从 MySQL 读取数据
    sql = f"SELECT {columns} FROM {table_name}"
    mysql_cursor.execute(sql)
    rows = mysql_cursor.fetchall()
    
    # 3. 插入 SQLite
    placeholders = ','.join(['?' for _ in columns.split(',')])
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    sqlite_conn.executemany(insert_sql, rows)
    
    # 4. 返回迁移行数
    return len(rows)
```

## 5. 迁移顺序详细说明

### 第一批：无依赖表（可并行）

| 表名 | 关键列 |
|------|---------|
| `user` | user_id, user_name, nickname, password, created_at, updated_at |

### 第二批：依赖 user 表

| 表名 | 关键列 | 外键 |
|------|--------|------|
| `note_risk` | id, user_id, user_name, ... | user_id → user |
| `t_week_note` | id, user_id, user_name, ... | user_id → user |
| `t_car_info` | id, user_name, ... | 无直接外键 |

### 第三批：依赖 t_week_note

| 表名 | 关键列 | 外键 |
|------|--------|------|
| `t_note_detail` | id, note_id, user_id, ... | note_id → t_week_note |

### 第四批：依赖 t_car_info

| 表名 | 关键列 | 外键 |
|------|--------|------|
| `t_car_pics` | id, car_id, path, ... | car_id → t_car_info |

### 第五批：独立表

| 表名 | 关键列 |
|------|---------|
| `t_chat_message` | id, user_id, session_id, role, content, created_at |

## 6. 错误处理

- **策略：** 遇到错误立即中断，输出错误信息
- **回滚：** 事务自动回滚，保证数据一致性
- **日志：** 输出迁移进度和结果

## 7. 使用方式

```bash
cd yail
python tools/migrate_mysql_to_sqlite.py
```

## 8. 预期输出

```
=== MySQL → SQLite 数据迁移 ===
开始迁移...

[1/7] 迁移 user 表... 5 rows
[2/7] 迁移 note_risk 表... 0 rows
[3/7] 迁移 t_week_note 表... 443 rows
[4/7] 迁移 t_note_detail 表... 1783 rows
[5/7] 迁移 t_car_info 表... 20 rows
[6/7] 迁移 t_car_pics 表... 45 rows
[7/7] 迁移 t_chat_message 表... 150 rows

迁移完成！总计: 2296 rows
```
