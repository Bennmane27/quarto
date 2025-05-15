import unittest
import strategy

class TestStrategy(unittest.TestCase):
    def test_get_all_pieces(self):
        pieces = strategy.get_all_pieces()
        self.assertEqual(len(pieces), 16)  # 2x2x2x2 = 16 pieces
        for p in pieces:
            self.assertEqual(len(p), 4)
            self.assertIn(p[0], 'BS')
            self.assertIn(p[1], 'DL')
            self.assertIn(p[2], 'EF')
            self.assertIn(p[3], 'CP')

    def test_extract_available_pieces(self):
        state = {
            'board': [None]*16,
            'piece': None
        }
        available = strategy.extract_available_pieces(state)
        self.assertEqual(len(available), 16)
        # Place a piece on the board
        state['board'][0] = 'BDEC'
        available = strategy.extract_available_pieces(state)
        self.assertEqual(len(available), 15)
        self.assertNotIn('BDEC', available)

    def test_gen_move_first(self):
        state = {'board': [None]*16, 'piece': None}
        move = strategy.gen_move(state)
        self.assertIsNone(move['pos'])
        self.assertIsInstance(move['piece'], str)
        self.assertEqual(len(move['piece']), 4)

    def test_gen_move_play(self):
        state = {'board': [None]*16, 'piece': 'BDEC'}
        move = strategy.gen_move(state)
        self.assertIn(move['pos'], range(16))
        self.assertIsInstance(move['piece'], str)
        self.assertEqual(len(move['piece']), 4)

    def test_gen_move_no_empty(self):
        state = {'board': ['BDEC']*16, 'piece': 'SDFP'}
        with self.assertRaises(Exception):
            strategy.gen_move(state)

    def test_same_true(self):
        # Toutes les pièces partagent la même couleur
        self.assertTrue(strategy.same(['BDEC', 'SDEC', 'BDFC', 'SDFC']))

    def test_same_false(self):
        # Pièces différentes sans attribut commun
        self.assertFalse(strategy.same(['BDEC', 'SLFP', 'BDFC', 'SLEC']))

    def test_get_lines(self):
        board = [None]*16
        lines = strategy.get_lines(board)
        self.assertEqual(len(lines), 10)
        # Teste la diagonale principale
        diag = [board[i*5] for i in range(4)]
        self.assertIn(diag, lines)

    def test_is_winning(self):
        # Ligne gagnante horizontale
        board = ['BDEC', 'SDEC', 'BDEC', 'SDEC'] + [None]*12
        self.assertTrue(strategy.is_winning(board))
        # Pas de victoire
        board = [None]*16
        self.assertFalse(strategy.is_winning(board))

    def test_valid_piece_regex(self):
        self.assertTrue(strategy.VALID_PIECE.match('BDEC'))
        self.assertFalse(strategy.VALID_PIECE.match('BDEZ'))
        self.assertFalse(strategy.VALID_PIECE.match('1234'))

if __name__ == '__main__':
    unittest.main()
