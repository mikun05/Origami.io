# Origami.io

An interactive rigid-origami simulator for exploring single-vertex folding using geometric constraints, numerical optimisation, and 3D visualisation.

This project was developed as part of my MCompPhil in Computer Science and Philosophy at the University of Oxford.

## Overview

Origami.io simulates the folding of single-vertex rigid origami patterns and visualises the resulting geometry interactively in the browser.

The project combines:

- geometric constraints governing valid fold configurations
- numerical optimisation to solve for fold states
- Rodrigues' rotation formula for updating 3D geometry
- interactive 3D browser-based visualisation
- comparison of alternative numerical solution methods

A key part of the project was analysing the performance and trade-offs of different numerical approaches rather than treating the simulator purely as a visualisation tool.

## Demo

A public demo is currently being prepared.

<!-- Replace with deployed URL -->
<!-- Demo: https://mikun05.github.io/Origami.io/ -->

## Features

- Interactive 3D visualisation of rigid-origami folds
- Simulation of single-vertex crease patterns
- Numerical solving of geometric fold constraints
- Exploration of different fold states
- Comparison of numerical methods and optimisation behaviour
- Browser-based visualisation of computed folds

## Technical Approach

Rigid folding is modelled using angular and geometric constraints around a single vertex.

The simulation computes candidate fold states numerically and applies the resulting transformations to the model in 3D. Rodrigues' rotation formula is used to rotate faces around crease axes as folding progresses.

The project also investigates the behaviour of different numerical methods, including their convergence, performance, and suitability for interactive simulation.

## Tech Stack

### Simulation

- Python
- SciPy
- Numerical optimisation

### Visualisation

- JavaScript
- Three.js
- SolidJS
- Vite

## Project Structure

```text
Origami.io/
├── simulation/        # Numerical simulation and geometry code
│   ├── src/
│   ├── tests/
│   ├── examples/
│   └── requirements.txt
│
├── visualizer/        # Interactive browser-based 3D visualisation
│   ├── src/
│   ├── public/
│   └── package.json
│
├── run.py             # Convenience script for running the project locally
└── README.md