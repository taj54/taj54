import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..", "..");

const readmePath = path.join(rootDir, "README.md");
const dataPath = path.join(rootDir, ".github", "scripts", "profile-data.json");
const funfactScriptPath = path.join(rootDir, ".github", "scripts", "update_funfact.py");

const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
let readme = fs.readFileSync(readmePath, "utf8");

function replaceSection(content, startMarker, endMarker, replacement) {
  const startIdx = content.indexOf(startMarker);
  const endIdx = content.indexOf(endMarker);
  if (startIdx === -1 || endIdx === -1 || endIdx < startIdx) {
    throw new Error(`Missing or invalid markers: ${startMarker} / ${endMarker}`);
  }
  const before = content.slice(0, startIdx + startMarker.length);
  const after = content.slice(endIdx);
  return `${before}\n${replacement}\n${after}`;
}

function renderTechStack(groups) {
  if (!Array.isArray(groups) || groups.length < 4) {
    throw new Error("Expected at least 4 techStack groups in profile-data.json");
  }

  const cell = (group) => {
    const badges = group.badges
      .map((b) => `        <img src="${b.src}" alt="${b.alt}" />`)
      .join("\n");
    return `    <td width="50%" valign="top">\n      <h3 align="center">${group.title}</h3>\n      <p align="center">\n${badges}\n      </p>\n    </td>`;
  };

  return [
    "<table>",
    "  <tr>",
    cell(groups[0]),
    cell(groups[1]),
    "  </tr>",
    "  <tr>",
    cell(groups[2]),
    cell(groups[3]),
    "  </tr>",
    "</table>",
  ].join("\n");
}

function renderProjects(projects) {
  const header = [
    "| Project | Description | Focus Areas |",
    "| :--- | :--- | :--- |",
  ];
  const rows = projects.map(
    (p) => `| ${p.name} | ${p.description} | ${p.focus} |`
  );
  return [...header, ...rows].join("\n");
}

function renderReadingList(books) {
  const items = books
    .map((b) => `- **[${b.title}](${b.url})** — *${b.author}*`)
    .join("\n");
  return [
    "<details>",
    "  <summary><b>📚 My Reading List (Click to Expand)</b></summary>",
    "  <br />",
    "",
    items,
    "",
    "</details>",
  ].join("\n");
}

readme = replaceSection(
  readme,
  "<!-- TECH_STACK_START -->",
  "<!-- TECH_STACK_END -->",
  renderTechStack(data.techStack)
);
readme = replaceSection(
  readme,
  "<!-- PROJECTS_START -->",
  "<!-- PROJECTS_END -->",
  renderProjects(data.projects)
);
readme = replaceSection(
  readme,
  "<!-- READING_LIST_START -->",
  "<!-- READING_LIST_END -->",
  renderReadingList(data.readingList)
);

fs.writeFileSync(readmePath, readme, "utf8");
console.log("README.md sections synced from .github/scripts/profile-data.json");

const pythonCmd = process.platform === "win32" ? "python" : "python3";
execFileSync(pythonCmd, [funfactScriptPath], { cwd: rootDir, stdio: "inherit" });

const statsScriptPath = path.join(rootDir, ".github", "scripts", "update_stats.py");
execFileSync(pythonCmd, [statsScriptPath], { cwd: rootDir, stdio: "inherit" });