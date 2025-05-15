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

if __name__ == '__main__':
    unittest.main()
