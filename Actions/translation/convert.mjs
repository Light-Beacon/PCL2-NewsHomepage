// Execute the pinned SPXX converter without executing any article scripts.
import { build } from 'esbuild';
import { JSDOM } from 'jsdom';
import fs from 'node:fs/promises';
import path from 'node:path';
const [source, htmlFile, url, output] = process.argv.slice(2);
const entry = path.resolve(source, 'packages/userscript/src/sites/minecraft-net.ts');
const code = await fs.readFile(entry, 'utf8');
const result = await build({stdin:{contents:code+'\nexport { convertMCArticleToMarkdown };',resolveDir:path.dirname(entry),loader:'ts'},bundle:true,write:false,platform:'node',format:'esm',plugins:[{name:'headless-config',setup(b){b.onLoad({filter:/[/\\]config\.ts$/},()=>({contents:'export default {translator:"Hilda-Bot",bugCenter:{}};',loader:'js'}));}}]});
const {convertMCArticleToMarkdown} = await import('data:text/javascript;base64,'+Buffer.from(result.outputFiles[0].text).toString('base64'));
const doc = new JSDOM(await fs.readFile(htmlFile,'utf8'), {url}).window.document;
if (!doc.querySelector('.MC_Layout_Article')) throw new Error('Minecraft.net article layout changed');
const markdown = await convertMCArticleToMarkdown(doc,url,'Hilda-Bot');
if (markdown.trim().length < 200) throw new Error('Empty/truncated article');
await fs.writeFile(output,markdown);
