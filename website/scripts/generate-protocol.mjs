import {compileFromFile} from "json-schema-to-typescript";
import {mkdir, readFile, writeFile} from "node:fs/promises";
import {dirname, resolve} from "node:path";
import {fileURLToPath} from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const schemaPath = resolve(root, "schema/lab-protocol.schema.json");
const outputPath = resolve(root, "src/lab/protocol.generated.ts");
const source = await compileFromFile(schemaPath, {
  bannerComment: "/* Generated from schema/lab-protocol.schema.json. Do not edit. */",
  style: {singleQuote: false, semi: true, tabWidth: 2},
  unreachableDefinitions: true
});
await mkdir(dirname(outputPath), {recursive: true});
const current = await readFile(outputPath, "utf8").catch(() => "");
if (current !== source) await writeFile(outputPath, source);
