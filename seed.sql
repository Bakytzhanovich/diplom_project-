INSERT INTO roles (name) VALUES
('admin'),
('manager'),
('employee');

INSERT INTO users (username, password, department, role_id, is_active) VALUES
('admin', 'admin123', 'IT', 1, 1),
('aiman.sholpan', 'user123', 'HR', 3, 1),
('manager', 'manager123', 'Finance', 2, 1),
('nurs', 'nurs2004', 'Founder', 1, 1);


INSERT INTO permissions (resource_type, action) VALUES
('workspace', 'view'),
('file', 'view'),
('file', 'download'),
('email', 'send'),
('admin_panel', 'view'),
('finance_portal', 'view');

INSERT INTO role_permissions (role_id, permission_id) VALUES
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 5),
(1, 6),

(2, 1),
(2, 2),
(2, 3),
(2, 4),
(2, 6),

(3, 1),
(3, 2),
(3, 4);