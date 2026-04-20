"""
chess_generator.py
==================
Librería Python para generar partidas de ajedrez.

Funcionalidades:
  - Generar partidas aleatorias completas
  - Generar partidas desde una posición FEN personalizada
  - Exportar partidas en formato PGN
  - Reproducir partidas movimiento a movimiento (modo texto ASCII)
  - Estadísticas de la partida (número de movimientos, resultado, capturas)
  - Generar múltiples partidas en lote
"""

import chess
import chess.pgn
import random
import io
import datetime
from typing import Optional, List, Dict


# ─────────────────────────────────────────────────────────────────────────────
# Clase principal
# ─────────────────────────────────────────────────────────────────────────────

class ChessGameGenerator:
    """Genera y gestiona partidas de ajedrez."""

    def __init__(self, seed: Optional[int] = None):
        """
        Parámetros
        ----------
        seed : int, opcional
            Semilla para el generador de números aleatorios.
            Permite reproducir exactamente la misma partida.
        """
        self.rng = random.Random(seed)
        self.game: Optional[chess.pgn.Game] = None
        self.board: Optional[chess.Board] = None

    # ──────────────────────────────────────────────
    # Generación de partidas
    # ──────────────────────────────────────────────

    def generate_random_game(
        self,
        max_moves: int = 200,
        white_name: str = "Blancas",
        black_name: str = "Negras",
        event: str = "Partida Generada",
    ) -> chess.pgn.Game:
        """
        Genera una partida aleatoria completa (movimientos legales al azar).

        Parámetros
        ----------
        max_moves : int
            Número máximo de medios-movimientos (plies) antes de declarar tablas.
        white_name : str
            Nombre del jugador con piezas blancas.
        black_name : str
            Nombre del jugador con piezas negras.
        event : str
            Nombre del evento en la cabecera PGN.

        Retorna
        -------
        chess.pgn.Game
            Objeto PGN con la partida completa y metadatos.
        """
        board = chess.Board()
        game = chess.pgn.Game()
        game.headers["Event"] = event
        game.headers["Date"] = datetime.date.today().strftime("%Y.%m.%d")
        game.headers["White"] = white_name
        game.headers["Black"] = black_name
        game.headers["Round"] = "1"

        node = game
        move_count = 0

        while not board.is_game_over() and move_count < max_moves:
            legal = list(board.legal_moves)
            move = self.rng.choice(legal)
            node = node.add_variation(move)
            board.push(move)
            move_count += 1

        game.headers["Result"] = board.result()
        self.game = game
        self.board = board
        return game

    def generate_game_from_fen(
        self,
        fen: str,
        max_moves: int = 100,
        white_name: str = "Blancas",
        black_name: str = "Negras",
    ) -> chess.pgn.Game:
        """
        Genera una partida aleatoria desde una posición FEN personalizada.

        Parámetros
        ----------
        fen : str
            Cadena FEN que describe la posición inicial.
        max_moves : int
            Número máximo de medios-movimientos.
        white_name : str
            Nombre del jugador con piezas blancas.
        black_name : str
            Nombre del jugador con piezas negras.

        Retorna
        -------
        chess.pgn.Game
        """
        board = chess.Board(fen)
        game = chess.pgn.Game()
        game.setup(board)
        game.headers["Date"] = datetime.date.today().strftime("%Y.%m.%d")
        game.headers["White"] = white_name
        game.headers["Black"] = black_name

        node = game
        move_count = 0

        while not board.is_game_over() and move_count < max_moves:
            legal = list(board.legal_moves)
            move = self.rng.choice(legal)
            node = node.add_variation(move)
            board.push(move)
            move_count += 1

        game.headers["Result"] = board.result()
        self.game = game
        self.board = board
        return game

    def generate_batch(
        self,
        count: int = 5,
        max_moves: int = 200,
    ) -> List[chess.pgn.Game]:
        """
        Genera múltiples partidas aleatorias en lote.

        Parámetros
        ----------
        count : int
            Número de partidas a generar.
        max_moves : int
            Máximo de medios-movimientos por partida.

        Retorna
        -------
        List[chess.pgn.Game]
        """
        games = []
        for i in range(1, count + 1):
            g = self.generate_random_game(
                max_moves=max_moves,
                white_name=f"Motor_Blanco_{i}",
                black_name=f"Motor_Negro_{i}",
                event=f"Partida {i}",
            )
            games.append(g)
        return games

    # ──────────────────────────────────────────────
    # Exportación
    # ──────────────────────────────────────────────

    def to_pgn(self, game: Optional[chess.pgn.Game] = None) -> str:
        """
        Devuelve la partida en formato PGN como cadena de texto.

        Parámetros
        ----------
        game : chess.pgn.Game, opcional
            Si se omite, usa la última partida generada.
        """
        g = game or self.game
        if g is None:
            raise ValueError("No hay ninguna partida generada aún.")
        buf = io.StringIO()
        print(g, file=buf, end="\n")
        return buf.getvalue()

    def save_pgn(self, filepath: str, game: Optional[chess.pgn.Game] = None) -> None:
        """
        Guarda la partida en un archivo PGN.

        Parámetros
        ----------
        filepath : str
            Ruta del archivo destino (ej. "mi_partida.pgn").
        game : chess.pgn.Game, opcional
            Si se omite, usa la última partida generada.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_pgn(game))
        print(f"Partida guardada en: {filepath}")

    def save_batch_pgn(self, filepath: str, games: List[chess.pgn.Game]) -> None:
        """
        Guarda múltiples partidas en un único archivo PGN.

        Parámetros
        ----------
        filepath : str
            Ruta del archivo destino.
        games : list
            Lista de objetos chess.pgn.Game.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            for g in games:
                buf = io.StringIO()
                print(g, file=buf, end="\n\n")
                f.write(buf.getvalue())
        print(f"{len(games)} partidas guardadas en: {filepath}")

    # ──────────────────────────────────────────────
    # Estadísticas
    # ──────────────────────────────────────────────

    def get_stats(self, game: Optional[chess.pgn.Game] = None) -> Dict:
        """
        Devuelve estadísticas básicas de la partida.

        Retorna
        -------
        dict con claves:
            - total_moves      : total de medios-movimientos
            - white_moves      : movimientos de blancas
            - black_moves      : movimientos de negras
            - result           : resultado ("1-0", "0-1", "1/2-1/2", "*")
            - termination      : motivo de finalización
            - captures         : número de capturas totales
            - checks           : número de jaques
        """
        g = game or self.game
        if g is None:
            raise ValueError("No hay ninguna partida generada aún.")

        board = g.board()
        total_moves = 0
        captures = 0
        checks = 0

        for move in g.mainline_moves():
            if board.is_capture(move):
                captures += 1
            board.push(move)
            if board.is_check():
                checks += 1
            total_moves += 1

        white_moves = (total_moves + 1) // 2
        black_moves = total_moves // 2

        # Determinar terminación
        termination = "En curso"
        if board.is_checkmate():
            termination = "Jaque mate"
        elif board.is_stalemate():
            termination = "Ahogado"
        elif board.is_insufficient_material():
            termination = "Material insuficiente"
        elif board.is_seventyfive_moves():
            termination = "Regla de 75 movimientos"
        elif board.is_fivefold_repetition():
            termination = "Repetición de posición (5 veces)"
        elif total_moves >= 200:
            termination = "Límite de movimientos alcanzado"

        return {
            "total_moves": total_moves,
            "white_moves": white_moves,
            "black_moves": black_moves,
            "result": g.headers.get("Result", "*"),
            "termination": termination,
            "captures": captures,
            "checks": checks,
        }

    # ──────────────────────────────────────────────
    # Visualización en consola
    # ──────────────────────────────────────────────

    def print_board(self, board: Optional[chess.Board] = None) -> None:
        """
        Imprime el tablero actual en ASCII en la consola.

        Parámetros
        ----------
        board : chess.Board, opcional
            Si se omite, usa el tablero de la última partida generada.
        """
        b = board or self.board
        if b is None:
            raise ValueError("No hay ningún tablero disponible.")
        print(b)
        print()

    def replay_game(
        self,
        game: Optional[chess.pgn.Game] = None,
        delay_between_moves: bool = False,
    ) -> None:
        """
        Reproduce la partida movimiento a movimiento en la consola.

        Parámetros
        ----------
        game : chess.pgn.Game, opcional
            Si se omite, usa la última partida generada.
        delay_between_moves : bool
            Si True, espera input del usuario entre cada movimiento.
        """
        import time

        g = game or self.game
        if g is None:
            raise ValueError("No hay ninguna partida generada aún.")

        board = g.board()
        print("=" * 40)
        print("   REPRODUCCIÓN DE PARTIDA")
        print("=" * 40)
        print(f"Blancas : {g.headers.get('White', '?')}")
        print(f"Negras  : {g.headers.get('Black', '?')}")
        print(f"Evento  : {g.headers.get('Event', '?')}")
        print(f"Fecha   : {g.headers.get('Date', '?')}")
        print("=" * 40)
        print("\nPosición inicial:")
        print(board)
        print()

        for move_num, move in enumerate(g.mainline_moves(), start=1):
            color = "Blancas" if board.turn == chess.WHITE else "Negras"
            san = board.san(move)
            board.push(move)
            full_move = (move_num + 1) // 2
            print(f"Movimiento {full_move} ({color}): {san}")
            print(board)
            print()
            if delay_between_moves:
                input("Presiona Enter para continuar...")

        print("=" * 40)
        print(f"Resultado: {g.headers.get('Result', '*')}")
        print("=" * 40)

    def get_move_list(self, game: Optional[chess.pgn.Game] = None) -> List[str]:
        """
        Devuelve la lista de movimientos en notación SAN.

        Retorna
        -------
        List[str]
            Lista de movimientos, ej. ["e4", "e5", "Nf3", ...]
        """
        g = game or self.game
        if g is None:
            raise ValueError("No hay ninguna partida generada aún.")
        board = g.board()
        moves = []
        for move in g.mainline_moves():
            moves.append(board.san(move))
            board.push(move)
        return moves


# ─────────────────────────────────────────────────────────────────────────────
# Funciones de conveniencia (API simple)
# ─────────────────────────────────────────────────────────────────────────────

def quick_game(seed: Optional[int] = None, max_moves: int = 200) -> chess.pgn.Game:
    """Genera una partida rápida con una sola llamada."""
    gen = ChessGameGenerator(seed=seed)
    return gen.generate_random_game(max_moves=max_moves)


def quick_pgn(seed: Optional[int] = None, max_moves: int = 200) -> str:
    """Genera una partida y devuelve directamente su PGN como texto."""
    gen = ChessGameGenerator(seed=seed)
    gen.generate_random_game(max_moves=max_moves)
    return gen.to_pgn()


# ─────────────────────────────────────────────────────────────────────────────
# Demostración al ejecutar directamente
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║   CHESS GAME GENERATOR - Demostración   ║")
    print("╚══════════════════════════════════════════╝\n")

    gen = ChessGameGenerator(seed=42)

    # 1. Partida aleatoria completa
    print("▶ Generando partida aleatoria...")
    game = gen.generate_random_game(
        white_name="Magnus Random",
        black_name="Hikaru Chaos",
        event="Torneo de Aleatoriedad 2025",
    )

    # 2. Estadísticas
    stats = gen.get_stats()
    print(f"\n📊 Estadísticas de la partida:")
    print(f"   Resultado     : {stats['result']}")
    print(f"   Terminación   : {stats['termination']}")
    print(f"   Total movs.   : {stats['total_moves']} medios-movimientos")
    print(f"   Blancas       : {stats['white_moves']} movimientos")
    print(f"   Negras        : {stats['black_moves']} movimientos")
    print(f"   Capturas      : {stats['captures']}")
    print(f"   Jaques        : {stats['checks']}")

    # 3. Lista de movimientos (primeros 20)
    moves = gen.get_move_list()
    print(f"\n♟  Primeros 20 movimientos (SAN):")
    for i, m in enumerate(moves[:20], start=1):
        sep = " | " if i % 5 != 0 else "\n"
        print(f"  {i:>3}. {m}", end=sep)
    print()

    # 4. PGN
    print("\n📄 PGN de la partida:")
    print("-" * 50)
    pgn_text = gen.to_pgn()
    # Mostrar solo las primeras 6 líneas del PGN para no saturar la salida
    for line in pgn_text.split("\n")[:6]:
        print(line)
    print("  ... (continúa)")

    # 5. Guardar PGN
    gen.save_pgn("/vercel/sandbox/partida.pgn")

    # 6. Partida desde FEN personalizado
    print("\n▶ Generando partida desde posición FEN (final de partida)...")
    fen_endgame = "8/8/4k3/8/4K3/8/4P3/8 w - - 0 1"
    gen2 = ChessGameGenerator(seed=7)
    game2 = gen2.generate_game_from_fen(fen_endgame, max_moves=60)
    stats2 = gen2.get_stats()
    print(f"   Resultado: {stats2['result']}  |  "
          f"Movimientos: {stats2['total_moves']}  |  "
          f"Terminación: {stats2['termination']}")

    # 7. Lote de 3 partidas
    print("\n▶ Generando lote de 3 partidas...")
    gen3 = ChessGameGenerator(seed=99)
    batch = gen3.generate_batch(count=3, max_moves=150)
    gen3.save_batch_pgn("/vercel/sandbox/lote_partidas.pgn", batch)
    for i, g in enumerate(batch, 1):
        s = gen3.get_stats(g)
        print(f"   Partida {i}: {s['result']:>8}  |  "
              f"{s['total_moves']:>3} movs  |  {s['termination']}")

    # 8. Posición final del tablero
    print("\n📋 Posición final de la partida 1:")
    gen.print_board()

    print("\n✅ Demostración completada.")
    print("   Archivos generados:")
    print("   • /vercel/sandbox/partida.pgn")
    print("   • /vercel/sandbox/lote_partidas.pgn")
