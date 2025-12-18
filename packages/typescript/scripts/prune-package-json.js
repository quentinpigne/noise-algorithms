import fs from "fs";

// Read root package.json
const rootPackage = JSON.parse(fs.readFileSync("./package.json", "utf8"));

// Define fields to keep in the published package.json
const prunedPackage = {
  name: rootPackage.name,
  version: rootPackage.version,
  keywords: rootPackage.keywords,
  description: rootPackage.description,
  license: rootPackage.license,
  author: rootPackage.author,
  repository: rootPackage.repository,
  bugs: rootPackage.bugs,
  homepage: rootPackage.homepage,
  type: rootPackage.type,
  main: "index.js", // Path to compiled entry (in dist/)
  types: "index.d.ts", // TypeScript types (if using TS)
};

// Write pruned package.json to dist/
fs.writeFileSync("./dist/package.json", JSON.stringify(prunedPackage, null, 2));
console.log("✅ Pruned package.json copied to dist/");
