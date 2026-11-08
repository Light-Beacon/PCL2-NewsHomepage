import unittest
from pathlib import Path
from unittest.mock import patch
from gh_pr import create_pr


class GhPrTests(unittest.TestCase):
    def test_wrong_account_stops_before_writes(self):
        with patch('gh_pr.subprocess.check_output', return_value='Light-Beacon\n') as command:
            with self.assertRaises(RuntimeError): create_pr('topic', 'title', Path('body.md'))
            self.assertEqual(command.call_count, 1)

    def test_existing_pr_is_reused(self):
        with patch('gh_pr.subprocess.check_output', side_effect=['Hilda-Bot\n', '[{"url":"https://github.com/test/pull/1","headRepositoryOwner":{"login":"Hilda-Bot"}}]']) as command:
            self.assertEqual(create_pr('topic', 'title', Path('body.md')), 'https://github.com/test/pull/1')
            self.assertEqual(command.call_count, 2)

    def test_create_with_explicit_head_and_body_file(self):
        with patch('gh_pr.subprocess.check_output', side_effect=['Hilda-Bot\n', '[]', 'https://github.com/test/pull/2\n']) as command:
            self.assertEqual(create_pr('topic', 'title', Path('body.md')), 'https://github.com/test/pull/2')
            args = command.call_args.args[0]
            self.assertIn('Hilda-Bot:topic', args)
            self.assertIn('--body-file', args)


if __name__ == '__main__': unittest.main()
