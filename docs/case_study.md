# Case Study

## Lineage - Preserving Family Roots & Connections

- **Role:** Full-Stack Developer
- **Technologies:** Python, Flask, SQLAlchemy, JavaScript, TailwindCSS, SQLite/PostgreSQL

## The Challenge

As families expand and geographic distances grow, keeping track of family history, coordinating events, and preserving shared memories becomes difficult. Traditional methods rely on fragmented social media groups or physical records susceptible to being lost.

## The Solution

I developed **Lineage**, a comprehensive digital platform designed to be a centralized hub for families. Lineage allows users to intuitively map out their family trees, record vital dates securely, and coordinate family events within a private, authenticated space.

## Engineering Architecture & Implementation

- **Modular Backend:** Built with Python and Flask, the application follows a robust modular Blueprint pattern (Auth, Family, Member, Event), making the codebase scalable and maintainable.
- **Relational Data Modeling:** Designed complex bidirectional user relationships utilizing SQLAlchemy. The system accurately models intricate family dynamics including roots, parents, children, and spouses with rigid application-level validation.
- **Dynamic Interface:** The front-end leverages Jinja2 templating with TailwindCSS, dynamically parsing nested relationships into an interactive UI tree.

## Outcomes & Next Steps

The application successfully handles complex tree logic and event planning out of the box. Following Agile best practices, the upcoming roadmap focuses on integrating an interactive Canvas/SVG-based data visualization for the tree logic and AWS S3 integration for a "Photo Memories" feature to store and share family albums securely.
