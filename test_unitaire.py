import unittest
import client
import strategy

class TestClientAndStrategy(unittest.TestCase):
    def test_check_server_false(self):
        # Teste un port qui ne devrait pas être ouvert
        import asyncio
        result = asyncio.run(client.check_server('127.0.0.1', 9999, timeout=1))
        self.assertFalse(result)

    def test_strategy_get_all_pieces(self):
        pieces = strategy.get_all_pieces()
        self.assertEqual(len(pieces), 16)
        for p in pieces:
            self.assertEqual(len(p), 4)

    def test_strategy_gen_move_first(self):
        state = {'board': [None]*16, 'piece': None}
        move = strategy.gen_move(state)
        self.assertIsNone(move['pos'])
        self.assertIsInstance(move['piece'], str)
        self.assertEqual(len(move['piece']), 4)

if __name__ == '__main__':
    unittest.main()
