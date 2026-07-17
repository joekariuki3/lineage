# Lineage

**Lineage** is a digital space dedicated to strengthening family connections and preserving precious memories.

[Live Demo](https://lineage.joelmuhoho.com/) | [Read the Case Study](https://medium.com/@joel_Muhoho/lineage-a-journey-into-family-roots-and-connections-3bc375684455)

## Problem Statement

As families expand and geographic distances grow, keeping track of family history, coordinating events, and preserving shared memories becomes increasingly difficult. Traditional methods often rely on fragmented social media groups or physical records that are susceptible to being lost or forgotten.

## Solution

Lineage is a comprehensive digital platform designed to be a centralized hub for families. It allows users to intuitively map out their family trees, securely record vital dates and relationships, and coordinate family events within a private, authenticated space.

## Features

- **Interactive Family Tree:** Visually explore and manage complex family dynamics (roots, parents, children, spouses).
- **Event Planning:** Plan, track, and organize upcoming and past family events with location and date tracking.
- **Role-Based Access & Privacy:** Secure authentication system ensuring family data is only visible to authorized members.
- **Shareable Links:** Generate secure, tokenized links to invite family members to explore the tree.
- **Responsive UI:** Built with TailwindCSS for a seamless experience on both desktop and mobile.

## Technologies Used

- **Backend:** Python, Flask, SQLAlchemy (ORM)
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **Frontend:** HTML5, Jinja2, TailwindCSS, JavaScript, jQuery
- **Testing & CI:** Pytest, GitHub Actions

## Architecture Overview

Lineage follows a modular, monolithic architecture using Flask Blueprints to separate concerns (`auth`, `family`, `member`, `event`, `link`).

For deep dives into the system design, please refer to our documentation directory:

- [Application Flow](./docs/architecture/application_flow.md)
- [Database Entity Relationship Diagram (ERD)](./docs/architecture/entity_relationship_diagram.md)
- [Deployment & AWS Infrastructure](./docs/architecture/deployment_aws.md)
- [Security & Scalability](./docs/infrastructure/security_and_scalability.md)

## Setup Instructions

### Prerequisites

- Python 3.11+
- Git

### Local Development

1. **Clone the repository:**

   ```bash
   git clone https://github.com/joelmuhoho/lineage.git

   cd lineage
   ```

2. **Set up a virtual environment (Recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt

   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory. Use `.env.example` as a template:

   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secure_secret_key
   LINEAGE_DATABASE_URI=sqlite:///lineage.db

   ```

5. **Initialize the Database:**

   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade

   ```

6. **Run the application:**
   ```bash
   flask run --port=5001

   ```
7. Access the app at `http://localhost:5001`.

### Running Tests

Lineage uses `pytest` for unit and integration testing.

```bash
pytest

```

## Lessons Learned

- **Complex Data Modeling:** Designing a self-referential database schema for family trees required strict application-level validation to prevent logical loops (e.g., a child cannot be older than a parent).
- **State Management:** Managing complex nested UI states (like expanding/collapsing family nodes) taught valuable lessons in combining server-side rendering (Jinja2) with asynchronous JavaScript (AJAX).
- **Security First:** Implementing secure JWT tokens for password resets and shareable links reinforced the importance of stateless, time-bound authentication.
