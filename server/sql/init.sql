CREATE DATABASE IF NOT EXISTS db_enterprise_ga
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE db_enterprise_ga;
SET NAMES utf8mb4;

DROP TABLE IF EXISTS qa_record;
DROP TABLE IF EXISTS knowledge_document;
DROP TABLE IF EXISTS sys_user;

CREATE TABLE sys_user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录账号',
  password VARCHAR(64) NOT NULL COMMENT 'MD5加密密码',
  role VARCHAR(20) NOT NULL COMMENT '角色：admin管理员，user普通用户',
  real_name VARCHAR(100) NOT NULL COMMENT '用户姓名',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1启用，0禁用',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

CREATE TABLE knowledge_document (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '知识文档ID',
  title VARCHAR(200) NOT NULL COMMENT '文档标题',
  source_type VARCHAR(20) NOT NULL COMMENT '来源类型：text文本，file文件',
  file_name VARCHAR(255) DEFAULT NULL COMMENT '原始文件名',
  content LONGTEXT NOT NULL COMMENT '文档正文',
  chunk_count INT NOT NULL DEFAULT 0 COMMENT '向量片段数量',
  created_by BIGINT NOT NULL COMMENT '创建人ID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  CONSTRAINT fk_document_user FOREIGN KEY (created_by) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识文档表';

CREATE TABLE qa_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '问答记录ID',
  user_id BIGINT NOT NULL COMMENT '提问用户ID',
  question TEXT NOT NULL COMMENT '用户问题',
  answer LONGTEXT NOT NULL COMMENT '模型回答',
  references_json JSON NULL COMMENT '引用文档JSON',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  CONSTRAINT fk_record_user FOREIGN KEY (user_id) REFERENCES sys_user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问答记录表';

INSERT INTO sys_user(username, password, role, real_name, status) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin', '系统管理员', 1),
('user', 'e10adc3949ba59abbe56e057f20f883e', 'user', '普通用户', 1);

INSERT INTO knowledge_document(title, source_type, file_name, content, chunk_count, created_by) VALUES
('企业报销制度', 'text', '', '员工出差前应完成审批。差旅结束后七个工作日内提交发票、行程单和审批记录。单次报销金额超过五千元需要部门负责人和财务负责人共同审批。', 0, 1),
('信息安全规范', 'text', '', '企业内部系统账号不得外借。密码至少每九十天更换一次，发现疑似泄露应立即联系信息安全管理员。敏感资料不得通过个人网盘或私人邮箱传输。', 0, 1),
('新员工入职流程', 'text', '', '新员工入职当天需要完成身份核验、劳动合同签署、工牌领取和系统账号开通。直属主管负责安排导师并在试用期内进行月度沟通。', 0, 1);
