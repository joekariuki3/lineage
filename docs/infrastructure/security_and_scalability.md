## Security & Scalability

**Security Considerations:**

- **Authentication & Hashing:** User passwords are encrypted using Werkzeug's `generate_password_hash` before database insertion.
- **Tokenization:** JWT (JSON Web Tokens) are utilized for secure, stateless password reset links, preventing unauthorized access.
- **CSRF Protection:** Form submissions are protected against Cross-Site Request Forgery via Flask-WTF's built-in CSRF token validation (`form.hidden_tag()`).
- **Authorization Guardrails:** Backend logic strictly enforces ownership checks (e.g., verifying `family.user_id == current_user.user_id` before allowing deletions or edits).

**Scalability Considerations:**

- **Database Migration:** Currently supporting SQLite for development. For production scaling, the ORM (SQLAlchemy) allows seamless transition to PostgreSQL to handle concurrent reads/writes and larger family tree datasets.
- **Stateless Architecture:** The application logic is primarily stateless (session cookies handle auth), allowing it to be horizontally scaled across multiple instances behind a Load Balancer.
- **Media Storage (Roadmap):** To ensure server storage doesn't become a bottleneck, future photo/media uploads are planned to be decoupled and stored in cloud object storage (AWS S3).
