DROP DATABASE IF EXISTS medibook_db;
CREATE DATABASE medibook_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE medibook_db;

-- ─── Users (Patients) ───
CREATE TABLE users_app_user (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(254) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    phone      VARCHAR(20)  DEFAULT '',
    role       VARCHAR(20)  DEFAULT 'patient',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ─── Patient Profile ───
CREATE TABLE users_app_patientprofile (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    patient_id              INT          NOT NULL UNIQUE,
    address                 VARCHAR(255) DEFAULT '',
    date_of_birth           DATE,
    gender                  VARCHAR(10)  DEFAULT '',
    profile_picture         VARCHAR(100),
    blood_type              VARCHAR(5)   DEFAULT '',
    allergies               TEXT,
    insurance_provider      VARCHAR(100) DEFAULT '',
    insurance_number        VARCHAR(100) DEFAULT '',
    insurance_expiry        DATE,
    emergency_contact_name  VARCHAR(100) DEFAULT '',
    emergency_contact_phone VARCHAR(20)  DEFAULT '',
    updated_at              DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users_app_user(id) ON DELETE CASCADE
);

-- ─── Medical Record ───
CREATE TABLE users_app_medicalrecord (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    patient_id  INT      NOT NULL UNIQUE,
    medications TEXT,
    conditions  TEXT,
    procedures  TEXT,
    notes       TEXT,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users_app_user(id) ON DELETE CASCADE
);

-- ─── Health Summary ───
CREATE TABLE users_app_healthsummary (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT         NOT NULL UNIQUE,
    chief_complaint TEXT,
    diagnosis       TEXT,
    treatment_plan  TEXT,
    vitals_bp       VARCHAR(20) DEFAULT '',
    vitals_pulse    VARCHAR(20) DEFAULT '',
    vitals_temp     VARCHAR(20) DEFAULT '',
    vitals_weight   VARCHAR(20) DEFAULT '',
    vitals_height   VARCHAR(20) DEFAULT '',
    updated_at      DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users_app_user(id) ON DELETE CASCADE
);

-- ─── Doctor ───
CREATE TABLE users_app_doctor (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    email          VARCHAR(254) NOT NULL UNIQUE,
    phone          VARCHAR(20)  DEFAULT '',
    bio            TEXT,
    image          VARCHAR(255) DEFAULT '',
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ─── Agent ───
CREATE TABLE users_app_agent (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    agent_id   VARCHAR(20)  NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    email      VARCHAR(254) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    phone      VARCHAR(20)  DEFAULT '',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ─── Appointment ───
CREATE TABLE users_app_appointment (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    patient_id    INT         NOT NULL,
    doctor_id     INT         NOT NULL,
    date          DATE        NOT NULL,
    time          TIME        NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes         TEXT,
    reminder_sent TINYINT(1)  NOT NULL DEFAULT 0,
    created_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users_app_user(id)   ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES users_app_doctor(id) ON DELETE CASCADE
);

-- ─── Bill ───
CREATE TABLE users_app_bill (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    patient_id  INT            NOT NULL,
    amount      DECIMAL(10, 2) NOT NULL,
    status      VARCHAR(20)    NOT NULL DEFAULT 'unpaid',
    due_date    DATE           NOT NULL,
    description TEXT,
    created_at  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users_app_user(id) ON DELETE CASCADE
);

-- ─── Message ───
CREATE TABLE users_app_message (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    sender_id  INT          NOT NULL,
    subject    VARCHAR(255) NOT NULL,
    body       TEXT         NOT NULL,
    is_read    TINYINT(1)   NOT NULL DEFAULT 0,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reply      TEXT,
    replied_at DATETIME,
    is_replied TINYINT(1)   NOT NULL DEFAULT 0,
    FOREIGN KEY (sender_id) REFERENCES users_app_user(id) ON DELETE CASCADE
);

-- ─── Lab Result ───
CREATE TABLE users_app_labresult (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    patient_id   INT          NOT NULL,
    test_name    VARCHAR(200) NOT NULL,
    result       TEXT         NOT NULL,
    normal_range VARCHAR(100) DEFAULT '',
    status       VARCHAR(20)  NOT NULL DEFAULT 'pending',
    test_date    DATE         NOT NULL,
    notes        TEXT,
    file         VARCHAR(100),
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users_app_user(id) ON DELETE CASCADE
);

-- ─── Patient File ───
CREATE TABLE users_app_patientfile (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    patient_id  INT          NOT NULL,
    name        VARCHAR(200) NOT NULL,
    file        VARCHAR(100) NOT NULL,
    file_type   VARCHAR(50)  DEFAULT '',
    uploaded_by VARCHAR(50)  NOT NULL DEFAULT 'agent',
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users_app_user(id) ON DELETE CASCADE
);

-- ─── Patient Document ───
CREATE TABLE users_app_patientdocument (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    patient_id  INT      NOT NULL,
    file        VARCHAR(100) NOT NULL,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users_app_patientprofile(id) ON DELETE CASCADE
);

-- ─── Password Reset Code ───
CREATE TABLE users_app_passwordresetcode (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT        NOT NULL,
    code       VARCHAR(6) NOT NULL,
    created_at DATETIME   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_used    TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users_app_user(id) ON DELETE CASCADE
);

SHOW TABLES;
