"use strict";

const byId = (id) => document.getElementById(id);
const data = BATHYS_PROOF;
const editor = byId("type");
const tester = document.querySelector(".tester");
const samples = [
  "SPHINX OF BLACK QUARTZ,\nJUDGE MY VOW.",
  "PACK MY BOX WITH FIVE DOZEN LIQUOR JUGS.",
  "WALTZ, BAD NYMPH, FOR QUICK JIGS VEX.",
  "CORINNE\nBAILEY\nRAE",
  "THE SEA\nAFTER HOURS",
  "THEATRE / FEVER / EVERYWHERE / BATHYS",
  "NEWTON / OUTWIT / AVOW / AWAY",
  "JUPITER / AQUA / LOW TIDE",
  "1969 / 2006 / 6090 / 69 96",
];

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function fitEditor() {
  editor.style.height = "auto";
  editor.style.height = `${Math.max(260, Math.min(850, editor.scrollHeight))}px`;
}

function update() {
  const small = byId("smallcaps").checked;
  const joins = byId("liga").checked;
  tester.style.setProperty("--type-size", `${Number(byId("size").value)}px`);
  tester.style.setProperty("--width", Number(byId("width").value));
  tester.style.setProperty("--tracking", `${Number(byId("tracking").value)}px`);
  tester.style.setProperty(
    "--features",
    [
      `"liga" ${Number(joins)}`,
      `"calt" ${Number(joins)}`,
      `"dlig" ${Number(byId("dlig").checked)}`,
      `"smcp" ${Number(small)}`,
      `"c2sc" ${Number(small)}`,
      '"kern" 1',
    ].join(", "),
  );
  byId("sizeValue").value = `${byId("size").value} px`;
  byId("widthValue").value = byId("width").value;
  byId("trackingValue").value = `${byId("tracking").value} px`;
  fitEditor();
}

for (const id of ["size", "width", "tracking", "liga", "dlig", "smallcaps"]) {
  byId(id).addEventListener("input", update);
}
editor.addEventListener("input", fitEditor);

byId("theme").addEventListener("click", () => {
  const dark = document.body.classList.toggle("dark");
  byId("theme").setAttribute("aria-pressed", String(dark));
});

byId("reset").addEventListener("click", () => {
  byId("size").value = "100";
  byId("width").value = "100";
  byId("tracking").value = "0";
  byId("liga").checked = true;
  byId("dlig").checked = false;
  byId("smallcaps").checked = false;
  update();
});

samples.forEach((sample, index) => {
  const option = node("option", "", sample.replaceAll("\n", " / "));
  option.value = String(index);
  byId("sample").append(option);
});
byId("sample").addEventListener("change", (event) => {
  if (event.target.value === "") return;
  editor.value = samples[Number(event.target.value)];
  fitEditor();
});

function pairs(catalogue, target, optional) {
  for (const word of catalogue) {
    const card = node("div", "pair");
    card.append(
      node("small", "", `${word} / ${optional ? "OPTIONAL" : "STANDARD"}`),
      node("span", "font unjoined", word),
      node("span", optional ? "font joined optional" : "font joined", word),
    );
    byId(target).append(card);
  }
}
pairs(data.standard, "pairs", false);
pairs(data.optional, "optionalPairs", true);

for (const word of data.chains) byId("chains").append(node("span", "", word));
for (const control of data.figures) {
  const row =
    [...data.figures].map((digit) => control + digit).join("") + control;
  byId("numeralRows").append(node("p", "", row));
}
for (const letter of data.alphabet + data.figures + "&?!") {
  const option = node("option", "", letter);
  option.value = letter;
  byId("glyph").append(option);
}
byId("glyph").value = "S";
byId("glyph").addEventListener("change", (event) => {
  byId("glyphView").textContent = event.target.value;
});
byId("glyphSize").addEventListener("input", (event) => {
  byId("glyphView").style.fontSize = `${Number(event.target.value)}px`;
});
byId("version").textContent = data.version;
update();
document.fonts.ready.then(fitEditor);
