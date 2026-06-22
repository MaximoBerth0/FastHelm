# Management Frontend

This repository contains the user interface for the `Management` back-office system. Built as a decoupled, static client, it is designed to securely and efficiently consume the backend REST API.

## Architecture & Core Stack

The frontend is architected as a lightweight Single Page Application (SPA) leveraging the following modern tools and standards:

* **Cloudflare Pages:** Automated static hosting and deployment on the Edge network, ensuring high availability and minimal latency.
* **Native JavaScript (ES6+) & Fetch API:** A framework-less approach utilizing standard web APIs to communicate asynchronously with the backend, eliminating the overhead of heavy JavaScript ecosystems.
* **Tailwind CSS & DaisyUI:** Used for quick, clean, and responsive UI layout styling, ensuring a professional dark-mode dashboard tailored for administration systems.

## Project Structure

The client follows a **feature-first** modular pattern, mirroring clean backend domains and isolating UI views from their respective business logic:

```text
management-front/
├── index.html              # Login page / Entry point
├── dashboard.html          # Main layout shell (Sidebar + Top navigation)
│
├── views/                  # UI Templates (HTML Snippets)
│   ├── inventory.html      # Isolated inventory table layout
│   └── orders.html         # Isolated orders dashboard layout
│
└── js/                     # Application Logic Layer
    ├── app.js              # Global API config & shared HTTP client wrapper
    │
    # Feature Modules
    ├── inventory/
    │   └── inventory.js    # Logic to fetch inventory data and manipulate the DOM
    └── orders/
        └── orders.js       # Logic to process orders and handle workflows
```

## Purpose

The main goal of this client is to provide a clean, visual dashboard to showcase the capabilities of the underlying backend infrastructure (inventory control, order workflows, and back-office administration) while demonstrating a fully decoupled, production-grade architecture.