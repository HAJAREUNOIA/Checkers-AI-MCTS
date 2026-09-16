\# Checkers AI — Enhanced Monte Carlo Tree Search



An advanced Artificial Intelligence project for English draughts (checkers), based on Monte Carlo Tree Search (MCTS) and enhanced with strategic game evaluation and guided simulations.



The project explores how Monte Carlo Tree Search can be improved by incorporating domain-specific knowledge into the decision-making process.



\## Project Overview



This project implements an AI agent capable of playing English draughts using Monte Carlo Tree Search.



The AI combines classical MCTS with additional strategic mechanisms designed to improve the quality of simulations and move selection, including:



\- Guided rollouts

\- Mandatory capture handling

\- Pawn advancement

\- Centre control

\- King bonuses

\- Strategic positional evaluation

\- Sigmoid-based positional evaluation

\- Adjustable search iterations



The project also includes an interactive graphical interface developed with Pygame, an evaluation framework used to analyze the AI's performance, and an interactive visualization of the MCTS search tree.



\## Main Features



\### Monte Carlo Tree Search



The AI uses Monte Carlo Tree Search to explore possible game states and select moves according to simulated outcomes.



The search process includes the classical MCTS stages:



1\. Selection

2\. Expansion

3\. Simulation

4\. Backpropagation



\### Enhanced Rollouts



Instead of relying only on completely random simulations, the project introduces guided rollouts using strategic information about the board.



The evaluation takes into account factors such as:



\- Forced captures

\- Pawn advancement

\- Centre control

\- King positioning

\- Strategic board positions



This allows the AI to make decisions using both search and domain-specific knowledge.



\### Positional Evaluation



A sigmoid-based positional evaluation function is used to provide a smoother assessment of board positions.



The evaluation considers different strategic characteristics of the current game state and contributes to the AI's decision-making process.



\### Interactive Game



The project includes a graphical interface implemented with Pygame.



The interface allows a user to interact with the AI and play English draughts while observing the AI's decisions.



\### Interactive MCTS Visualization



An interactive visualization was also developed to illustrate how the MCTS algorithm constructs and explores its search tree.



The visualization provides an interactive representation of the search process and allows users to observe the structure of the MCTS tree.



The visualization is available here:



https://mctshjr.netlify.app/



\## Experiments



Several experiments were conducted to study the impact of the number of MCTS iterations on the AI's performance.



The project includes experiments using:



\- 1,000 iterations

\- 2,000 iterations

\- 3,000 iterations



The evaluation results are stored in `exp\_winrate.csv` and visualized in `evaluation\_ia\_mcts.png`.



The experiments resulted in an observed win rate of approximately 72% for the evaluated configuration.



\## Project Structure



Checkers-AI-MCTS/

│

├── TER/

│   │

│   ├── main.py

│   │

│   ├── game/

│   │   ├── game.py

│   │   └── utilities.py

│   │

│   └── evaluation/

│       ├── evaluate (2).py

│       ├── evaluation\_ia\_mcts.png

│       └── exp\_winrate.csv

│

├── game (3).py

│

└── .gitignore



The project contains two game implementations, `game.py` and `game (3).py`, which can be used as alternative implementations of the checkers game logic.



\## Technologies Used



\- Python

\- Monte Carlo Tree Search (MCTS)

\- Pygame

\- NumPy

\- Pandas

\- Matplotlib



\## Evaluation



The evaluation component is located in the `evaluation/` directory.



It contains:



\- The evaluation script

\- Experimental win-rate data

\- Evaluation visualizations



These resources make it possible to analyze the AI's performance and compare different MCTS configurations.



\## Project Objectives



The main objectives of this project were to:



\- Implement Monte Carlo Tree Search for a board game

\- Develop an AI capable of playing English draughts

\- Improve classical MCTS using domain-specific knowledge

\- Experiment with guided simulations

\- Develop a positional evaluation function

\- Study the relationship between search iterations and AI performance

\- Analyze AI performance through experimental evaluation

\- Visualize the construction and exploration of the MCTS search tree



\## Results



The experiments demonstrate the impact of combining Monte Carlo Tree Search with strategic information specific to the game of checkers.



The project achieved an observed win rate of approximately 72% across the evaluated experiments.



\## Author



Hajar El Barhdadi



