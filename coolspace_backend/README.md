# CoolSpace AI - Backend Service

This directory contains the backend service for the CoolSpace AI project. It's a Python-based service using the Flask framework.

## Core Responsibilities
1.  **API Server (`server.py`)**: Provides an HTTP API for the mobile app client. The primary endpoint is `/api/v1/upload_scan` for receiving 3D room geometry.
2.  **CFD Analysis Orchestration**: Manages the pipeline for running Computational Fluid Dynamics (CFD) simulations on the uploaded room scans.

---

## CFD Integration Strategy: Using OpenFOAM

For our CFD analysis, we will use **OpenFOAM**, a powerful, open-source CFD software package. It is highly customizable and widely used in both academia and industry for complex fluid flow simulations, including heat transfer, which is perfect for our use case.

### Why OpenFOAM?
*   **Open Source**: No licensing fees, which is critical for keeping operational costs down.
*   **Powerful & Validated**: It's a robust solver trusted for a wide range of physics problems.
*   **Customizable**: We can write our own solvers or utilities if needed.
*   **Large Community**: Extensive documentation and community support are available.

### Asynchronous Simulation Workflow

CFD simulations are computationally expensive and can take anywhere from minutes to hours to run. It is **critical** that the web server does not run these simulations directly in an API request-response cycle. Doing so would cause client timeouts and make the server unresponsive.

We will implement an **asynchronous task queue** system. A popular and robust choice for this in the Python ecosystem is **Celery** with **Redis** or **RabbitMQ** as the message broker.

The workflow for processing a new scan will be as follows:

1.  **Upload**: The iOS app `POST`s the `.obj` file to the `/api/v1/upload_scan` endpoint on the Flask server.
2.  **Store & Queue**: The Flask server saves the `.obj` file to a persistent storage (e.g., a mounted volume or a cloud bucket) and gets a unique `scan_id`. It then creates a new job on the Celery task queue, passing the `scan_id` and file path as arguments. The server immediately returns a `201 Accepted` response to the app, confirming the task has been queued.
    ```
    +----------------+     (1. POST /upload_scan)     +-----------------+
    |   Mobile App   | -----------------------------> |   Flask Server  |
    +----------------+     (2. 201 Accepted)          +-----------------+
                         <-----------------------------       | (2a. Save file)
                                                              |
                                                              v (2b. Add job to queue)
                                                      +-----------------+
                                                      |  Message Queue  |
                                                      | (e.g., Redis)   |
                                                      +-----------------+
    ```
3.  **Consume & Process**: A separate **CFD Worker** process (running Celery) is constantly listening for new jobs on the queue. When it receives a job, it performs the following steps:
    *   **a. Pre-processing (Meshing)**: The worker takes the raw `.obj` file and uses an OpenFOAM utility like `snappyHexMesh` to generate a high-quality computational mesh suitable for simulation. This step also involves defining boundary patches (walls, windows, AC inlet, fan inlet).
    *   **b. Set Boundary Conditions**: The worker programmatically creates the necessary configuration files for the OpenFOAM solver. This includes setting the temperature of the window patch (from weather data), the velocity and temperature of the AC inlet patch (from device specs), etc.
    *   **c. Run Solver**: The worker executes the appropriate OpenFOAM solver (e.g., `buoyantBoussinesqSimpleFoam` for thermal analysis) on the prepared case.
    *   **d. Post-processing**: Once the simulation converges, the worker runs post-processing utilities to extract the key results (e.g., temperature and velocity fields) and saves them in a structured format (like JSON or a lightweight binary format) associated with the `scan_id`.
    *   **e. Update Status**: The worker updates a database to mark the `scan_id` as "Completed" and stores the path to the results.

4.  **Retrieve Results**: The mobile app can later poll another endpoint, e.g., `/api/v1/results/{scan_id}`, to check the status of the simulation and retrieve the final results once they are ready.

This architecture ensures the API server remains responsive and allows us to scale the number of CFD workers independently based on the simulation load.
