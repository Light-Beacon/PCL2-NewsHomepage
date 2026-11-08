import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pipeline as p


class PipelineTests(unittest.TestCase):
    def test_pull_before_preparation(self):
        with patch.object(p.subprocess, 'check_output', return_value=''), patch.object(p.subprocess, 'run') as run:
            p.sync_after_detection()
            self.assertEqual(run.call_args.args[0], ['git', 'pull', '--ff-only', 'https://github.com/Light-Beacon/PCL2-NewsHomepage.git', 'main'])
        with patch.object(p.subprocess, 'check_output', return_value='local.md'), patch.object(p.subprocess, 'run') as run:
            with self.assertRaises(RuntimeError): p.sync_after_detection()
            run.assert_not_called()

    def test_paths(self):
        cases = {'26.3-snapshot-2':'26/26.3/snapshot/26.3-snapshot-2.md',
                 '1.21.11-pre1':'1.21/1.21.11/pre-release/1.21.11-pre1.md',
                 '26.1-rc-1':'26/26.1/release-candidate/26.1-rc-1.md',
                 '1.21.11':'1.21/1.21.11/release/1.21.11.md'}
        for vid, expected in cases.items():
            self.assertEqual(str(p.version_info(vid)[0]),expected)
        with self.assertRaises(ValueError): p.version_info('25w01a')
        with self.assertRaises(ValueError): p.version_info('../evil')

    def test_apply_preserves_metadata_and_detects_concurrency(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve(); lib = root/'Project/libraries/Versions'; lib.mkdir(parents=True)
            target = lib/'26.md'
            old = '---\nversion-image-link: original\nwip: true\ncats: [26]\n---\n'
            target.write_text(old)
            packet = root/'packet.json'
            packet.write_text(json.dumps({'path':str(target.relative_to(root)),'original_sha256':p.digest(old),'official_url':'https://example.com','wiki_url':'https://wiki.example.com','wiki_revision':123}))
            body = '## 新特性\n'+'- 完整中文翻译。\n'*30+'[MC-123](https://example.com)'
            (root/'source.md').write_text('[MC-123](https://example.com)')
            translation = root/'translation.md'; translation.write_text(body)
            with patch.object(p,'ROOT',root),patch.object(p,'LIB',lib):
                p.apply(packet,translation)
                output = target.read_text()
                self.assertIn('version-image-link: original',output)
                self.assertNotIn('wip:',output)
                self.assertEqual(output.count('llm-transalte: true'),1)
                with self.assertRaises(ValueError): p.apply(packet,translation)
                target.write_text(old)
                translation.write_text('中文'*150)
                with self.assertRaisesRegex(ValueError,'bug IDs'): p.apply(packet,translation)
                self.assertEqual(target.read_text(),old)


if __name__ == '__main__': unittest.main()
