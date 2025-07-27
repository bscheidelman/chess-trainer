# Chess Trainer

A web-based chess training tool that provides instant feedback on move quality by leveraging the Lichess database and a powerful chess engine API.

## Live Demo

You can play the Chess Trainer live in your browser at the following URL:

**[https://bscheidelman.github.io/chess-trainer/](https://bscheidelman.github.io/chess-trainer/)**

## Features

-   **Interactive Chessboard:** A clean, modern, and responsive chessboard interface.
-   **Play Against Lichess Database:** The computer opponent plays moves based on the massive Lichess database of human games, providing a realistic training experience.
-   **Instant Move Analysis:** Every move you make is instantly evaluated for its quality (Best, Excellent, Good, Inaccuracy, Mistake, Blunder).
-   **Engine Fallback:** If a position is not in the Lichess database, the app seamlessly switches to a strong engine to continue the game.
-   **Visual Feedback:** The computer's last move is clearly highlighted on the board, with a descriptive text of its action.
-   **Core Controls:** Easily start a new game or undo your last move to try a different line.

## Technologies Used

-   **HTML, CSS, JavaScript:** The core of the application.
-   **Tailwind CSS:** For modern and responsive styling.
-   **Chess.js:** For client-side chess logic, move validation, and FEN generation.
-   **Chess-API.com:** Provides remote Stockfish engine analysis for move evaluation.
-   **Lichess Opening Explorer API:** Used to source common human-played moves for the computer opponent.
-   **Font Awesome:** For icons.

## Local Development

For those who wish to run the project locally:

1.  Clone the repository:
    ```bash
    git clone [https://github.com/bscheidelman/chess-trainer.git](https://github.com/bscheidelman/chess-trainer.git)
    ```
2.  Navigate to the project directory:
    ```bash
    cd chess-trainer
    ```
3.  Open the `index.html` file in your web browser.
